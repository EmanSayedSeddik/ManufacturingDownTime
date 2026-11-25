# HR Workforce Analytics — Data Cleaning & ETL Pipeline

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/184-rBOCiMDNz-5LIf7ssICKL9N2Xfp_d)

## Overview
This Python (`pandas`) script cleans raw shift roster records and reconstructs the **`Fact_Workforce_Assignment`** fact table from `HR_Tables_DIRTY.xlsx`. Using vectorized operations, it standardizes machine identifiers, enforces HR termination date rules, and aggregates consecutive daily shifts into continuous machine assignment intervals.

---

## Input & Output
* **Input File:** `HR_Tables_DIRTY.xlsx`
  * `Fact_Shift_Roster`: Daily employee shift logs and machine assignments.
  * `Dim_Employee`: Employee master data including `termination_date`.
* **Output File:** `Fact_Workforce_Assignment_clean.csv` (cleaned and reconstructed assignment table ready for Power BI).

---

## Data Cleaning & Transformation Steps

1. **Raw Data Ingestion (String-Safe Loading)**
   * Reads `Fact_Shift_Roster` and `Dim_Employee` with `dtype=str` and `keep_default_na=False` to preserve leading zeros and prevent unintended type coercion during string standardization.

2. **Machine ID Standardization & Validation**
   * Builds a reference set of valid machine IDs (`MCH-00001` through `MCH-05000`).
   * Cleans formatting typos in `machine_id` by converting text to uppercase, replacing letter `"O"` with `"0"`, and zero-padding numeric suffixes to 5 digits (`MCH-XXXXX`).
   * Blanks out any invalid or out-of-range machine IDs.

3. **Post-Termination Record Filtering**
   * Deduplicates `Dim_Employee` on `employee_id` to map each employee's `termination_date`.
   * Removes invalid shift roster entries where `work_date` occurs after the employee's recorded `termination_date`.

4. **Consecutive Assignment Reconstruction & Feature Engineering**
   * Filters out unassigned shifts (`machine_id != ""`) and sorts records chronologically by `employee_id` and `work_date`.
   * Uses shift comparison and cumulative sum (`cumsum()`) to detect contiguous blocks of working days on the same machine per employee.
   * Aggregates each contiguous block to determine `assignment_start_date` (`min`) and `assignment_end_date` (`max`).
   * Generates tracking attributes per employee:
     * `machine_assignment_count`: Sequential assignment number for each employee.
     * `previous_machine_id`: The machine ID from the employee's immediately preceding assignment.
     * `is_machine_rotation`: Flags `"Yes"` if the assignment represents a rotation from a previous machine, and `"No"` otherwise.
   * Assigns formatted primary keys (`ASG-000001`, `ASG-000002`, ...) and exports the final dataset to CSV.
