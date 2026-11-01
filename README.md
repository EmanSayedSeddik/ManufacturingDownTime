# Data

The raw CSV (~100,000 rows x 72 columns) is **not stored in this repository** because of its size.

1. Download *Smart Manufacturing & Predictive Maintenance Dataset* from Kaggle (file `ai_smart_manufacturing_predictive_maintenance.csv`) and place it in this folder.
2. Run `python etl/build_star_schema.py` from the repo root. It writes the star-schema CSVs to `data/star/` (also not committed).
