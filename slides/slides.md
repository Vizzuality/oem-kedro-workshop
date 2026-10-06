---
marp: true
theme: vizzuality
title: Geospatial pipelines with Kedro
paginate: true
---

<!--
_class: cover
_paginate: false
_backgroundImage: "linear-gradient(90deg, rgba(0, 0, 0, 0.88) 0%, rgba(0, 0, 0, 0.55) 45%, rgba(0, 0, 0, 0) 80%), url(https://cdn.prod.website-files.com/6050a76fa6a633d5d54ae714/60db42e458a2686322b441ef_imagery-4.jpeg)"
-->

# Geospatial pipelines with Kedro

Reproducible and scalable geospatial data workflows.

Biel Stela Ballester — biel.stela@vizzuality.com

---

<!--_class: divider -->

Get the slides at

`https://vizzuality.github.io/oem-kedro-workshop`


---

## The context

TODO
> we are a multidisciplinaary team ...
> multiple projects with one or two memebers
> Show project that used kedro: FIP, BSC...

---

## Geospatial data pipelines 

- Geospatial projects tend to turn into a pile of notebooks, scripts and shell commands.
- People come from different backgrounds.
- Teams have different levels of software engineering skills.

---

<!-- _class: split -->

## Why Kedro?

Opinionated framework that streamlines and organizes projects around software engineering "best practices".

1. **Data Catalog** Every dataset declared in one place
2. **Pipelines and Nodes** Pure Python functions wired into a DAG
3. **Reproducibility** Same inputs give the same outputs

---
<!-- _class: split divider -->

## `kedro`

start with `kedro new -n example`

```
.
├── conf
│  ├── base
│  │  ├── catalog.yml
│  │  └── parameters.yml
│  ├── local
│  │  └── credentials.yml
│  └── logging.yml
├── data
│  ├── 01_raw
│  ├── 02_intermediate
│  └── 03_primary
├── src
│  └── simple_example
│     ├── pipeline_registry.py
│     ├── pipelines
│     └── settings.py
├── tests
│  ├── __init__.py
│  └── pipelines
├── pyproject.toml
├── README.md
├── requirements.txt
└── uv.lock
```

---

<!-- _class: split -->

## The Data Catalog

Record of all the I/O datasets.

```yaml
# conf/base/catalog.yml
admin_boundaries:
  type: geopandas.GenericDataset
  filepath: data/01_raw/admin_boundaries.gpkg
  file_format: file

land_cover:
  type: kedro_datasets_experimental.rioxarray.GeoTIFFDataset
  filepath: data/01_raw/land_cover.tif

zonal_stats:
  type: geopandas.GenericDataset
  filepath: data/03_primary/zonal_stats.parquet
  file_format: parquet
```

---

<!-- _class: split -->

## Nodes are plain functions

**No I/O** inside the function, so it's easy to test with tiny sample data.

```python
# src/example/pipelines/{pipeline}/nodes.py
import geopandas as gpd


def reproject(gdf: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    return gdf.to_crs(crs)


def compute_area(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    gdf["area_km2"] = gdf.geometry.area / 1e6
    return gdf
```

---

<!-- _class: split -->

## Wiring the pipeline

Nodes connect through dataset names. Kedro works out the run order.

```python
# src/example/pipelines/{pipeline}/pipeline.py
from kedro.pipeline import Pipeline, node


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(reproject, ["admin_boundaries", "params:target_crs"],
             "admin_projected"),
        node(compute_area, "admin_projected", "admin_with_area"),
        node(zonal_statistics, ["admin_with_area", "land_cover"],
             "zonal_stats"),
    ])
```

---

<!-- _class: split -->

## Parameters

Parameters go to the `parameters.yml` files, which is namespaced by `env` and easy to change.

```yaml
# conf/{env}/parameters.yml
target_crs: "EPSG:3035"
resolution_m: 100
```

---

<!-- _class: divider -->
<!-- _paginate: false -->

## Demo: the resulting DAG

`kedro viz`

---

## What doesn't work so well

TODO


---

## Takeaways

1. **Catalog, not code** Every dataset declared once
2. **Pure nodes** GeoDataFrame in, GeoDataFrame out
3. **Parameters** CRS, resolution, thresholds
4. **`kedro viz`**

---

<!-- _class: divider -->
<!-- _paginate: false -->

## Thank you

biel.stela@vizzuality.com
