/* =====================================================================
   Smart Manufacturing - Star Schema (SQL Server / T-SQL)
   NOTE: written for SQL Server; NOT executed against a live server by the
   author of this file. Run it in a test database first.
   ===================================================================== */
IF DB_ID('SmartManufacturingDW') IS NULL CREATE DATABASE SmartManufacturingDW;
GO
USE SmartManufacturingDW;
GO

-- ---------- Dimensions ----------
CREATE TABLE dbo.dim_machine (
    machine_key            INT           NOT NULL PRIMARY KEY,
    machine_id             VARCHAR(12)   NOT NULL UNIQUE,      -- business key, e.g. MCH-00001
    factory_id             VARCHAR(10)   NOT NULL,
    production_line        VARCHAR(10)   NOT NULL,
    machine_type           VARCHAR(40)   NOT NULL,
    manufacturer           VARCHAR(40)   NOT NULL,
    model                  VARCHAR(12)   NOT NULL,
    installation_year      SMALLINT      NOT NULL,
    machine_age            SMALLINT      NOT NULL,
    machine_capacity       DECIMAL(10,1) NOT NULL,
    machine_power_kw       DECIMAL(10,1) NOT NULL,
    machine_weight_kg      DECIMAL(10,1) NOT NULL,
    shift_hours            TINYINT       NOT NULL,
    previous_failure_count SMALLINT      NOT NULL,
    failure_frequency      DECIMAL(6,3)  NOT NULL
);

CREATE TABLE dbo.dim_date (
    date_key     INT         NOT NULL PRIMARY KEY,              -- yyyymmdd
    [date]       DATE        NOT NULL UNIQUE,
    [year]       SMALLINT    NOT NULL,
    month_num    TINYINT     NOT NULL,
    month_name   VARCHAR(10) NOT NULL,
    [day]        TINYINT     NOT NULL,
    weekday_num  TINYINT     NOT NULL,
    weekday_name VARCHAR(10) NOT NULL,
    iso_week     TINYINT     NOT NULL
);

CREATE TABLE dbo.dim_time (
    time_key   TINYINT     NOT NULL PRIMARY KEY,                -- hour 0-23
    hour_label CHAR(5)     NOT NULL,
    day_part   VARCHAR(10) NOT NULL
);

CREATE TABLE dbo.dim_shift (
    shift_key  TINYINT     NOT NULL PRIMARY KEY,
    shift_name VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE dbo.dim_maintenance_type (
    maintenance_type_key  TINYINT     NOT NULL PRIMARY KEY,
    maintenance_type_name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE dbo.dim_failure_type (
    failure_type_key  TINYINT     NOT NULL PRIMARY KEY,
    failure_type_name VARCHAR(30) NOT NULL UNIQUE,
    is_failure        BIT         NOT NULL
);

-- ---------- Fact ----------
CREATE TABLE dbo.fact_readings (
    monitoring_id              VARCHAR(12) NOT NULL PRIMARY KEY,
    machine_key                INT     NOT NULL REFERENCES dbo.dim_machine(machine_key),
    date_key                   INT     NOT NULL REFERENCES dbo.dim_date(date_key),
    time_key                   TINYINT NOT NULL REFERENCES dbo.dim_time(time_key),
    shift_key                  TINYINT NOT NULL REFERENCES dbo.dim_shift(shift_key),
    maintenance_type_key       TINYINT NOT NULL REFERENCES dbo.dim_maintenance_type(maintenance_type_key),
    failure_type_key           TINYINT NOT NULL REFERENCES dbo.dim_failure_type(failure_type_key),
    last_maintenance_date_key  INT     NOT NULL REFERENCES dbo.dim_date(date_key),
    [timestamp]                DATETIME2(0) NOT NULL,
    -- sensors & operation
    temperature_c FLOAT, vibration_mm_s FLOAT, pressure_bar FLOAT, rotational_speed_rpm INT,
    torque_nm FLOAT, voltage_v FLOAT, current_a FLOAT, power_consumption_kw FLOAT,
    humidity_percent FLOAT, acoustic_level_db FLOAT, bearing_temperature_c FLOAT,
    motor_temperature_c FLOAT, oil_temperature_c FLOAT, coolant_temperature_c FLOAT,
    oil_pressure_bar FLOAT, hydraulic_pressure_bar FLOAT, air_pressure_bar FLOAT,
    operating_hours FLOAT, idle_hours FLOAT, production_cycles INT, load_percentage FLOAT,
    production_rate FLOAT, downtime_hours FLOAT, energy_consumption_kwh FLOAT,
    ambient_temperature_c FLOAT, ambient_humidity_percent FLOAT, dust_level FLOAT,
    air_quality_index INT, noise_level_db FLOAT,
    -- maintenance
    days_since_maintenance FLOAT, maintenance_count INT, maintenance_cost FLOAT,
    last_repair_duration_hours FLOAT, replacement_parts_count INT,
    technician_experience_years INT, days_since_previous_failure FLOAT,
    -- component health & anomaly scores
    bearing_health FLOAT, motor_health FLOAT, pump_health FLOAT, hydraulic_health FLOAT,
    electrical_health FLOAT, cooling_system_health FLOAT,
    temperature_anomaly_score FLOAT, vibration_anomaly_score FLOAT, pressure_anomaly_score FLOAT,
    electrical_anomaly_score FLOAT, energy_anomaly_score FLOAT,
    -- scores & targets
    machine_health_score FLOAT, failure_probability FLOAT, remaining_useful_life_hours INT,
    machine_failure BIT NOT NULL,
    risk_level VARCHAR(8) NOT NULL, risk_rank TINYINT NOT NULL
);

CREATE INDEX ix_fact_machine ON dbo.fact_readings(machine_key);
CREATE INDEX ix_fact_date    ON dbo.fact_readings(date_key);
CREATE INDEX ix_fact_failure ON dbo.fact_readings(failure_type_key) INCLUDE (machine_failure);
GO
