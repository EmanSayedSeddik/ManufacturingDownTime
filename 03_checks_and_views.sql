USE SmartManufacturingDW;
GO
-- ---------- Sanity checks: run after loading; expected values from the ETL ----------
SELECT 'fact_readings' AS tbl, COUNT(*) AS n,  100000 AS expected FROM dbo.fact_readings
UNION ALL SELECT 'dim_machine', COUNT(*), 5000 FROM dbo.dim_machine
UNION ALL SELECT 'failures (machine_failure=1)', SUM(CAST(machine_failure AS INT)), 1472 FROM dbo.fact_readings;
GO

-- ---------- Reporting view used by Power BI (optional: you can also import the tables directly) ----------
CREATE OR ALTER VIEW dbo.vw_failure_by_factory AS
SELECT m.factory_id,
       COUNT(*)                                         AS readings,
       SUM(CAST(f.machine_failure AS INT))              AS failures,
       CAST(100.0 * SUM(CAST(f.machine_failure AS INT)) / COUNT(*) AS DECIMAL(5,2)) AS failure_rate_pct,
       SUM(f.downtime_hours)                            AS downtime_hours
FROM dbo.fact_readings f
JOIN dbo.dim_machine   m ON m.machine_key = f.machine_key
GROUP BY m.factory_id;
GO

CREATE OR ALTER VIEW dbo.vw_failure_type_summary AS
SELECT ft.failure_type_name, COUNT(*) AS events
FROM dbo.fact_readings f
JOIN dbo.dim_failure_type ft ON ft.failure_type_key = f.failure_type_key
WHERE ft.is_failure = 1
GROUP BY ft.failure_type_name;
GO

/* Risk rule used to populate fact_readings.risk_level (done in the Python ETL):
   Critical : failure_probability >= 5   OR machine_health_score < 65
   High     : failure_probability >= 3   OR machine_health_score < 68
   Medium   : failure_probability >= 1.7
   Low      : otherwise
   Reason: the source column maintenance_priority is 'Low' in every row, so it carries no information. */
