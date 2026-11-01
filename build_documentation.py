import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
                                PageBreak, ListFlowable, ListItem, KeepTogether)
NAVY=colors.HexColor("#1F3A5F"); LIGHT=colors.HexColor("#EAF0F7"); GRID=colors.HexColor("#B8C4D3")
fx=json.load(open("docs/findings.json")); kp=json.load(open("data/star/kpis.json"))
T=ParagraphStyle("T",fontName="Helvetica-Bold",fontSize=24,leading=29,textColor=NAVY,spaceAfter=8)
H1=ParagraphStyle("H1",fontName="Helvetica-Bold",fontSize=16,leading=20,textColor=NAVY,spaceBefore=4,spaceAfter=8)
H2=ParagraphStyle("H2",keepWithNext=1,fontName="Helvetica-Bold",fontSize=11.5,leading=15,textColor=NAVY,spaceBefore=9,spaceAfter=4)
B=ParagraphStyle("B",fontName="Helvetica",fontSize=9.6,leading=13.6,spaceAfter=4)
S=ParagraphStyle("S",parent=B,fontSize=8.5,leading=11.5,textColor=colors.HexColor("#555555"))
C=ParagraphStyle("C",parent=B,fontSize=8.3,leading=10.8,spaceAfter=0)
CH=ParagraphStyle("CH",parent=C,fontName="Helvetica-Bold",textColor=colors.white)
W=A4[0]-4*cm
def P(t,s=B): return Paragraph(t,s)
def bl(items): return ListFlowable([ListItem(P(i),leftIndent=12) for i in items],bulletType="bullet",start="-",leftIndent=12)
def tbl(rows,widths):
    d=[[P(c,CH if i==0 else C) for c in r] for i,r in enumerate(rows)]
    t=Table(d,colWidths=[w*cm for w in widths],repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
        ("GRID",(0,0),(-1,-1),.5,GRID),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    return t
def img(p,w=W):
    from PIL import Image as PI
    iw,ih=PI.open(p).size; return Image(p,width=w,height=w*ih/iw)
I="docs/images/"
s=[]
# ---- cover ----
s+= [Spacer(1,4*cm),P("Smart Manufacturing &amp; Predictive Maintenance",T),
     P("Power BI Dashboard on a SQL Server Star Schema",ParagraphStyle("x",parent=B,fontSize=13,textColor=NAVY)),Spacer(1,.5*cm),
     P("Graduation Project Documentation - Digital Egypt Pioneers Initiative (DEPI)",B),
     P("Data source: Kaggle - Smart Manufacturing &amp; Predictive Maintenance Dataset (100,000 rows x 72 columns, 5,000 machines)",S),
     P("Author: Eman Sayed Seddik",S),Spacer(1,1*cm),
     tbl([["Section","Content"],["1","Project overview and objectives"],["2","Project planning"],["3","Stakeholder analysis"],
          ["4","Database design"],["5","UI/UX design"],["6","Data findings and limitations"],["7","How to reproduce"]],[2,14.5]),
     Spacer(1,1*cm),P("<b>Reading note:</b> the stakeholders in section 3 are assumed roles for a realistic factory scenario - the dataset is synthetic, so there is no real client. The wireframes in section 5 are design mock-ups and should be replaced or complemented by screenshots of the finished Power BI report.",S),PageBreak()]
# ---- 1 ----
s+=[P("1. Project overview and objectives",H1),
 P("Factories collect thousands of sensor readings but often use them only after a machine has stopped. This project builds a monitoring dashboard on top of a clean SQL star schema so that maintenance and plant teams can see, in one place, how often machines fail, which failure types occur, how healthy the fleet is, and what maintenance and downtime cost."),
 P("Problem statement",H2),P("Plant and maintenance managers need one trusted view of machine health, failures, downtime and maintenance effort across 10 factories, instead of reading a 72-column flat file."),
 P("Objectives",H2),bl(["Design and load a dimensional (star) data model from the flat Kaggle file with no loss of rows or totals.",
  "Deliver a 4-page Power BI report: Executive Overview, Machine Health &amp; Risk, Maintenance &amp; Cost, Sensors &amp; Anomalies.",
  "Define a transparent risk tier, because the source column <font name='Courier'>maintenance_priority</font> is constant.",
  "Document honestly what the data can and cannot support (section 6)."]),
 P("Scope",H2),tbl([["In scope","Out of scope"],["Data profiling, star schema, ETL (Python), SQL Server DDL/load, DAX measures, 4-page report, documentation, presentation, demo video","Real-time streaming, a production deployment, and a validated failure-prediction model (see section 6 for why)"]],[8.25,8.25]),
 P("Key figures (from the data)",H2),
 tbl([["Metric","Value"],["Monitoring records",f"{kp['rows']:,}"],["Machines",f"{kp['machines']:,} (20 readings each)"],["Time window","2026-01-01 to 2026-03-07 (hourly timestamps)"],
      ["Failure events (machine_failure = 1)",f"{kp['failures']:,} ({kp['failure_rate_pct']}% of readings)"],["Average machine health score",f"{kp['avg_health']} / 100"],["Total downtime hours",f"{kp['total_downtime_h']:,.0f}"]],[8,8.5]),PageBreak()]
# ---- 2 ----
s+=[P("2. Project planning",H1),
 P("Methodology: a lightweight, phased waterfall with a review at the end of each phase - suitable for a single-person analytics project with a fixed deadline. Weeks below are relative; shift them to match your DEPI dates."),
 img(I+"gantt.png",W*.92),
 P("Work breakdown and deliverables",H2),
 tbl([["Phase","Main tasks","Deliverable"],["Understand","Read dataset guide, list business questions, confirm scope","Scope &amp; KPI list"],
  ["Profile data","Check missing values, duplicates, constants per machine, label balance","Profiling notes (section 6)"],
  ["Design","Dimensional model, keys, risk rule, naming","ER diagram, data dictionary"],
  ["Build data layer","Python ETL, SQL Server DDL, bulk load, row-count checks","etl/, sql/ folders"],
  ["Build report","Model relationships, DAX measures, 4 pages, theme","Dashboard (.pbix)"],
  ["Validate","Reconcile totals SQL vs Power BI, test slicers, test the risk tier against real failures","Test log"],
  ["Communicate","Documentation, presentation PDF, demo video","Docs, PDF, video"]],[2.6,9.2,4.7]),
 P("Tools",H2),P("Python (pandas) for ETL; SQL Server (T-SQL) for the warehouse; Power BI Desktop + DAX for the report; Git/GitHub for version control; matplotlib/reportlab for the diagrams and documents."),
 P("Risks and mitigation",H2),
 tbl([["Risk","Impact","Mitigation"],
  ["Source column maintenance_priority is constant ('Low')","The README's 'critical machines' view is impossible","Derived risk_level with documented thresholds; validated against real failures"],
  ["Only 1.47% of readings are failures","Any future classifier would be hard to train and easy to over-state","Report rates and counts, avoid accuracy claims; document the imbalance"],
  ["Sensors do not predict the failure label in this data (section 6)","Cannot promise 'predictive' value","Position the dashboard as monitoring/descriptive; state the limitation openly"],
  ["Meaning of some fields is undocumented (e.g. maintenance_cost per event or cumulative)","Totals could be misread","Label measures clearly, treat as per-record amounts, flag as an assumption"],
  ["SQL scripts not run on the author's side","Possible syntax/path errors on first run","Run in a test DB; checks in 03_checks_and_views.sql"]],[5.5,4.5,6.5]),PageBreak()]
# ---- 3 ----
s+=[P("3. Stakeholder analysis",H1),
 P("Because the dataset is synthetic, the stakeholders below are <b>assumed roles</b> that would exist in a real factory group. They drive the choice of KPIs and dashboard pages."),
 tbl([["Stakeholder","Main interest","Key questions","Page","Influence","Interest"],
  ["Plant Manager","Output, downtime, cost","Which factory loses most hours? Is it getting better?","1, 3","High","High"],
  ["Maintenance Manager","Maintenance workload and effectiveness","Which machines need attention? What does each maintenance type cost?","2, 3","High","Very high"],
  ["Reliability Engineer","Root causes of failure","Which failure types dominate? Any sensor pattern?","1, 4","Medium","Very high"],
  ["Production Planner","Capacity and scheduling","Which lines/machine types have most downtime?","1, 3","Medium","High"],
  ["Finance / Cost Controller","Maintenance spend","Total and per-type maintenance cost; cost per failure","3","Medium","Medium"],
  ["EHS / Quality","Safe, stable operation","Where are anomaly scores high?","4","Medium","Medium"],
  ["IT / BI Team","Maintainable data pipeline","Is the model documented and refreshable?","(docs)","Low","Medium"],
  ["Executives","Portfolio view","One-page status across 10 factories","1","Very high","Medium"]],[3,3,4.7,1.2,2.2,2.4]),
 Spacer(1,6),img(I+"stakeholder_grid.png",W*.62),
 P("Engagement approach: Plant Manager and Maintenance Manager are managed closely (review each page draft); Executives are kept satisfied with page 1; Engineers and Planners are kept informed and invited to give feedback on filters and drill-through.",S),
 P("Functional requirements (derived)",H2),
 bl(["Filter every page by factory, machine type, date range and shift.","Show failure count, failure rate, health score, downtime and maintenance cost as KPI cards.",
     "Show failure events by type and failure rate by factory.","Provide a drill-through from a risk table to a single machine.","Refresh from SQL Server without manual editing."]),
 P("Non-functional requirements",H2),
 bl(["Page load under a few seconds with 100,000 fact rows (star schema, no unused columns in visuals).","Colour is never the only carrier of meaning (labels/icons accompany risk colours).","All measures documented in powerbi/measures.dax."]),PageBreak()]
# ---- 4 ----
s+=[P("4. Database design",H1),
 P("Source profile",H2),P("One flat file: 100,000 rows x 72 columns, 0 missing values, 0 duplicate rows, <font name='Courier'>monitoring_id</font> unique. 14 columns are constant per machine (factory, line, type, manufacturer, model, installation year, age, capacity, power, weight, shift hours, previous failure count, failure frequency, maintenance priority) - these belong in a machine dimension, which the ETL verifies programmatically before building it."),
 P("Model: star schema (grain = one monitoring reading of one machine)",H2),
 img(I+"er_diagram.png",W),
 P("Table dictionary",H2),
 tbl([["Table","Rows","Key","Purpose"],
  ["fact_readings","100,000","monitoring_id (PK); FKs to all dimensions","All sensor, health, maintenance and target measures + derived risk_level"],
  ["dim_machine","5,000","machine_key (surrogate); machine_id (business key)","Static machine attributes (factory, line, type, manufacturer, model, size, age)"],
  ["dim_date","185","date_key (yyyymmdd)","Calendar; also covers last_maintenance_date, which starts in 2025-09 (role-playing date)"],
  ["dim_time","24","time_key (hour)","Hour of day and day part"],
  ["dim_shift","3","shift_key","Morning / Evening / Night"],
  ["dim_maintenance_type","5","maintenance_type_key","Corrective, Emergency, Predictive, Preventive, Routine"],
  ["dim_failure_type","7","failure_type_key","6 failure types + 'No Failure'; is_failure flag"]],[3.4,1.5,4.9,6.7]),
 P("Design decisions (and why)",H2),
 bl(["<b>Surrogate keys</b> (machine_key) keep joins small and independent of the source ID format.",
     "<b>Low-cardinality text columns</b> (shift, maintenance type, failure type) moved to dimensions so slicers and labels come from one place.",
     "<b>Measures stay in the fact</b>: they vary per reading, so splitting them would add joins without benefit.",
     "<b>Derived risk_level</b> is stored in the fact (computed in the ETL) so SQL and Power BI show the same numbers. Rule: Critical if failure_probability &gt;= 5 or health &lt; 65; High if &gt;= 3 or health &lt; 68; Medium if &gt;= 1.7; else Low. Thresholds are roughly the 75th/90th/99th percentiles of failure_probability - a heuristic, not a validated model.",
     "<b>maintenance_priority</b> (constant 'Low') is dropped from the fact because it carries no information."]),
 P("Quality checks built into the ETL",H2),
 bl(["Row count after the split equals the raw row count (100,000).","Every foreign key exists in its dimension (no orphans).","Total failures (1,472) and total downtime hours are identical before and after the split.","Per-machine attributes verified constant before they are placed in dim_machine."]),
 P("Implementation files: etl/build_star_schema.py (builds the 7 CSVs), sql/01_create_schema.sql (T-SQL DDL with PK/FK), sql/02_load_data.sql (BULK INSERT), sql/03_checks_and_views.sql (checks + 2 views). The SQL scripts were written for SQL Server and have not been executed by the author - run them first in a test database.",S),PageBreak()]
# ---- 5 ----
s+=[P("5. UI/UX design",H1),
 P("Design goals",H2),bl(["Answer the stakeholders' first question within 5 seconds on each page (KPI cards on top).","Same layout skeleton on all pages: left navigation + slicer panel, KPI row, two or three charts, one detail visual.","Consistent filters: a sync-slicer group so a factory choice follows the user across pages."]),
 P("Visual identity",H2),
 tbl([["Element","Choice"],["Primary colour","Navy #1F3A5F (titles, main series)"],["Accent","Blue #3C7DD9; amber #F2A33A (attention); red #D64545 (critical); green #2E9E83 (healthy)"],
      ["Typography","Segoe UI; KPI numbers 28 pt semibold, labels 10 pt"],["Theme file","powerbi/theme.json (import via View > Themes > Browse for themes)"]],[4,12.5]),
 P("Chart choices",H2),
 tbl([["Question","Visual","Reason"],["How many / how often?","KPI cards","Single number, fast reading"],["Which failure types dominate?","Donut or sorted bar","6 categories; sorted bar is easier to compare"],["Which factory is worse?","Bar with a reference line","Compare against the overall 1.47% rate"],["How is health distributed?","Gauge + histogram","Gauge for the average, histogram for the spread"],["Where is the cost?","Column by maintenance type","Categorical comparison"],["Do sensors move together?","Scatter","Relationship between two numeric fields"]],[5,4.5,7]),
 P("Interaction",H2),bl(["Slicers: factory, machine type, date range, shift (synced across pages).","Cross-filtering between visuals on a page; drill-through from the risk table to a machine detail page.","Tooltips show counts and the formula meaning (e.g. failure rate = failures / readings)."]),
 P("Accessibility",H2),bl(["Contrast of text on white at least 4.5:1 (navy on white).","Risk levels use labels and ordering as well as colour.","Alt text on every visual; logical tab order."]),
 P("Wireframes",H2),P("Mock-ups made before building; replace with the final screenshots in the presentation.",S)]
for n,t in [("wf_1_overview.png","Page 1 - Executive Overview"),("wf_2_health.png","Page 2 - Machine Health &amp; Risk"),("wf_3_maintenance.png","Page 3 - Maintenance &amp; Cost"),("wf_4_sensors.png","Page 4 - Sensors &amp; Anomalies")]:
    s.append(KeepTogether([P(t,H2),img(I+n,W*.9)]))
s.append(PageBreak())
# ---- 6 ----
rv=fx["risk_vs_failure"]
s+=[P("6. Data findings and limitations",H1),
 P("These findings come from profiling the file itself. They matter because they change what the dashboard may claim.",B),
 P("6.1 The dataset guide does not fully match the data",H2),
 tbl([["Guide says","Actual data"],["maintenance_priority table with 'Critical' machines","Constant: 'Low' in all 100,000 rows"],["8 failure types","6 failure types + 'No Failure' = 7 values"],["Dataset is ready to use (0 missing, 0 duplicates)","Confirmed: 0 missing, 0 duplicate rows"]],[8.25,8.25]),
 P("6.2 Failure events",H2),
 img(I+"fig_failure_types.png",W*.62),
 P(f"Failures are rare ({kp['failure_rate_pct']}% of readings) and spread almost evenly across the six types (222 to 265 events each)."),
 P("6.3 Factory differences are small",H2),
 img(I+"fig_factory_rate.png",W*.62),
 P(f"Factory failure rates range from 1.36% to 1.71%. A chi-square test of 'failure rate is the same in all 10 factories' gives p = {fx['chi2_p']:.2f}, so the differences are consistent with chance. The dashboard should not rank factories by failure rate as if the gaps were meaningful."),
 P("6.4 The risk tier and probability scores do not separate real failures",H2),
 img(I+"fig_risk_validation.png",W*.62),
 P(f"Actual failure rate by derived risk level: Low {rv['Low']['rate_pct']}%, Medium {rv['Medium']['rate_pct']}%, High {rv['High']['rate_pct']}%, Critical {rv['Critical']['rate_pct']}% - all close to the overall 1.47%. In addition, no numeric column has a correlation above about 0.007 (absolute) with machine_failure, and a gradient-boosting model cross-validated by machine gave an AUC of 0.505 (0.5 = random guessing)."),
 P("<b>What this means for the project:</b> the dashboard is a <b>monitoring and reporting</b> tool. The failure_probability, machine_health_score and remaining_useful_life fields are shown as provided by the dataset, but this project does not claim they predict real failures. A genuine predictive-maintenance model would need data where the failure label is linked to the sensor history."),
 P("6.5 Other caveats",H2),bl(["The dataset is synthetic; conclusions apply to the data, not to a real plant.","The unit/currency and exact meaning of maintenance_cost, and whether some fields are cumulative, are not documented - totals are treated as per-record amounts (assumption).","The 20 readings per machine are not evenly spaced in time and cover only about 9 weeks, so long-term trends cannot be judged."]),PageBreak()]
# ---- 7 ----
s+=[P("7. How to reproduce",H1),
 tbl([["Step","Command / action"],
  ["1. Get the data","Download the CSV from Kaggle (Smart Manufacturing &amp; Predictive Maintenance) and place it in data/"],
  ["2. Build the star schema","python etl/build_star_schema.py  (creates data/star/*.csv and runs the checks)"],
  ["3. Create the database","Run sql/01_create_schema.sql in SQL Server"],
  ["4. Load","Edit the folder path in sql/02_load_data.sql, then run it; confirm with sql/03_checks_and_views.sql"],
  ["5. Power BI","Get Data > SQL Server (or Text/CSV on data/star), set relationships, add powerbi/measures.dax, apply powerbi/theme.json; follow powerbi/BUILD_GUIDE.md"]],[4,12.5]),
 P("Repository: link to be added after upload to GitHub.",S)]
def foot(c,d):
    c.saveState(); c.setFont("Helvetica",8); c.setFillColor(colors.HexColor("#777")); c.drawString(2*cm,1.1*cm,"Smart Manufacturing & Predictive Maintenance - Project Documentation"); c.drawRightString(A4[0]-2*cm,1.1*cm,f"Page {d.page}"); c.restoreState()
SimpleDocTemplate("docs/Project_Documentation.pdf",pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=1.8*cm,bottomMargin=1.8*cm,title="Smart Manufacturing - Project Documentation",author="Eman Sayed Seddik").build(s,onFirstPage=lambda c,d:None,onLaterPages=foot)
