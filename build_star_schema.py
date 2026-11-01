"""
Build the star schema CSVs from the raw Kaggle file.

Usage:
    python etl/build_star_schema.py --input data/ai_smart_manufacturing_predictive_maintenance.csv --out data/star

Why this script exists: Power BI (and SQL Server) run faster and are easier to
model when the 72 flat columns are split into small dimension tables
(who/where/when/what) and one fact table (the measurements).
"""
import argparse, json, os
import pandas as pd
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="data/ai_smart_manufacturing_predictive_maintenance.csv")
ap.add_argument("--out", default="data/star")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

df = pd.read_csv(args.input, parse_dates=["timestamp", "last_maintenance_date"])
n_raw = len(df)

# ---------- 1. Data-quality gate (fail loudly, don't assume) ----------
assert df.isna().sum().sum() == 0, "unexpected missing values"
assert df.duplicated().sum() == 0, "unexpected duplicate rows"
assert df.monitoring_id.is_unique, "monitoring_id must be unique"

# ---------- 2. Dimensions ----------
MACHINE_COLS = ["machine_id", "factory_id", "production_line", "machine_type", "manufacturer",
                "model", "installation_year", "machine_age", "machine_capacity",
                "machine_power_kw", "machine_weight_kg", "shift_hours",
                "previous_failure_count", "failure_frequency"]
# verify these really are constant per machine (otherwise they don't belong in a dimension)
varies = df.groupby("machine_id")[MACHINE_COLS[1:]].nunique().max()
assert (varies == 1).all(), f"not constant per machine: {list(varies[varies > 1].index)}"

dim_machine = df[MACHINE_COLS].drop_duplicates("machine_id").sort_values("machine_id").reset_index(drop=True)
dim_machine.insert(0, "machine_key", np.arange(1, len(dim_machine) + 1))

# Date table must also cover last_maintenance_date, which goes back before the monitoring window
d_min = min(df.timestamp.min(), df.last_maintenance_date.min()).normalize()
d_max = df.timestamp.max().normalize()
dates = pd.date_range(d_min, d_max, freq="D")
dim_date = pd.DataFrame({"date": dates})
dim_date["date_key"] = dim_date.date.dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date.date.dt.year
dim_date["month_num"] = dim_date.date.dt.month
dim_date["month_name"] = dim_date.date.dt.strftime("%B")
dim_date["day"] = dim_date.date.dt.day
dim_date["weekday_num"] = dim_date.date.dt.dayofweek + 1   # Monday = 1
dim_date["weekday_name"] = dim_date.date.dt.strftime("%A")
dim_date["iso_week"] = dim_date.date.dt.isocalendar().week.astype(int)
dim_date = dim_date[["date_key", "date", "year", "month_num", "month_name", "day",
                     "weekday_num", "weekday_name", "iso_week"]]

dim_time = pd.DataFrame({"time_key": range(24)})
dim_time["hour_label"] = dim_time.time_key.map(lambda h: f"{h:02d}:00")
dim_time["day_part"] = pd.cut(dim_time.time_key, [-1, 5, 11, 17, 23],
                              labels=["Night", "Morning", "Afternoon", "Evening"]).astype(str)

def make_dim(col, key, name):
    d = pd.DataFrame({name: sorted(df[col].unique())})
    d.insert(0, key, np.arange(1, len(d) + 1))
    return d

dim_shift = make_dim("factory_shift", "shift_key", "shift_name")
dim_maint = make_dim("maintenance_type", "maintenance_type_key", "maintenance_type_name")
dim_fail = make_dim("failure_type", "failure_type_key", "failure_type_name")
dim_fail["is_failure"] = (dim_fail.failure_type_name != "No Failure").astype(int)

# ---------- 3. Derived risk level ----------
# Source column maintenance_priority is constant ('Low' in all 100,000 rows), so it cannot
# drive a risk view. This heuristic uses the dataset's own failure_probability (%) and
# machine_health_score (0-100). Thresholds are roughly p75 / p90 / p99 of failure_probability.
fp, hs = df.failure_probability, df.machine_health_score
df["risk_level"] = np.select([(fp >= 5) | (hs < 65), (fp >= 3) | (hs < 68), (fp >= 1.7)],
                             ["Critical", "High", "Medium"], default="Low")
df["risk_rank"] = df.risk_level.map({"Low": 1, "Medium": 2, "High": 3, "Critical": 4})

# ---------- 4. Fact table ----------
fact = df.merge(dim_machine[["machine_id", "machine_key"]], on="machine_id")
fact["date_key"] = fact.timestamp.dt.strftime("%Y%m%d").astype(int)
fact["time_key"] = fact.timestamp.dt.hour
fact = fact.merge(dim_shift, left_on="factory_shift", right_on="shift_name")
fact = fact.merge(dim_maint, left_on="maintenance_type", right_on="maintenance_type_name")
fact = fact.merge(dim_fail, left_on="failure_type", right_on="failure_type_name")
fact["last_maintenance_date_key"] = fact.last_maintenance_date.dt.strftime("%Y%m%d").astype(int)

drop = (MACHINE_COLS + ["factory_shift", "maintenance_type", "failure_type",
        "shift_name", "maintenance_type_name", "failure_type_name", "is_failure",
        "last_maintenance_date", "maintenance_priority"])
fact = fact.drop(columns=drop)
keys = ["monitoring_id", "machine_key", "date_key", "time_key", "shift_key",
        "maintenance_type_key", "failure_type_key", "last_maintenance_date_key", "timestamp"]
fact = fact[keys + [c for c in fact.columns if c not in keys]].sort_values("monitoring_id")

# ---------- 5. Validation: the split must not lose or invent anything ----------
assert len(fact) == n_raw, "row count changed"
for col, dim, dkey in [("machine_key", dim_machine, "machine_key"), ("date_key", dim_date, "date_key"),
                       ("last_maintenance_date_key", dim_date, "date_key"), ("time_key", dim_time, "time_key"),
                       ("shift_key", dim_shift, "shift_key"), ("maintenance_type_key", dim_maint, "maintenance_type_key"),
                       ("failure_type_key", dim_fail, "failure_type_key")]:
    assert fact[col].isin(dim[dkey]).all(), f"orphan keys in {col}"
assert fact.machine_failure.sum() == df.machine_failure.sum()
assert np.isclose(fact.downtime_hours.sum(), df.downtime_hours.sum())

for name, t in {"dim_machine": dim_machine, "dim_date": dim_date, "dim_time": dim_time,
                "dim_shift": dim_shift, "dim_maintenance_type": dim_maint,
                "dim_failure_type": dim_fail, "fact_readings": fact}.items():
    t.to_csv(f"{args.out}/{name}.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    print(f"{name:22s} {len(t):>7,} rows x {t.shape[1]} cols")

kpis = {
    "rows": int(n_raw), "machines": int(len(dim_machine)),
    "failures": int(fact.machine_failure.sum()),
    "failure_rate_pct": round(100 * fact.machine_failure.mean(), 2),
    "avg_health": round(fact.machine_health_score.mean(), 1),
    "total_downtime_h": round(fact.downtime_hours.sum(), 0),
    "total_maintenance_cost": round(fact.maintenance_cost.sum(), 0),
    "risk_counts": fact.risk_level.value_counts().to_dict(),
}
json.dump(kpis, open(f"{args.out}/kpis.json", "w"), indent=2)
print(json.dumps(kpis, indent=2))
