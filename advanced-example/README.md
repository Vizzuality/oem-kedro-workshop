# advanced-example: detecting new construction with TESSERA embeddings

[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://kedro.org)

A Kedro project that trains a **construction detection model** from
[TESSERA](https://geotessera.org) pixel embeddings, using polygons of known
new constructions as training labels.

## Data

| Dataset | Source | Format | Read with |
|---|---|---|---|
| `construction_polygons` | Polygons drawn around constructions that appeared between the two years (bring your own) | any vector file | `geopandas.GenericDataset` |
| `tessera` | [TESSERA v1 embeddings](https://source.coop/tessera/tessera) on Source Cooperative: 128 dimensions, 10 m, 2017–2025 | Zarr v3, one group per UTM zone | custom `TesseraDataset` |

Put the polygons in `data/01_raw/construction_polygons.geojson`. The TESSERA
store is read straight from `https://data.source.coop`; nothing needs to be
downloaded beforehand.

## Pipelines

```
sampling     construction_polygons ──► construction + background circles ──► sampling_sites
embeddings   sampling_sites + tessera ──► extract_embeddings ──► training_pixels
training     training_pixels ──► split_data ──► train_model ──► evaluate_model
                                                      │                │
                                              construction_model  model_metrics
inference    tessera + construction_model ──► area_window ──► classify_area ──► construction_probability
```

- **sampling**: places a circle at the centre of each polygon (construction, `label=1`)
  and a small circle just outside it, in a random direction (no construction, `label=0`).
  Background circles that touch any polygon are dropped.
- **embeddings**: finds the 10 m pixels inside each circle and reads their
  embeddings for `years.before` and `years.after`. The feature is the difference
  between the two years.
- **training**: splits by site, so pixels of one site are never in both train and test.
  Then it fits a `StandardScaler` + `RandomForestClassifier` and reports metrics on the
  held-out sites.
- **inference**: classifies every pixel inside `inference.bbox`, tile by tile
  (`inference.tile_size`), with the same before/after difference as in training.
  Tiles without data (the sea) skip the embeddings download. The result is the
  probability of construction per pixel, as a GeoTIFF.

### Reading only what we need from the Zarr store

The TESSERA store keeps each UTM zone as one huge array
`embeddings[time, band, y, x]` (int8). Each 4096×4096 shard holds 32×32 inner chunks.
`TesseraDataset` only opens the group, which reads the metadata.
`read_embeddings` then does a point-wise selection (`array.vindex[...]`) at the
sampled pixels, and zarr fetches just the inner chunks that contain them, using HTTP
range requests. Embeddings are dequantised by multiplying by the per-pixel `scales` array.

## Outputs

- `data/02_intermediate/sampling_sites.parquet`: the sampling circles (GeoParquet, opens in QGIS).
- `data/05_model_input/training_pixels.parquet`: one row per pixel, with the 128 embedding differences.
- `data/06_models/construction_model.pkl`: the trained scikit-learn pipeline.
- `data/07_model_output/construction_probability.tif`: P(construction) per pixel of the inference area (COG, opens in QGIS).
- `data/08_reporting/model_metrics.json`: the classification report on the test sites.

## Run it

```bash
uv sync
uv run kedro run                              # everything (~1.5 min, mostly the download)
uv run kedro run --pipeline training          # retrain without downloading again
uv run kedro run --params sampling.n_polygons=2000
uv run kedro run --pipeline inference         # classify the area with the saved model
uv run kedro run --pipeline inference --env mallorca  # all of Mallorca, ~1 hour
uv run kedro viz
uv run pytest
```

`sampling.n_polygons` controls how much is downloaded. The default of 500 polygons gives
about 6,000 pixels. The UTM zone (`group` in `conf/base/catalog.yml`) has to match
where your polygons are; Mallorca is `utm31`.
