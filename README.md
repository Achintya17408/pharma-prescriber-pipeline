# Pharma Prescriber Intelligence Pipeline

A CMS Medicare Part D ETL and analytics project using dlt, DuckDB, ClickHouse/BigQuery-compatible SQL models, GitHub Actions scheduling, and Tableau export SQL.

## Structure

- `PROJECT_SPEC.md` contains the original full project instruction, copied exactly.
- `pipelines/` contains CMS API ingestion and DuckDB model runners.
- `models/` contains DuckDB, ClickHouse, and BigQuery star-schema SQL.
- `exports/tableau_export.sql` creates the Tableau-ready extract.

## Run Locally

```bash
pip install -r requirements.txt
cp .env.example .env
~/.local/bin/maxio --data-dir ./maxio-data --port 7410 --access-key maxio --secret-key maxio123
python setup_maxio.py
python pipelines/ingest_partd.py
python pipelines/run_models.py
make export-tableau
```

CMS UUIDs for 2020-2023 are configured in `pipelines/cms_dataset_ids.py`.
