install:
	pip install -r requirements.txt

ingest-duckdb:
	DLT_DESTINATION=duckdb python pipelines/ingest_partd.py

ingest-clickhouse:
	DLT_DESTINATION=clickhouse python pipelines/ingest_partd.py

ingest-bigquery:
	DLT_DESTINATION=bigquery python pipelines/ingest_partd.py

models:
	python pipelines/run_models.py

export-tableau:
	python -c "import duckdb; con=duckdb.connect('pharma_prescriber_pipeline.duckdb'); con.execute(open('exports/tableau_export.sql').read()); print('Done')"
