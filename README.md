# Manufacturing Downtime & HR Workforce Analytics

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
