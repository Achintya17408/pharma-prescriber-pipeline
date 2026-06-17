CREATE OR REPLACE TABLE dim_provider AS
SELECT
    row_number() OVER () AS provider_key,
    prscrbr_npi AS provider_npi,
    prscrbr_last_org_name AS last_or_org_name,
    prscrbr_first_name AS first_name,
    prscrbr_city AS city,
    prscrbr_state_abrvtn AS state,
    prscrbr_type AS specialty
FROM partd_prescribers
WHERE prscrbr_npi IS NOT NULL
GROUP BY prscrbr_npi, prscrbr_last_org_name, prscrbr_first_name, prscrbr_city, prscrbr_state_abrvtn, prscrbr_type;
