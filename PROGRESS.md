# Progress

## Completed Locally
- Exact original spec copied to `PROJECT_SPEC.md`.
- Required folder structure created.
- dlt ingestion pipeline implemented.
- CMS dataset UUIDs for 2020-2023 filled from data.cms.gov/data.gov metadata.
- Maxio local settings corrected to `localhost:7410`, access key `maxio`, and bucket `pharma-raw`.
- DuckDB, ClickHouse, and BigQuery SQL model files added.
- GitHub Actions workflow added.
- Tableau export SQL and Makefile added.

## Pending External/Manual Steps
- Add ClickHouse/GCP secrets if using those branches.
- Publish Tableau Public dashboard and add the public URL.
- Refresh GitHub CLI auth with `workflow` scope, then push `.github/workflows/etl_pipeline.yml`.
