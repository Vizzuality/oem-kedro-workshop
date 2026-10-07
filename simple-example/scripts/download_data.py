"""Download the raw data for the example into ``data/01_raw``.

- ``lynx_observations.csv``: GBIF occurrences of the Iberian lynx in Spain.
- ``natura2000_es.gpkg``: Natura 2000 Habitats Directive sites in Spain (EEA).

Run it once from the project root: ``uv run python scripts/download_data.py``
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

import geopandas as gpd
import polars as pl

RAW = Path(__file__).parents[1] / "data" / "01_raw"

GBIF_URL = "https://api.gbif.org/v1/occurrence/search"
LYNX_TAXON_KEY = 2435261  # Lynx pardinus
GBIF_COLUMNS = [
    "gbifID",
    "species",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "year",
    "basisOfRecord",
    "datasetName",
]

N2K_URL = (
    "https://bio.discomap.eea.europa.eu/arcgis/rest/services/"
    "ProtectedSites/Natura2000Sites/MapServer/0/query"
)


def get_json(url: str, params: dict) -> dict:
    with urllib.request.urlopen(f"{url}?{urllib.parse.urlencode(params)}") as r:
        return json.load(r)


def download_gbif() -> None:
    records, offset = [], 0
    while True:
        page = get_json(
            GBIF_URL,
            {
                "taxonKey": LYNX_TAXON_KEY,
                "country": "ES",
                "hasCoordinate": "true",
                "limit": 300,
                "offset": offset,
            },
        )
        records += [{c: r.get(c) for c in GBIF_COLUMNS} for r in page["results"]]
        if page["endOfRecords"]:
            break
        offset += 300
    pl.DataFrame(records, infer_schema_length=None).write_csv(
        RAW / "lynx_observations.csv"
    )
    print(f"GBIF: {len(records)} observations")  # noqa: T201


def download_natura2000() -> None:
    pages, offset = [], 0
    while True:
        page = get_json(
            N2K_URL,
            {
                "where": "MS='ES'",
                "outFields": "SITECODE,SITENAME,SITETYPE",
                "outSR": 4326,
                "maxAllowableOffset": 0.001,  # simplify to ~100 m, keeps the file small
                "geometryPrecision": 5,
                "resultOffset": offset,
                "resultRecordCount": 200,
                "f": "geojson",
            },
        )
        if not page["features"]:
            break
        pages.append(gpd.GeoDataFrame.from_features(page["features"], crs=4326))
        offset += 200
    sites = gpd.pd.concat(pages, ignore_index=True)
    sites.to_file(RAW / "natura2000_es.gpkg", driver="GPKG")
    print(f"Natura 2000: {len(sites)} sites")  # noqa: T201


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    download_gbif()
    download_natura2000()
