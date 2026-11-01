# Power BI build guide (step by step, with the "why")

Goal: turn `data/star/*.csv` (or the SQL Server tables) into the 4-page report designed in `docs/Project_Documentation.pdf`.
Menu names can differ slightly between Power BI Desktop versions - if something is not where it says, search the ribbon.

## Step 1 - Load the tables
1. **Home > Get data > Text/CSV** (or **SQL Server** if you loaded the warehouse). Load all 7 tables: `fact_readings`, `dim_machine`, `dim_date`, `dim_time`, `dim_shift`, `dim_maintenance_type`, `dim_failure_type`.
2. In Power Query check types: `date` = Date, `timestamp` = Date/Time, keys = Whole number, `machine_failure` = Whole number (0/1).

*Why:* wrong data types are the most common reason a measure returns blank or a date axis looks wrong.

## Step 2 - Model view: relationships
Create one-to-many relationships (dimension side = 1, fact side = many), single direction:

| From (1) | To (many) | Active? |
|---|---|---|
| dim_machine[machine_key] | fact_readings[machine_key] | yes |
| dim_date[date_key] | fact_readings[date_key] | yes |
| dim_date[date_key] | fact_readings[last_maintenance_date_key] | **no** (inactive) |
| dim_time[time_key] | fact_readings[time_key] | yes |
| dim_shift[shift_key] | fact_readings[shift_key] | yes |
| dim_maintenance_type[maintenance_type_key] | fact_readings[maintenance_type_key] | yes |
| dim_failure_type[failure_type_key] | fact_readings[failure_type_key] | yes |

*Why:* Power BI allows only one active path between two tables. `dim_date` is used twice (monitoring date and last maintenance date), so the second one stays inactive and you activate it inside a measure with `USERELATIONSHIP` when you need it.

## Step 3 - Date table and sorting
1. Select `dim_date` > **Table tools > Mark as date table** > choose `date`.
2. Select `month_name` > **Column tools > Sort by column** > `month_num`. Do the same for `weekday_name` > `weekday_num`, and `hour_label` is already ordered by `time_key`.

*Why:* without this, months sort alphabetically (April, August, ...).

## Step 4 - Measures
1. **Home > Enter data**, create an empty table named `_Measures`, load it.
2. Paste each measure from `powerbi/measures.dax` (one at a time: **New measure**). Format `Failure Rate %` and `Critical Readings %` as percentage; `Avg Failure Probability %` is already in percent units (the source stores 0-14.5), so format it as a decimal with a "%" suffix, not as Percentage.
3. Check one number: `Failure Events` with no filters must equal **1,472**; `Total Readings` = **100,000**. If not, a relationship or type is wrong.

*Why:* checking against a number you already know from the ETL is how you catch silent errors before building visuals.

## Step 5 - Theme
**View > Themes > Browse for themes** > `powerbi/theme.json`.

## Step 6 - Pages (follow the wireframes in the documentation)
- **Page 1 Overview:** 5 cards (Total Readings, Failure Events, Failure Rate %, Avg Health Score, Total Downtime). Donut or sorted bar: `dim_failure_type[failure_type_name]` by Failure Events - add a **visual filter** `is_failure = 1` so "No Failure" does not swamp the chart. Bar: Failure Rate % by `dim_machine[factory_id]` with a constant line at overall rate. Line: Failure Events by `dim_date[date]`. Matrix: factory x machine type, Failure Rate %, conditional formatting.
- **Page 2 Health & Risk:** cards + Gauge (Avg Health Score, range 0-100) + stacked bar of readings by `risk_level` per factory (sort `risk_level` by `risk_rank`: select column > Sort by column) + table of machines.
- **Page 3 Maintenance & Cost:** Total Maintenance Cost by `maintenance_type_name`; Total Downtime by `machine_type`; monthly cost/downtime line.
- **Page 4 Sensors:** scatter `temperature_c` vs `vibration_mm_s` (details = machine type, sample is fine), anomaly scores by machine type.

## Step 7 - Interactions
- **View > Sync slicers**: sync Factory, Machine type, Date and Shift across all pages.
- Create a hidden **drill-through** page "Machine detail" with field `dim_machine[machine_id]`.

## Step 8 - Be honest in the report
Add a small text box on pages 1-2: *"Risk level is a heuristic from the dataset's own scores; it does not predict actual failures in this data (see documentation section 6)."* This matches the findings and protects your credibility in the evaluation.

## Step 9 - Screenshots for the presentation
Export each page (**File > Export > PDF**, or screenshot) and replace the wireframe slide in `presentation/`.
