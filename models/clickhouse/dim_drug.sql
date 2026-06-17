CREATE OR REPLACE TABLE dim_drug AS
SELECT
    row_number() OVER () AS drug_key,
    gnrc_name AS generic_name,
    brnd_name AS brand_name,
    MAX(source_year) AS latest_source_year
FROM partd_prescribers
WHERE gnrc_name IS NOT NULL
GROUP BY gnrc_name, brnd_name;
