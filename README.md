# Manufacturing Downtime & HR Workforce Analytics

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/184-rBOCiMDNz-5LIf7ssICKL9N2Xfp_d)

---

## 1. Project Name
**Manufacturing Downtime & HR Workforce Analytics** — End-to-End Operational & Workforce Intelligence Pipeline

---

## 2. Project Idea
Manufacturing plants frequently face unplanned equipment downtime, excessive overtime costs, and operational safety risks caused by uncertified machine assignments and suboptimal shift coverage. 

This project builds an end-to-end data analytics pipeline starting from raw multi-table HR and shift roster records (`HR_Tables_DIRTY.xlsx`), cleaning and reconstructing consecutive machine assignments via **Python (`pandas`)**, structuring a normalized **Star Schema** in **Power BI & SQL Server**, executing **T-SQL** analytical queries and views, and delivering interactive dashboards to optimize shift scheduling, training compliance, and machine rotation strategies.

---

## 3. Team Members
* **Eman Sayed** — Team Leader
* **Aya Sharweda** — Team Member
* **Nourhan Osman** — Team Member

---

## 4. Work Plan

| Phase | Milestone | Key Activities & Deliverables | Tools Used |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Data Exploration & ETL Cleaning** | Standardize machine IDs, filter post-termination records, and reconstruct consecutive machine assignment intervals. | Python (`pandas`), Google Colab |
| **Phase 2** | **Data Modeling & Database Setup** | Build Star Schema relationships (`Dim_Date`, `Dim_Employee`, `Dim_Shift`, `Fact_Shift_Roster`, `Fact_Machine_Shift_Coverage`, `Fact_Workforce_Assignment_clean`) and standardize SQL data types. | Power BI, DAX Studio, SQL Server |
| **Phase 3** | **SQL Analytical Views & KPIs** | Develop reusable T-SQL views and window-function queries to analyze overtime, compliance risks, machine rotation, and bottleneck equipment. | SQL Server (T-SQL / SSMS) |
| **Phase 4** | **Data Visualization & Reporting** | Design multi-page interactive dashboards, executive KPI cards, and final project documentation. | Tableau / Power BI, GitHub |

---

## 5. Roles & Responsibilities

* **Eman Sayed (Team Leader):**
  * Overall project planning, task coordination, and GitHub repository management.
  * Developing the Python ETL pipeline (`workforce_assignment_cleaning.ipynb`) to clean raw rosters and engineer rotation features.
  * Designing the Star Schema data model, migrating tables to SQL Server, and writing T-SQL analytical views (`manufacturing_downtime_analysis.sql`).

* **Aya Sharweda (Team Member):**
  * Data profiling, quality validation, and verification of business rules across raw HR and shift tables.
  * Assisting in SQL query validation, KPI verification, and compliance/training gap analysis.
  * Contributing to dashboard layout design and insight storytelling.

* **Nourhan Osman (Team Member):**
  cleaned and prepared the 72+ column monitoring table—containing manufacturing downtime, sensor, and quality data—using Power Query.
 extracted a predictive regression formula in Excel to forecast next-cycle machine failures.
 created 5+ Power BI dashboards to predict equipment downtime and uncover failure root causes.

---

## 6. Key Performance Indicators (KPIs)

### Workforce & Attendance KPIs
* **Attendance Rate (%):** Percentage of scheduled shifts marked as `Present` across factories and shifts.
* **Total Actual vs. Scheduled Hours:** Comparison between planned labor capacity and actual worked hours.
* **Total Overtime Hours:** Extra hours worked beyond standard shift schedules, segmented by factory and overnight shifts (`crosses_midnight`).

### Compliance & Safety Risk KPIs
* **Uncertified Shift Risk (%):** Percentage of active shifts where operators ran machines without proper certification (`certified_for_machine_type = 'No'`).
* **Safety & Maintenance Training Gap:** Number of active shifts operated by personnel lacking completed safety or maintenance training.

### Machine Rotation & Utilization KPIs
* **Machine Rotation Rate (%):** Proportion of assignments involving operator rotation to a different machine (`is_machine_rotation = 'Yes'`).
* **Average Assignment Tenure (Days):** Mean duration of consecutive working days an employee stays assigned to a single machine.
* **Average Performance Score:** Employee performance rating evaluated across skill levels, operator types, and rotation frequency.
* **Top Bottleneck Machines:** Top 5 machines per factory ranked by overtime hours and uncertified operator coverage gaps.

---

## 7. Instructor
* **Adham Osama Mohamed**

---

## 8. Project Files
* `workforce_assignment_cleaning.ipynb` — Python (`pandas`) notebook for cleaning raw HR/roster tables and reconstructing consecutive machine assignments.
* `manufacturing_downtime_analysis.sql` — T-SQL script containing schema type conversions, operational KPI queries, `vw_Machine_Rotation_Impact` view, and `DENSE_RANK()` bottleneck analysis.
* `README.md` — Comprehensive project documentation, team structure, work plan, and KPI definitions.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/184-rBOCiMDNz-5LIf7ssICKL9N2Xfp_d)

## Project Overview
An end-to-end workforce operations and manufacturing downtime analytics pipeline. The workflow transforms raw shift rosters (`HR_Tables_DIRTY.xlsx`) using **Python (`pandas`)**, structures a Star Schema data model in **Power BI / SQL Server**, and executes **T-SQL** analytical queries and views to uncover attendance bottlenecks, certification compliance risks, machine rotation impacts, and high-overtime equipment.

---

## Repository Structure
* `workforce_assignment_cleaning.ipynb` — Python (`pandas`) ETL pipeline for cleaning shift rosters and reconstructing consecutive machine assignments.
* `manufacturing_downtime_analysis.sql` — T-SQL script for schema type standardization, operational KPI aggregations, compliance risk analysis, analytical views, and window-function machine ranking.

---

## Phase 1: Python ETL & Data Cleaning (`workforce_assignment_cleaning.ipynb`)
1. **String-Safe Ingestion:** Loads `Fact_Shift_Roster` and `Dim_Employee` with `dtype=str` and `keep_default_na=False` to preserve leading zeros.
2. **Machine ID Standardization:** Validates IDs against `MCH-00001` through `MCH-05000`, corrects formatting typos (`"O"` to `"0"`, zero-padding), and blanks out invalid entries.
3. **Post-Termination Filtering:** Removes invalid shift records logged after an employee's recorded `termination_date`.
4. **Consecutive Assignment Reconstruction:** Uses `shift()` and `cumsum()` to group contiguous working days on the same machine into continuous intervals (`ASG-000001`, ...), engineering `machine_assignment_count`, `previous_machine_id`, and `is_machine_rotation`.

---

## Phase 2: SQL Server Analysis & Views (`manufacturing_downtime_analysis.sql`)
1. **Schema & Data Type Standardization:** Converts numeric fields (`actual_hours`, `overtime_hours`, `operators_on_duty`, `certified_operators_on_duty`) from `nvarchar` to `FLOAT`/`INT` for accurate aggregations.
2. **Shift Attendance & Overtime Analysis:** Joins `Fact_Shift_Roster`, `Dim_Date`, and `Dim_Shift` to evaluate attendance rates and overtime across factories, months, and overnight shifts (`crosses_midnight`).
3. **Certification Compliance & Training Risk:** Tracks active shifts operated by uncertified personnel (`certified_for_machine_type = 'No'`) alongside safety and maintenance training gaps across production lines and skill levels.
4. **Machine Rotation Impact View (`vw_Machine_Rotation_Impact`):** Reusable SQL View calculating average consecutive assignment duration (`DATEDIFF`), machine rotation frequency, and average `performance_score`.
5. **Top 5 Bottleneck Machines per Factory:** Uses a `CTE` and `DENSE_RANK() OVER (PARTITION BY factory_id ...)` to identify the highest-overtime machines and uncertified operator coverage gaps per plant.
