---
marp: true
title: Geospatial pipelines with Kedro
paginate: true
style: |
  section.lead {
    text-align: center;
    justify-content: center;
  }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Geospatial pipelines with Kedro

*Reproducible and testable geospatial data workflows*

Biel Stela Ballester

---

## Why Kedro for geospatial?

Geospatial projects tend to turn into a pile of notebooks and scripts:

- Hard-coded paths to shapefiles and rasters
- CRS conversions scattered everywhere
- "Run cell 4, then cell 2, then cell 7"

Kedro gives us:

- **Data Catalog**: every dataset declared in one place
- **Pipelines**: pure Python functions wired into a DAG
- **Reproducibility**: same inputs give the same outputs

---

## The Data Catalog

Vector and raster data are declared like any other dataset:

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

## Nodes are plain functions

```python
import geopandas as gpd


def reproject(gdf: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    return gdf.to_crs(crs)


def compute_area(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    gdf["area_km2"] = gdf.geometry.area / 1e6
    return gdf
```

No I/O inside the function, so it's easy to test with a tiny GeoDataFrame.

---

## Wiring the pipeline

```python
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

<!-- _class: lead -->

## Demo: the resulting DAG

`kedro viz`

---

## Parameters, not magic numbers

CRS, resolution and thresholds live in config, not in code:

```yaml
# conf/base/parameters.yml
target_crs: "EPSG:3035"
resolution_m: 100
```

A 10,000 km² region at 100 m is 1,000,000 pixels (~4 MB as float32).
At 10 m it's 100× that. Worth being able to change in one place.

---

<!-- _class: lead -->

## Takeaways

1. Declare geodata in the **catalog**, not in code
2. Keep nodes **pure**: GeoDataFrame in, GeoDataFrame out
3. Put CRS, resolution and thresholds in **parameters**
4. Use `kedro viz` to explain the pipeline to others

**Questions?**
