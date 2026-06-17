import os
from pathlib import Path
import duckdb

DB_PATH = os.getenv("DUCKDB_PATH", "pharma_prescriber_pipeline.duckdb")
MODEL_DIR = Path("models/duckdb")
ORDER = ["dim_drug", "dim_provider", "dim_date", "fact_prescriptions"]

with duckdb.connect(DB_PATH) as con:
    for model in ORDER:
        sql_path = MODEL_DIR / f"{model}.sql"
        print(f"Running {sql_path}...")
        con.execute(sql_path.read_text())
    print("DuckDB star schema models completed.")
