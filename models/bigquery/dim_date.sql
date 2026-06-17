CREATE OR REPLACE TABLE dim_date AS
SELECT DISTINCT
    source_year AS year_key,
    DATE(source_year, 1, 1) AS year_start_date,
    DATE(source_year, 12, 31) AS year_end_date
FROM partd_prescribers;
