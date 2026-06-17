COPY (
    SELECT
        f.year_key,
        f.provider_npi,
        dp.specialty,
        dp.city,
        dp.state,
        f.generic_name,
        f.brand_name,
        f.total_claims,
        f.total_30_day_fills,
        f.total_day_supply,
        f.total_drug_cost,
        CASE WHEN f.total_claims > 0 THEN f.total_drug_cost / f.total_claims END AS cost_per_claim
    FROM fact_prescriptions f
    LEFT JOIN dim_provider dp ON f.provider_npi = dp.provider_npi
) TO 'exports/tableau_prescriber_export.csv' (HEADER, DELIMITER ',');
