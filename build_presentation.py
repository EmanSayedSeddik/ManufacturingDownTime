import json
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader, simpleSplit
from PIL import Image as PI
W,H=960,540
NAVY=colors.HexColor("#1F3A5F"); BLUE=colors.HexColor("#3C7DD9"); GREY=colors.HexColor("#5A6675"); LIGHT=colors.HexColor("#EAF0F7"); AMB=colors.HexColor("#F2A33A")
kp=json.load(open("data/star/kpis.json")); fx=json.load(open("docs/findings.json")); rv=fx["risk_vs_failure"]
I="docs/images/"
c=canvas.Canvas("presentation/Presentation.pdf",pagesize=(W,H)); c.setTitle("Smart Manufacturing & Predictive Maintenance - Graduation Project"); c.setAuthor("Eman Sayed Seddik")
n=[0]
def base(title):
    n[0]+=1; c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(NAVY); c.rect(0,H-70,W,70,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",26); c.drawString(40,H-46,title)
    c.setFillColor(GREY); c.setFont("Helvetica",10); c.drawRightString(W-30,18,f"{n[0]}")
    c.drawString(40,18,"Smart Manufacturing & Predictive Maintenance | DEPI Graduation Project")
def bullets(items,x,y,w,size=17,gap=12):
    c.setFont("Helvetica",size)
    for t in items:
        lines=simpleSplit(t,"Helvetica",size,w-20)
        c.setFillColor(BLUE); c.circle(x+5,y+size*0.32,3,fill=1,stroke=0); c.setFillColor(colors.HexColor("#1B2733"))
        for ln in lines: c.drawString(x+20,y,ln); y-=size*1.3
        y-=gap
    return y
def pic(p,x,y,w=None,h=None):
    iw,ih=PI.open(p).size
    if w: h=w*ih/iw
    else: w=h*iw/ih
    c.drawImage(ImageReader(p),x,y,width=w,height=h)
def note(t,x,y,w,size=11,color=GREY):
    c.setFillColor(color); c.setFont("Helvetica-Oblique",size)
    for ln in simpleSplit(t,"Helvetica-Oblique",size,w): c.drawString(x,y,ln); y-=size*1.3

# 1 title
n[0]+=1; c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
c.setFillColor(colors.white); c.setFont("Helvetica-Bold",40)
c.drawString(60,330,"Smart Manufacturing &"); c.drawString(60,282,"Predictive Maintenance")
c.setFont("Helvetica",20); c.drawString(60,235,"Power BI dashboard on a SQL Server star schema")
c.setFillColor(AMB); c.rect(60,210,90,4,fill=1,stroke=0)
c.setFillColor(colors.white); c.setFont("Helvetica",15); c.drawString(60,170,"Graduation Project - Digital Egypt Pioneers Initiative (DEPI)"); c.drawString(60,146,"Eman Sayed Seddik"); c.showPage()
# 2 problem
base("Problem and objectives")
y=bullets(["Factories record thousands of sensor readings, but teams still lack one trusted view of machine health, failures, downtime and maintenance effort.",
 "Goal: turn a flat 72-column file into a clean data model and a 4-page Power BI report for maintenance and plant managers.",
 "Success = correct numbers (reconciled with the source), clear pages, and honest limits."],50,H-120,860)
c.setFillColor(LIGHT); c.roundRect(50,70,860,120,10,fill=1,stroke=0)
for i,(v,l) in enumerate([("100,000","readings"),("5,000","machines"),("10","factories"),(f"{kp['failure_rate_pct']}%","readings with a failure")]):
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",34); c.drawCentredString(50+110+i*215,128,v); c.setFillColor(GREY); c.setFont("Helvetica",13); c.drawCentredString(50+110+i*215,100,l)
c.showPage()
# 3 data
base("The data")
bullets(["Kaggle: Smart Manufacturing & Predictive Maintenance (synthetic IIoT data).","100,000 rows x 72 columns; 5,000 machines with 20 readings each; Jan - Mar 2026.","Quality: 0 missing values, 0 duplicate rows (verified).",
 "Groups: machine metadata, sensors, operating conditions, environment, maintenance history, component health, anomaly scores, targets."],50,H-120,520)
c.setFillColor(LIGHT); c.roundRect(600,110,320,300,10,fill=1,stroke=0)
c.setFillColor(NAVY); c.setFont("Helvetica-Bold",15); c.drawString(620,385,"Found while profiling")
bullets(["maintenance_priority = 'Low' in every row","6 failure types (+ No Failure), not 8","Only 1.47% of readings are failures"],620,350,290,size=14,gap=10); c.showPage()
# 4 approach
base("Approach")
steps=[("1  Profile","Check quality, constants per machine, label balance"),("2  Model","Star schema: 1 fact + 6 dimensions"),("3  ETL","Python splits the file and validates totals"),("4  Warehouse","SQL Server DDL with PK/FK, bulk load"),("5  Report","Power BI model, DAX, 4 pages")]
for i,(a,b) in enumerate(steps):
    x=40+i*180; c.setFillColor(NAVY if i%2==0 else BLUE); c.roundRect(x,250,165,90,8,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",16); c.drawString(x+12,312,a)
    c.setFont("Helvetica",11)
    for k,ln in enumerate(simpleSplit(b,"Helvetica",11,140)): c.drawString(x+12,290-k*14,ln)
note("Tools: Python (pandas), SQL Server (T-SQL), Power BI Desktop + DAX, GitHub.",40,200,860,13); c.showPage()
# 5 schema
base("Star schema design")
pic(I+"er_diagram.png",30,60,h=370)
bullets(["Grain: one reading of one machine","Surrogate keys, low-cardinality text moved to dimensions","Checks: rows, FKs, failures and downtime totals match the source"],610,H-130,320,size=14,gap=8); c.showPage()
# 6 dashboard
base("Dashboard design (wireframes)")
for i,f in enumerate(["wf_1_overview.png","wf_2_health.png","wf_3_maintenance.png","wf_4_sensors.png"]):
    pic(I+f,120+(i%2)*390,262-(i//2)*202,w=330)
note("Wireframes - replace with final Power BI screenshots before presenting.",40,40,860,11,AMB); c.showPage()
# 7 findings
base("What the data shows")
pic(I+"fig_failure_types.png",40,230,w=430); pic(I+"fig_factory_rate.png",490,230,w=430)
bullets([f"{kp['failures']:,} failure events in 100,000 readings; spread almost evenly across 6 types (222-265 each).",
 f"Factory failure rates range 1.36%-1.71%, but a chi-square test gives p = {fx['chi2_p']:.2f}: consistent with chance, so no factory ranking."],40,200,880,size=14,gap=6); c.showPage()
# 8 limitation
base("Validation: what the scores can and cannot do")
pic(I+"fig_risk_validation.png",40,170,w=470)
bullets([f"Derived risk tiers (Low/Medium/High/Critical) all show about the same actual failure rate ({rv['Low']['rate_pct']}%-{rv['High']['rate_pct']}%).",
 "No column correlates with the failure label above ~0.007; a cross-validated model scored AUC 0.505 (0.5 = random).",
 "So: the dashboard is for monitoring and reporting - not a validated failure predictor."],530,H-120,400,size=14,gap=8)
note("A real predictive model would need data where failures are linked to sensor history.",40,130,880,12,NAVY); c.showPage()
# 9 next
base("Conclusions and next steps")
bullets(["Delivered: reproducible ETL, SQL Server star schema, DAX measures, theme, 4-page dashboard design, documentation.",
 "Learned: always validate a dataset's claims before building on them.",
 "Next: add row-level drill-through, scheduled refresh, and test the model on data with real failure signals."],50,H-120,860); c.showPage()
# 10 thanks
n[0]+=1; c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont("Helvetica-Bold",44); c.drawString(60,300,"Thank you"); c.setFont("Helvetica",20); c.drawString(60,255,"Questions?"); c.setFont("Helvetica",13); c.drawString(60,200,"Eman Sayed Seddik | linkedin.com/in/eman-sayed-seddik-59bb1616a")
c.showPage(); c.save()
