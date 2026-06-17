CREATE OR REPLACE TABLE fact_prescriptions AS
SELECT
    p.prscrbr_npi AS provider_npi,
    p.gnrc_name AS generic_name,
    p.brnd_name AS brand_name,
    p.source_year AS year_key,
    TRY_CAST(p.tot_clms AS DOUBLE) AS total_claims,
    TRY_CAST(p.tot_30day_fills AS DOUBLE) AS total_30_day_fills,
    TRY_CAST(p.tot_day_suply AS DOUBLE) AS total_day_supply,
    TRY_CAST(p.tot_drug_cst AS DOUBLE) AS total_drug_cost,
    TRY_CAST(p.ge65_sprsn_flag AS DOUBLE) AS ge65_suppression_flag
FROM partd_prescribers p;
