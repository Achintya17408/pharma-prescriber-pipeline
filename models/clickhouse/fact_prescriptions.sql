CREATE OR REPLACE TABLE fact_prescriptions AS
SELECT
    p.prscrbr_npi AS provider_npi,
    p.gnrc_name AS generic_name,
    p.brnd_name AS brand_name,
    p.source_year AS year_key,
    toFloat64OrNull(p.tot_clms ) AS total_claims,
    toFloat64OrNull(p.tot_30day_fills ) AS total_30_day_fills,
    toFloat64OrNull(p.tot_day_suply ) AS total_day_supply,
    toFloat64OrNull(p.tot_drug_cst ) AS total_drug_cost,
    toFloat64OrNull(p.ge65_sprsn_flag ) AS ge65_suppression_flag
FROM partd_prescribers p;
