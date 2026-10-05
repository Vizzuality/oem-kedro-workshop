---
marp: true
title: Geospatial pipelines with Kedro
paginate: true
style: |
  @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap");

  /* Vizzuality palette (from vizzuality.com) */
  section {
    --black: #222222;
    --green: #2ba4a0;
    --cream: #f8f5f3;
    --yellow: #fae356;
    --grey: #86868b;

    font-family: Inter, sans-serif;
    font-size: 28px;
    background: var(--cream);
    color: var(--black);
    padding: 64px 80px;
  }
  h1, h2 {
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--black);
  }
  h2 {
    font-size: 1.6em;
    border-bottom: 6px solid var(--green);
    padding-bottom: 0.2em;
    width: fit-content;
  }
  strong { color: var(--green); }
  em { color: var(--grey); }
  ul li::marker, ol li::marker { color: var(--green); font-weight: 800; }
  code {
    background: #fff;
    color: var(--black);
    border-radius: 4px;
  }
  pre {
    background: #fff;
    border-left: 6px solid var(--green);
    border-radius: 4px;
    font-size: 0.8em;
  }
  section::after { color: var(--grey); font-size: 0.6em; }

  section.lead {
    text-align: center;
    justify-content: center;
  }
  section.lead h2 { margin-inline: auto; }

  section.dark {
    background: var(--black);
    color: var(--cream);
  }
  section.dark h1, section.dark h2 { color: var(--cream); }
  section.dark h1 { font-size: 2.4em; }
  section.dark h1::after {
    content: "";
    display: block;
    width: 120px;
    height: 8px;
    margin: 0.4em auto 0;
    background: var(--yellow);
  }
  section.dark em { color: var(--green); }
  section.dark code { background: #333; color: var(--yellow); }
---

<!-- _class: lead dark -->
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

<!-- _class: lead dark -->

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
