import pandas as pd, numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from scipy import stats

NAVY="#1F3A5F"; BLUE="#3C7DD9"; AMB="#F2A33A"; RED="#D64545"; GRN="#2E9E83"; GREY="#B8C4D3"; BG="#EAF0F7"
plt.rcParams["font.family"]="DejaVu Sans"
OUT="docs/images/"
raw=pd.read_csv("data/ai_smart_manufacturing_predictive_maintenance.csv")
fact=pd.read_csv("data/star/fact_readings.csv"); mach=pd.read_csv("data/star/dim_machine.csv")
f=fact.merge(mach[["machine_key","factory_id","machine_type"]],on="machine_key")
res={}

# ---- findings charts ----
ft=raw[raw.machine_failure==1].failure_type.value_counts().sort_values()
fig,ax=plt.subplots(figsize=(6,3.2)); ax.barh(ft.index,ft.values,color=NAVY)
for i,v in enumerate(ft.values): ax.text(v+3,i,str(v),va="center",fontsize=9)
ax.set_title("Failure events by type (n = 1,472)",loc="left",color=NAVY,fontsize=11); ax.spines[["top","right"]].set_visible(False)
plt.tight_layout(); plt.savefig(OUT+"fig_failure_types.png",dpi=200); plt.close()
res["by_type"]=ft.to_dict()

g=f.groupby("factory_id").machine_failure.agg(["sum","size"]); g["rate"]=100*g["sum"]/g["size"]
p=g["sum"].sum()/g["size"].sum(); se=100*np.sqrt(p*(1-p)/g["size"])
chi=stats.chi2_contingency(np.array([g["sum"],g["size"]-g["sum"]]))
res["factory_rate"]=g.rate.round(2).to_dict(); res["chi2_p"]=float(chi[1])
fig,ax=plt.subplots(figsize=(6,3.2)); ax.bar(g.index.str[-2:],g.rate,yerr=1.96*se,color=BLUE,capsize=3)
ax.axhline(100*p,color=RED,ls="--",lw=1); ax.set_ylabel("Failure rate %"); ax.set_xlabel("Factory (FAC-xx)")
ax.set_title("Failure rate by factory (bars = 95% interval)",loc="left",color=NAVY,fontsize=11); ax.spines[["top","right"]].set_visible(False)
plt.tight_layout(); plt.savefig(OUT+"fig_factory_rate.png",dpi=200); plt.close()

r=f.groupby("risk_level").machine_failure.agg(["mean","size"]).reindex(["Low","Medium","High","Critical"])
res["risk_vs_failure"]={k:{"rate_pct":round(100*v["mean"],2),"readings":int(v["size"])} for k,v in r.iterrows()}
fig,ax=plt.subplots(figsize=(6,3.2)); ax.bar(r.index,100*r["mean"],color=[GRN,AMB,"#E07B39",RED])
ax.axhline(1.47,color=NAVY,ls="--",lw=1); ax.text(-0.4,2.0,"dashed line = overall failure rate 1.47%",ha="left",fontsize=8,color=NAVY)
for i,(k,v) in enumerate(r.iterrows()): ax.text(i,100*v["mean"]+0.03,f"{100*v['mean']:.2f}%",ha="center",fontsize=9)
ax.set_ylim(0,2.2); ax.set_ylabel("Actual failure rate %")
ax.set_title("Does the risk tier separate real failures?",loc="left",color=NAVY,fontsize=11); ax.spines[["top","right"]].set_visible(False)
plt.tight_layout(); plt.savefig(OUT+"fig_risk_validation.png",dpi=200); plt.close()
json.dump(res,open("docs/findings.json","w"),indent=2); print(json.dumps(res,indent=2))

# ---- ER diagram ----
def box(ax,x,y,w,title,rows,color):
    h=0.32+0.24*len(rows)
    ax.add_patch(Rectangle((x,y-h),w,h,fc="white",ec=color,lw=1.5))
    ax.add_patch(Rectangle((x,y-0.32),w,0.32,fc=color,ec=color))
    ax.text(x+w/2,y-0.16,title,ha="center",va="center",color="white",fontsize=9,fontweight="bold")
    for i,t in enumerate(rows): ax.text(x+0.08,y-0.32-0.12-0.24*i,t,va="center",fontsize=7.2)
    return (x,y,w,h)
fig,ax=plt.subplots(figsize=(11,7.2)); ax.set_xlim(0,11); ax.set_ylim(0,7.4); ax.axis("off")
F=box(ax,4.1,6.0,2.8,"fact_readings",["PK monitoring_id","FK machine_key","FK date_key","FK time_key","FK shift_key","FK maintenance_type_key","FK failure_type_key","FK last_maintenance_date_key","timestamp","~50 measures (sensors, health,","  maintenance, scores)","machine_failure, risk_level"],NAVY)
M=box(ax,0.2,6.4,2.9,"dim_machine",["PK machine_key","machine_id (business key)","factory_id, production_line","machine_type, manufacturer, model","installation_year, machine_age","capacity, power_kw, weight_kg","previous_failure_count, ..."],BLUE)
D=box(ax,7.9,6.9,2.9,"dim_date",["PK date_key (yyyymmdd)","date, year, month_num/name","day, weekday_num/name","iso_week"],BLUE)
T=box(ax,7.9,4.7,2.9,"dim_time",["PK time_key (hour 0-23)","hour_label, day_part"],BLUE)
S=box(ax,0.2,3.6,2.9,"dim_shift",["PK shift_key","shift_name"],BLUE)
MT=box(ax,0.2,2.2,2.9,"dim_maintenance_type",["PK maintenance_type_key","maintenance_type_name"],BLUE)
FT=box(ax,7.9,3.0,2.9,"dim_failure_type",["PK failure_type_key","failure_type_name","is_failure"],BLUE)
for (x1,y1),(x2,y2) in [((3.1,5.2),(4.1,5.2)),((7.9,6.2),(6.9,6.2)),((7.9,4.3),(6.9,4.7)),((3.1,3.1),(4.1,3.9)),((3.1,1.8),(4.1,3.5)),((7.9,2.4),(6.9,3.4))]:
    ax.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle="-|>",color="#555",lw=1))
ax.text(5.5,0.5,"Arrows point from dimension (1) to fact (many). dim_date is also used for last_maintenance_date_key (role-playing).",ha="center",fontsize=8,color="#555")
ax.set_title("Star schema: Smart Manufacturing Data Warehouse",loc="left",color=NAVY,fontsize=13,fontweight="bold")
plt.savefig(OUT+"er_diagram.png",dpi=200,bbox_inches="tight"); plt.close()

# ---- Wireframes ----
def wf(name,title,blocks):
    fig,ax=plt.subplots(figsize=(10,5.6)); ax.set_xlim(0,100); ax.set_ylim(0,56); ax.axis("off")
    ax.add_patch(Rectangle((0,0),100,56,fc="#F6F8FB",ec="#999"))
    ax.add_patch(Rectangle((0,50),100,6,fc=NAVY,ec=NAVY)); ax.text(2,53,title,color="white",va="center",fontsize=11,fontweight="bold")
    ax.text(98,53,"WIREFRAME - replace with final Power BI screenshot",color="#cfd8e6",va="center",ha="right",fontsize=7)
    ax.add_patch(Rectangle((0,0),11,50,fc="#E3E9F1",ec="#bbb")); 
    for i,t in enumerate(["Overview","Machine Health","Maintenance","Sensors"]): ax.text(1,45-i*5,t,fontsize=7,fontweight="bold" if t in title else "normal")
    ax.text(1,18,"Slicers:",fontsize=7,fontweight="bold")
    for i,t in enumerate(["Factory","Machine type","Date range","Shift"]): ax.text(1,14-i*3.2,"[ "+t+" v ]",fontsize=6.5)
    for (x,y,w,h,label,kind) in blocks:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.2",fc="white",ec=GREY))
        ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=7.5,color=NAVY)
    plt.savefig(OUT+name,dpi=200,bbox_inches="tight"); plt.close()
card=lambda x,l:(x,40,13,7,l,"card")
wf("wf_1_overview.png","Page 1 - Executive Overview",[card(13,"Readings"),card(28,"Failure events"),card(43,"Failure rate %"),card(58,"Avg health score"),card(73,"Total downtime (h)"),
  (13,20,27,18,"Donut: failure events by type","d"),(42,20,27,18,"Bar: failure rate by factory","b"),(71,20,27,18,"Line: failures per day","l"),(13,2,85,16,"Matrix: factory x machine type -> failure rate (conditional colour)","m")])
wf("wf_2_health.png","Page 2 - Machine Health & Risk",[card(13,"Avg health"),card(28,"Critical readings %"),card(43,"Machines w/ critical"),card(58,"Avg failure prob %"),card(73,"Avg RUL (h)"),
  (13,20,27,18,"Gauge: avg health (0-100)","g"),(42,20,27,18,"Stacked bar: risk level by factory","b"),(71,20,27,18,"Histogram: failure probability","h"),(13,2,85,16,"Table: top 20 machines by avg failure probability (drill-through to machine page)","t")])
wf("wf_3_maintenance.png","Page 3 - Maintenance & Cost",[card(13,"Maintenance cost"),card(28,"Cost / failure"),card(43,"Avg repair (h)"),card(58,"Downtime (h)"),card(73,"Avg days since maint."),
  (13,20,41,18,"Column: cost by maintenance type","c"),(56,20,42,18,"Bar: downtime by machine type","b"),(13,2,85,16,"Line: monthly cost & downtime","l")])
wf("wf_4_sensors.png","Page 4 - Sensors & Anomalies",[card(13,"Avg temp C"),card(28,"Avg vibration"),card(43,"Avg anomaly (temp)"),card(58,"Avg anomaly (vib)"),card(73,"Avg load %"),
  (13,20,41,18,"Scatter: temperature vs vibration (by machine type)","s"),(56,20,42,18,"Bar: avg anomaly scores by machine type","b"),(13,2,85,16,"Line: hourly average of selected sensor (field parameter)","l")])

# ---- Gantt ----
tasks=[("Understand data & requirements",1,1),("Data profiling & cleaning checks",1,2),("Star schema design",2,3),("ETL + SQL build & load",3,4),("Power BI model + DAX",4,5),("Dashboard design & build (4 pages)",5,7),("Testing & validation",7,8),("Documentation",6,9),("Presentation + video",9,10),("Final review & submission",10,10)]
fig,ax=plt.subplots(figsize=(8,3.8))
for i,(t,s,e) in enumerate(tasks): ax.barh(len(tasks)-i,e-s+1,left=s-1,color=NAVY if i%2==0 else BLUE)
ax.set_yticks(range(1,len(tasks)+1)); ax.set_yticklabels([t[0] for t in reversed(tasks)],fontsize=8)
ax.set_xticks(range(0,10)); ax.set_xticklabels([f"W{i}" for i in range(1,11)],fontsize=8); ax.grid(axis="x",alpha=.3)
ax.set_title("Indicative plan (relative weeks - adjust to your DEPI deadline)",loc="left",color=NAVY,fontsize=10); ax.spines[["top","right"]].set_visible(False)
plt.tight_layout(); plt.savefig(OUT+"gantt.png",dpi=200); plt.close()

# ---- Power/Interest grid ----
st=[("Plant Manager",9,8),("Maintenance Manager",8,9.3),("Reliability Engineer",5,9),("Production Planner",6,7),("Finance / Cost Controller",7,4.5),("EHS / Quality",4.5,5.5),("IT / BI Team",5,3.5),("Executives",9.3,4)]
fig,ax=plt.subplots(figsize=(6,4.6)); ax.set_xlim(0,10.5); ax.set_ylim(0,10.5)
ax.axhline(5,color=GREY); ax.axvline(5,color=GREY)
for t,x,y in [("Keep satisfied",0.3,9.9),("Manage closely",5.3,9.9),("Monitor",0.3,0.4),("Keep informed",5.3,0.4)]: ax.text(x,y,t,fontsize=8,color="#777",fontweight="bold")
for n,x,y in st: ax.scatter(y,x,s=60,color=NAVY); ax.text(y+0.15,x+0.15,n,fontsize=7.5)
ax.set_xlabel("Interest in the dashboard"); ax.set_ylabel("Influence / power"); ax.set_title("Stakeholder map (assumed)",loc="left",color=NAVY,fontsize=11)
ax.spines[["top","right"]].set_visible(False); plt.tight_layout(); plt.savefig(OUT+"stakeholder_grid.png",dpi=200); plt.close()
