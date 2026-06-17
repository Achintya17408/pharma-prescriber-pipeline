# Pharma Prescriber Intelligence Pipeline

> **Copilot / Agent Instruction:** This README is a complete self-contained implementation spec. Follow every story and task in exact order. Every tool setup step is included inline — do not skip any setup step. Install, sign up, or configure every tool as instructed before writing any code. Do not invent tools, rename variables, or reorder sections. Implement completely in one pass.

---

## Project Overview

**Business Target:** Automated multi-destination ETL pipeline ingesting multi-year CMS Medicare Part D prescribing data via REST API, modelling it into a star schema, and surfacing prescriber behaviour, drug spending trends, and geographic market patterns through a Tableau Public dashboard.

**Domain:** Pharmaceutical prescriber analytics — mirrors ZS Associates client work.

**Dataset:** CMS Medicare Part D Prescribers by Provider and Drug. Fetched via paginated REST API from `data.cms.gov`. No CSV downloads. No local raw file storage. Years: 2020, 2021, 2022, 2023.

**Three Branches (same codebase, env-var switched):**
- Branch A: DuckDB — local OLAP, zero cost, permanent
- Branch B: ClickHouse Cloud — cloud OLAP, 30-day free trial
- Branch C: BigQuery GCP — cloud warehouse, 1TB/month free tier

---

## Exact Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11 |
| Ingestion | dlt (data load tool) |
| Raw object storage | Maxio v0.3.2 (S3-compatible, replaces MinIO) |
| OLAP Branch A | DuckDB |
| OLAP Branch B | ClickHouse Cloud |
| OLAP Branch C | Google BigQuery |
| SQL modelling | Plain SQL files per destination |
| Scheduling | GitHub Actions (cron) |
| Visualisation | Tableau Public |
| Env management | python-dotenv |

---

## Repository Structure

```
pharma-prescriber-pipeline/
├── .github/workflows/etl_pipeline.yml
├── pipelines/
│   ├── cms_dataset_ids.py
│   └── ingest_partd.py
├── models/
│   ├── duckdb/
│   │   ├── dim_drug.sql
│   │   ├── dim_provider.sql
│   │   ├── dim_date.sql
│   │   └── fact_prescriptions.sql
│   ├── clickhouse/
│   │   ├── dim_drug.sql
│   │   ├── dim_provider.sql
│   │   ├── dim_date.sql
│   │   └── fact_prescriptions.sql
│   └── bigquery/
│       ├── dim_drug.sql
│       ├── dim_provider.sql
│       ├── dim_date.sql
│       └── fact_prescriptions.sql
├── exports/tableau_export.sql
├── pipelines/run_models.py
├── .dlt/
│   ├── config.toml
│   └── secrets.toml.example
├── .env.example
├── .gitignore
├── Makefile
└── requirements.txt
```

---

## Sprint 1 — Python Environment Setup

### Story 1.1 — Install Anaconda and create environment
**Tasks:**
1. Download Anaconda from `anaconda.com/download` — choose installer for your OS (Windows/Mac/Linux)
2. Run installer. During install on Windows: check "Add Anaconda to PATH"
3. Open terminal (or Anaconda Prompt on Windows)
4. Run: `conda create -n pharma-pipeline python=3.11 -y`
5. Run: `conda activate pharma-pipeline`
6. Verify: `python --version` → must show Python 3.11.x

### Story 1.2 — Create project folder and requirements.txt
**Tasks:**
1. `mkdir pharma-prescriber-pipeline && cd pharma-prescriber-pipeline`
2. Create `requirements.txt` with exact contents:
```
dlt[duckdb,bigquery,filesystem]
dlt[clickhouse]
duckdb
pandas
requests
python-dotenv
boto3
```
3. Run: `pip install -r requirements.txt`
4. Verify: `python -c "import dlt, duckdb, pandas, requests; print('ALL OK')"` — must print ALL OK

### Story 1.3 — Create .gitignore immediately
**Tasks:**
1. Create `.gitignore` in project root:
```
.dlt/secrets.toml
gcp_key.json
*.duckdb
.env
__pycache__/
*.pyc
.DS_Store
maxio-data/
```

### Story 1.4 — Create .env.example and .env
**Tasks:**
1. Create `.env.example`:
```
DLT_DESTINATION=duckdb
# Options: duckdb | clickhouse | bigquery
MAXIO_ENDPOINT=http://localhost:7410
MAXIO_ACCESS_KEY=maxio
MAXIO_SECRET_KEY=maxio123
MAXIO_BUCKET=pharma-raw
```
2. Copy to `.env`: `cp .env.example .env`
3. `.env` is gitignored — confirm it is in `.gitignore`

---

## Sprint 2 — Maxio Object Storage Setup

### Story 2.1 — Download and install Maxio v0.3.2
**Tasks:**
1. Go to: `https://github.com/coollabsio/maxio/releases/tag/v0.3.2`
2. Under Assets, download the binary for your OS:
   - Windows: `maxio_windows_amd64.exe`
   - Linux: `maxio_linux_amd64`
   - Mac (Intel): `maxio_darwin_amd64`
   - Mac (Apple Silicon): `maxio_darwin_arm64`
3. On Linux/Mac: `chmod +x maxio_linux_amd64` (make executable)
4. Move to a permanent location. Example on Linux/Mac: `mv maxio_linux_amd64 /usr/local/bin/maxio`
5. On Windows: rename to `maxio.exe` and add its folder to PATH

### Story 2.2 — Start Maxio server
**Tasks:**
1. Create a data directory: `mkdir maxio-data`
2. Start Maxio (it is S3-compatible, runs on port 7410 by default):
```bash
maxio server --dir ./maxio-data --port 7410 --access-key maxio --secret-key maxio123
```
3. Leave this terminal running. Open a new terminal for all other commands.
4. Verify Maxio is running: open browser at `http://localhost:7410` — should show a response (even an error page confirms it's running)

### Story 2.3 — Create Maxio bucket using boto3
**Tasks:**
1. Create `setup_maxio.py`:
```python
import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:7410',
    aws_access_key_id='maxio',
    aws_secret_access_key='maxio123',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

s3.create_bucket(Bucket='pharma-raw')
print("Bucket 'pharma-raw' created successfully")
print("Existing buckets:", [b['Name'] for b in s3.list_buckets()['Buckets']])
```
2. Run: `python setup_maxio.py` — must print bucket created message

---

## Sprint 3 — GitHub Repository Setup

### Story 3.1 — Create GitHub repository
**Tasks:**
1. Go to `github.com` → sign in (or sign up free at `github.com/signup`)
2. Click "+" → New repository
3. Name: `pharma-prescriber-pipeline`
4. Set to Public
5. Do NOT initialise with README (you already have files locally)
6. Click Create repository
7. In your local project folder run:
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/pharma-prescriber-pipeline.git
git add .gitignore requirements.txt .env.example
git commit -m "initial: project structure and requirements"
git push -u origin main
```

### Story 3.2 — Add GitHub Actions secrets
**Tasks:**
1. On GitHub repo page: Settings → Secrets and variables → Actions → New repository secret
2. Add these secrets one by one (values filled in after GCP setup in Sprint 5):
   - `GCP_PROJECT_ID` — your GCP project ID
   - `GCP_CLIENT_EMAIL` — from service account JSON
   - `GCP_PRIVATE_KEY` — from service account JSON (the full key including BEGIN/END lines)
   - `CLICKHOUSE_HOST` — from ClickHouse Cloud (Sprint 4)
   - `CLICKHOUSE_PASSWORD` — from ClickHouse Cloud (Sprint 4)
3. Return here after completing Sprints 4 and 5 to fill secret values

---

## Sprint 4 — ClickHouse Cloud Setup (Branch B)

### Story 4.1 — Sign up for ClickHouse Cloud free trial
**Tasks:**
1. Go to `clickhouse.cloud`
2. Click "Get started" → sign up with email — NO credit card required for trial start
3. Verify email → log in
4. Click "Create new service"
5. Select tier: **Basic**
6. Region: choose closest to you (e.g., AWS ap-south-1 for India)
7. Service name: `pharma-pipeline`
8. Click Create service — wait 2–3 minutes for provisioning

### Story 4.2 — Get ClickHouse credentials
**Tasks:**
1. Once service is active, click your service name
2. Click "Connect" → choose "Python" tab
3. Copy: host (format: `xyz.clickhouse.cloud`), port (`8443`), username (`default`), password
4. Create `.dlt/secrets.toml` (this file is gitignored):
```toml
[destination.clickhouse]
host = "YOUR_HOST.clickhouse.cloud"
port = 8443
database = "default"
user = "default"
password = "YOUR_PASSWORD"
secure = true
```
5. Add `CLICKHOUSE_HOST` and `CLICKHOUSE_PASSWORD` to GitHub Secrets now (Story 3.2)

---

## Sprint 5 — GCP BigQuery Setup (Branch C)

### Story 5.1 — Create GCP account
**Tasks:**
1. Go to `cloud.google.com`
2. Click "Get started for free" → sign in with Google account
3. Enter billing details (credit card for verification — you will NOT be charged for BigQuery free tier)
4. Accept terms → Continue
5. You receive $300 free credits for 90 days PLUS permanent BigQuery free tier (10GB storage, 1TB queries/month)

### Story 5.2 — Create GCP project and enable BigQuery
**Tasks:**
1. Go to `console.cloud.google.com`
2. Top bar → click project dropdown → "New Project"
3. Project name: `pharma-pipeline` → Create
4. Wait for project creation → select it as active project
5. Left menu → "APIs & Services" → "Enable APIs and Services"
6. Search: "BigQuery API" → Click → Enable
7. Wait for enablement (30 seconds)

### Story 5.3 — Create service account and download key
**Tasks:**
1. Left menu → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `dlt-pipeline` → Create and Continue
4. Role: select "BigQuery Admin" → Continue → Done
5. Click the service account email that was just created
6. Click "Keys" tab → "Add Key" → "Create new key" → JSON → Create
7. JSON file downloads automatically — rename it to `gcp_key.json`
8. Move `gcp_key.json` to project root (it is already in `.gitignore`)
9. Verify it is gitignored: `git status` — `gcp_key.json` must NOT appear

### Story 5.4 — Set BigQuery billing alert
**Tasks:**
1. GCP Console → Billing → Budgets & Alerts → Create Budget
2. Name: `pharma-pipeline-budget`
3. Amount: $5
4. Alert thresholds: 50% and 100%
5. Add your email for alerts → Finish
6. This prevents accidental charges if you scan too much data

### Story 5.5 — Wire GCP credentials into dlt
**Tasks:**
1. Open `gcp_key.json` in a text editor
2. Add to `.dlt/secrets.toml` under a new section:
```toml
[destination.bigquery.credentials]
project_id = "pharma-pipeline"
private_key_id = "VALUE_FROM_JSON"
private_key = "VALUE_FROM_JSON"
client_email = "VALUE_FROM_JSON"
token_uri = "https://oauth2.googleapis.com/token"
```
3. Add GitHub Secrets `GCP_PROJECT_ID`, `GCP_CLIENT_EMAIL`, `GCP_PRIVATE_KEY` now (Story 3.2)

---

## Sprint 6 — CMS API Discovery and dlt Pipeline

### Story 6.1 — Find CMS dataset UUIDs manually
**Tasks:**
1. Go to: `data.cms.gov`
2. Search: "Medicare Part D Prescribers by Provider and Drug"
3. Click the dataset page
4. For each year (2020, 2021, 2022, 2023): click that year's dataset → click "API" tab
5. Copy the UUID from the URL. It looks like: `9552919d-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
6. Create `pipelines/cms_dataset_ids.py`:
```python
# CMS Medicare Part D — Prescribers by Provider and Drug
# UUIDs from data.cms.gov API tab for each year
YEAR_DATASET_IDS = {
    2020: "PASTE-2020-UUID-HERE",
    2021: "PASTE-2021-UUID-HERE",
    2022: "PASTE-2022-UUID-HERE",
    2023: "PASTE-2023-UUID-HERE",
}
```

### Story 6.2 — Build the dlt ingestion pipeline
**Tasks:**
1. Create `pipelines/ingest_partd.py` with exact contents:
```python
import os
import dlt
import requests
from dotenv import load_dotenv
from cms_dataset_ids import YEAR_DATASET_IDS

load_dotenv()

CMS_BASE = "https://data.cms.gov/data-api/v1/dataset/{uuid}/data"
BATCH_SIZE = 5000

@dlt.resource(
    name="partd_raw",
    write_disposition="append",
    primary_key=["prscrbr_npi", "gnrc_name", "year"]
)
def partd_prescribers(year: int):
    uuid = YEAR_DATASET_IDS[year]
    url = CMS_BASE.format(uuid=uuid)
    offset = 0

    while True:
        response = requests.get(url, params={"size": BATCH_SIZE, "offset": offset})
        response.raise_for_status()
        batch = response.json()

        if not batch:
            print(f"Year {year}: complete. Total loaded: {offset} rows.")
            break

        for row in batch:
            row["year"] = year
        yield batch

        offset += BATCH_SIZE
        if offset % 50000 == 0:
            print(f"Year {year}: {offset} rows loaded so far...")


@dlt.source
def cms_partd_source(years: list):
    for year in years:
        yield partd_prescribers(year)


def run_pipeline():
    destination = os.getenv("DLT_DESTINATION", "duckdb")
    print(f"Running pipeline → destination: {destination}")

    pipeline = dlt.pipeline(
        pipeline_name="pharma_prescriber_pipeline",
        destination=destination,
        dataset_name="partd",
    )

    load_info = pipeline.run(
        cms_partd_source(years=[2020, 2021, 2022, 2023])
    )
    print(load_info)


if __name__ == "__main__":
    run_pipeline()
```

### Story 6.3 — Test Branch A: DuckDB ingestion
**Tasks:**
1. Ensure `.env` has `DLT_DESTINATION=duckdb`
2. Run: `python pipelines/ingest_partd.py`
3. Verify (run in Python shell):
```python
import duckdb
con = duckdb.connect("pharma_prescriber_pipeline.duckdb")
print(con.execute("SELECT COUNT(*) FROM partd.partd_raw").fetchone())
print(con.execute("SELECT year, COUNT(*) FROM partd.partd_raw GROUP BY year").df())
```
4. Expected: row count > 1,000,000 per year loaded

### Story 6.4 — Test Branch B: ClickHouse ingestion
**Tasks:**
1. Change `.env`: `DLT_DESTINATION=clickhouse`
2. Run: `python pipelines/ingest_partd.py`
3. Log into ClickHouse Cloud → SQL Console → run:
```sql
SELECT year, COUNT(*) FROM partd.partd_raw GROUP BY year ORDER BY year
```
4. Screenshot result → save to `docs/screenshots/clickhouse_load.png`

### Story 6.5 — Test Branch C: BigQuery ingestion
**Tasks:**
1. Change `.env`: `DLT_DESTINATION=bigquery`
2. Run: `python pipelines/ingest_partd.py`
3. Go to GCP Console → BigQuery → your project → dataset `partd` → table `partd_raw` → Preview tab
4. Screenshot → save to `docs/screenshots/bigquery_load.png`
5. Immediately check: Billing → Cost Table — confirm $0 or very small amount

---

## Sprint 7 — Star Schema SQL Models

> **Agent Instruction:** Build DuckDB models first (run them). Then copy to clickhouse/ and bigquery/ folders and adapt only the syntax differences noted. The analytical logic is identical across all three.

### Story 7.1 — DuckDB models

**`models/duckdb/dim_drug.sql`:**
```sql
CREATE OR REPLACE TABLE partd.dim_drug AS
SELECT
    ROW_NUMBER() OVER (ORDER BY gnrc_name) AS drug_id,
    gnrc_name AS generic_name,
    brnd_name AS brand_name
FROM (
    SELECT DISTINCT gnrc_name, brnd_name
    FROM partd.partd_raw
    WHERE gnrc_name IS NOT NULL
);
```

**`models/duckdb/dim_provider.sql`:**
```sql
CREATE OR REPLACE TABLE partd.dim_provider AS
SELECT
    ROW_NUMBER() OVER (ORDER BY prscrbr_npi) AS provider_id,
    prscrbr_npi           AS npi,
    prscrbr_last_org_name AS last_name,
    prscrbr_first_name    AS first_name,
    prscrbr_city          AS city,
    prscrbr_state_abrvtn  AS state,
    prscrbr_type          AS specialty
FROM (
    SELECT DISTINCT
        prscrbr_npi, prscrbr_last_org_name, prscrbr_first_name,
        prscrbr_city, prscrbr_state_abrvtn, prscrbr_type
    FROM partd.partd_raw
    WHERE prscrbr_npi IS NOT NULL
);
```

**`models/duckdb/dim_date.sql`:**
```sql
CREATE OR REPLACE TABLE partd.dim_date AS
SELECT DISTINCT year AS year_id, year
FROM partd.partd_raw;
```

**`models/duckdb/fact_prescriptions.sql`:**
```sql
CREATE OR REPLACE TABLE partd.fact_prescriptions AS
SELECT
    dp.provider_id,
    dd.drug_id,
    dt.year_id,
    CAST(r.tot_clms AS INTEGER)    AS total_claims,
    CAST(r.tot_drug_cst AS DOUBLE) AS total_drug_cost,
    CAST(r.tot_drug_cst AS DOUBLE) / NULLIF(CAST(r.tot_clms AS INTEGER), 0) AS cost_per_claim
FROM partd.partd_raw r
JOIN partd.dim_provider dp ON r.prscrbr_npi = dp.npi
JOIN partd.dim_drug     dd ON r.gnrc_name   = dd.generic_name
JOIN partd.dim_date     dt ON r.year        = dt.year_id
WHERE r.tot_clms IS NOT NULL AND r.tot_drug_cst IS NOT NULL;
```

**`pipelines/run_models.py`:**
```python
import duckdb, os

destination = os.getenv("DLT_DESTINATION", "duckdb")
if destination != "duckdb":
    print(f"Run {destination} models manually in the cloud console using files in models/{destination}/")
    exit()

con = duckdb.connect("pharma_prescriber_pipeline.duckdb")
for model in ["dim_drug", "dim_provider", "dim_date", "fact_prescriptions"]:
    sql = open(f"models/duckdb/{model}.sql").read()
    con.execute(sql)
    print(f"Built: {model}")

result = con.execute("SELECT COUNT(*) FROM partd.fact_prescriptions").fetchone()
print(f"fact_prescriptions row count: {result[0]:,}")
con.close()
```

**Run:** `python pipelines/run_models.py`

### Story 7.2 — ClickHouse model adaptations
**Tasks:**
1. Copy all 4 SQL files: `cp models/duckdb/*.sql models/clickhouse/`
2. In each ClickHouse file, make these changes:
   - `CREATE OR REPLACE TABLE` → `CREATE TABLE IF NOT EXISTS`
   - After the table name and before `AS SELECT`, add: `ENGINE = MergeTree() ORDER BY (first_column_name)`
   - `DOUBLE` → `Float64`, `INTEGER` → `Int32`
3. Run each file in ClickHouse Cloud SQL Console in order: dim_drug → dim_provider → dim_date → fact_prescriptions

### Story 7.3 — BigQuery model adaptations
**Tasks:**
1. Copy all 4 SQL files: `cp models/duckdb/*.sql models/bigquery/`
2. In each BigQuery file:
   - Table refs become `pharma-pipeline.partd.table_name`
   - `DOUBLE` → `FLOAT64`, `INTEGER` → `INT64`
   - `CREATE OR REPLACE TABLE` stays the same (BigQuery supports it)
   - `ROW_NUMBER() OVER (ORDER BY ...)` stays the same (BigQuery supports it)
3. Run each file in BigQuery console in order

---

## Sprint 8 — GitHub Actions Scheduler

### Story 8.1 — Create workflow file
**Tasks:**
1. Create `.github/workflows/etl_pipeline.yml`:
```yaml
name: Pharma ETL Pipeline

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Write dlt secrets
        run: |
          mkdir -p .dlt
          cat > .dlt/secrets.toml << 'EOF'
          [destination.bigquery.credentials]
          project_id = "${{ secrets.GCP_PROJECT_ID }}"
          private_key = "${{ secrets.GCP_PRIVATE_KEY }}"
          client_email = "${{ secrets.GCP_CLIENT_EMAIL }}"
          token_uri = "https://oauth2.googleapis.com/token"
          EOF

      - name: Run pipeline (DuckDB branch — no cloud credentials needed)
        env:
          DLT_DESTINATION: duckdb
        run: python pipelines/ingest_partd.py
```
2. Commit and push: `git add .github/ && git commit -m "feat: add GitHub Actions ETL scheduler" && git push`
3. Go to GitHub repo → Actions tab → verify workflow appears
4. Click "Run workflow" → "Run workflow" button → watch it execute
5. Green checkmark = success. Screenshot → `docs/screenshots/github_actions_success.png`

---

## Sprint 9 — Tableau Public Dashboard

### Story 9.1 — Sign up for Tableau Public
**Tasks:**
1. Go to `public.tableau.com`
2. Click "Sign Up for Tableau Public" → fill email + password → Create account
3. Verify email
4. Download Tableau Public desktop app from: `public.tableau.com/en/s/download`
   - This is FREE. Do NOT download Tableau Desktop (that costs money)
5. Install the app

### Story 9.2 — Export data from DuckDB
**Tasks:**
1. Create `exports/tableau_export.sql`:
```sql
COPY (
    SELECT
        dp.state,
        dp.specialty,
        dd.generic_name,
        dd.brand_name,
        dt.year,
        SUM(f.total_claims)              AS total_claims,
        SUM(f.total_drug_cost)           AS total_drug_cost,
        AVG(f.cost_per_claim)            AS avg_cost_per_claim,
        COUNT(DISTINCT dp.provider_id)   AS unique_prescribers
    FROM partd.fact_prescriptions f
    JOIN partd.dim_provider dp ON f.provider_id = dp.provider_id
    JOIN partd.dim_drug     dd ON f.drug_id     = dd.drug_id
    JOIN partd.dim_date     dt ON f.year_id     = dt.year_id
    GROUP BY dp.state, dp.specialty, dd.generic_name, dd.brand_name, dt.year
) TO 'exports/tableau_export.csv' (HEADER, DELIMITER ',');
```
2. Run:
```python
import duckdb
con = duckdb.connect("pharma_prescriber_pipeline.duckdb")
con.execute(open("exports/tableau_export.sql").read())
print("Export complete. File: exports/tableau_export.csv")
```

### Story 9.3 — Build and publish dashboard
**Tasks:**
1. Open Tableau Public desktop app
2. Connect → Text File → select `exports/tableau_export.csv`
3. Build View 1 (Sheet 1): Horizontal bar — Top 20 generic drugs by total_drug_cost. Filter: year = 2022
4. Build View 2 (Sheet 2): Map — drag `state` to Detail, `total_drug_cost` to Colour. Change mark type to Map
5. Build View 3 (Sheet 3): Line chart — total_drug_cost by year, coloured by generic_name (top 5 drugs)
6. Build View 4 (Sheet 4): Bar chart — top 10 specialties by total_claims
7. Create Dashboard sheet → drag all 4 views in → arrange layout
8. File → Save to Tableau Public → name: "Medicare Part D Prescriber Intelligence"
9. Copy the public URL → paste it here: **[TABLEAU DASHBOARD URL — REPLACE THIS]**
10. Add URL to GitHub README under a "Dashboard" section

---

## Sprint 10 — Makefile and Final Commit

### Story 10.1 — Makefile
**Tasks:**
1. Create `Makefile`:
```makefile
.PHONY: run-duckdb run-clickhouse run-bigquery models export maxio

maxio:
	maxio server --dir ./maxio-data --port 7410 --access-key maxio --secret-key maxio123

run-duckdb:
	DLT_DESTINATION=duckdb python pipelines/ingest_partd.py

run-clickhouse:
	DLT_DESTINATION=clickhouse python pipelines/ingest_partd.py

run-bigquery:
	DLT_DESTINATION=bigquery python pipelines/ingest_partd.py

models:
	python pipelines/run_models.py

export:
	python -c "import duckdb; con=duckdb.connect('pharma_prescriber_pipeline.duckdb'); con.execute(open('exports/tableau_export.sql').read()); print('Done')"
```

### Story 10.2 — Final commit
**Tasks:**
1. `git add -A`
2. `git commit -m "feat: complete pharma prescriber pipeline — all 3 destination branches"`
3. `git push`
4. Verify on GitHub: all files visible, Actions tab shows green run, README shows Tableau URL

---

## Definition of Done

- [ ] `make run-duckdb` completes without error, row count > 1M
- [ ] `make run-clickhouse` completes without error, verified in ClickHouse console
- [ ] `make run-bigquery` completes without error, verified in BigQuery console
- [ ] `make models` builds all 4 star schema tables in DuckDB
- [ ] GitHub Actions workflow shows green tick
- [ ] Tableau dashboard published with public URL in README
- [ ] Screenshots of all 3 destinations in `docs/screenshots/`
- [ ] `gcp_key.json` and `.dlt/secrets.toml` are NOT in git history
- [ ] `pip install -r requirements.txt` works from scratch on a clean machine
