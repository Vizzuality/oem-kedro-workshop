# simple-example: how protected is the Iberian lynx?

[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://kedro.org)

A small Kedro pipeline answering one conservation question:
**what share of Iberian lynx (*Lynx pardinus*) observations in Spain fall inside Natura 2000 sites?**

## Data

| Dataset | Source | Format | Read with |
|---|---|---|---|
| `lynx_observations` | [GBIF](https://www.gbif.org/species/2435261) occurrences in Spain | CSV (lat/lon) | `polars.CSVDataset` |
| `natura2000_sites` | [EEA Natura 2000](https://www.eea.europa.eu/data-and-maps/data/natura-12) Habitats Directive sites in Spain | GeoPackage | `geopandas.GenericDataset` |

## Pipeline

```
lynx_observations ──► to_points ──► reproject_points ──┐
                                                       ├──► flag_protected ──► summarise
natura2000_sites ─────────────────► reproject_sites ───┘
```

Outputs:

- `data/03_primary/lynx_points_flagged.parquet`: every observation with an `in_protected` column (GeoParquet, opens in QGIS).
- `data/08_reporting/protection_summary.csv`: number of observations, how many are protected, and the percentage.

## Run it

```bash
uv sync
uv run python scripts/download_data.py   # once, fills data/01_raw
uv run kedro run
uv run kedro viz                          # explore the DAG
```
