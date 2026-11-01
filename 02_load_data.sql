/* Load the CSVs produced by etl/build_star_schema.py.
   1) Replace C:\smart_dw\ with the folder that holds data/star/*.csv
   2) Order matters: dimensions first, fact last (foreign keys).
   NOTE: not executed by the author; BULK INSERT needs the file to be readable by the SQL Server service account. */
USE SmartManufacturingDW;
GO
DECLARE @p NVARCHAR(200) = N'C:\smart_dw\';   -- <- change me

-- BULK INSERT does not accept a variable for the file name, so build each statement dynamically.
DECLARE @t TABLE (tbl SYSNAME, ord INT);
INSERT @t VALUES ('dim_machine',1),('dim_date',2),('dim_time',3),('dim_shift',4),
                 ('dim_maintenance_type',5),('dim_failure_type',6),('fact_readings',7);

DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql += N'BULK INSERT dbo.' + tbl + N' FROM ''' + @p + tbl + N'.csv'' WITH (FORMAT=''CSV'', FIRSTROW=2, FIELDTERMINATOR='','', ROWTERMINATOR=''0x0a'', CODEPAGE=''65001'', TABLOCK);' + CHAR(10)
FROM @t ORDER BY ord;
EXEC sp_executesql @sql;
GO
