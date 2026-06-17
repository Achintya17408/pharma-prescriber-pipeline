import os
from typing import Iterable, Dict, Any
import dlt
import requests
from dotenv import load_dotenv
from cms_dataset_ids import CMS_DATASET_IDS

load_dotenv()

API_BASE = "https://data.cms.gov/data-api/v1/dataset/{dataset_id}/data"
YEARS = sorted(CMS_DATASET_IDS)


def _validate_dataset_id(year: int, dataset_id: str) -> None:
    if not dataset_id or dataset_id.startswith("PASTE_"):
        raise ValueError(
            f"CMS dataset UUID for {year} is not configured. "
            "Open data.cms.gov, copy the API dataset UUID, and update pipelines/cms_dataset_ids.py."
        )


@dlt.resource(name="partd_prescribers", write_disposition="append")
def fetch_partd_year(year: int) -> Iterable[Dict[str, Any]]:
    dataset_id = CMS_DATASET_IDS[year]
    _validate_dataset_id(year, dataset_id)
    offset = 0
    limit = int(os.getenv("CMS_PAGE_LIMIT", "5000"))
    while True:
        response = requests.get(
            API_BASE.format(dataset_id=dataset_id),
            params={"size": limit, "offset": offset},
            timeout=60,
        )
        response.raise_for_status()
        rows = response.json()
        if not rows:
            break
        for row in rows:
            row["source_year"] = year
            yield row
        offset += limit


def run() -> None:
    destination = os.getenv("DLT_DESTINATION", "duckdb")
    pipeline = dlt.pipeline(
        pipeline_name="pharma_prescriber_pipeline",
        destination=destination,
        dataset_name="pharma_prescriber",
    )
    for year in YEARS:
        print(f"Loading CMS Medicare Part D data for {year} into {destination}...")
        info = pipeline.run(fetch_partd_year(year))
        print(info)


if __name__ == "__main__":
    run()
