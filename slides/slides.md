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

![w:300](assets/url-qr.svg)

---
<!-- _footer: " * therefore the context of this workshop and why we are using kedro." -->
## The Context at Vizzuality*


1) Team of 10 scientist and data engineers
2) Multiple projets at time with 1~3 persons allocated each
3) Huge diversity of projects with completely different kinds of data
4) From small .csv to 100 GBs of EO data

---

## Geospatial data pipelines 

- Geospatial projects tend to turn into a pile of notebooks, scripts and shell commands.
- People have different backgrounds.
- Teams have different levels of software engineering skills.

![w:400](assets/too-many-nb.png)

---

<style scoped>
p {text-align: center;}
</style>

`make` this
`make` that
`make` it messy
`make` it bad

---

## Why Kedro?

`kedro` is an **opinionated** framework that streamlines and organizes data pipeline projects around software engineering "best practices" and standard python project layouts.

---

1. **Project structure** The project template provided is standard python package
1. **Data Catalog** Every dataset declared in one place
2. **Pipelines and Nodes** Pure Python functions wired into a DAG
3. **Reproducibility and testability** Structure allows repetition and eases tests

---
<!-- _class: split divider -->
## `kedro`

start a templated project with `kedro new -n example`

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
│  └── example
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
<!-- _footer: Code can be found [here](https://github.com/Vizzuality/oem-kedro-workshop/tree/main/simple-example)-->
## Example project

How protected is the Iberian lynx?

What share of *Lynx pardinus* observations in Spain fall inside **Natura 2000** sites?

- **GBIF** observations: CSV with lat/lon
- **Natura 2000** Habitats Directive sites: GeoPackage

```
observations ──► to_points ──► reproject ──┐
                                           ├──► flag_protected ──► summarise
natura2000 ─────────────────► reproject ───┘
```

---

<!-- _class: split -->

## The Data Catalog

Record of all the I/O datasets.

Check the available <a href='https://docs.kedro.org/projects/kedro-datasets/en/kedro-datasets-9.6.0/' target='_blank'>kedro datasets</a>

```yaml
# conf/base/catalog.yml
lynx_observations:
  type: polars.CSVDataset
  filepath: data/01_raw/lynx_observations.csv

natura2000_sites:
  type: geopandas.GenericDataset
  filepath: data/01_raw/natura2000_es.gpkg
  file_format: file

lynx_points_flagged:
  type: geopandas.GenericDataset
  filepath: data/03_primary/lynx_points_flagged.parquet
  file_format: parquet
```

---

<!-- _class: split -->

## Nodes are plain functions

**No I/O** inside the function, so it's easy to test with tiny sample data.

```python
# src/simple_example/pipelines/lynx/nodes.py
import geopandas as gpd


def reproject(gdf: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    return gdf.to_crs(crs)


def to_points(observations: pl.DataFrame) -> gpd.GeoDataFrame:
    geometry = gpd.points_from_xy(
        observations["decimalLongitude"], observations["decimalLatitude"]
    )
    return gpd.GeoDataFrame(
        observations.to_pandas(), geometry=geometry, crs="EPSG:4326"
    )
```

---

<!-- _class: split -->

## Wiring the pipeline

Nodes connect through dataset names. Kedro works out the run order.

```python
# src/simple_example/pipelines/lynx/pipeline.py
from kedro.pipeline import Node, Pipeline
from .nodes import reproject, to_points

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            Node(to_points, "lynx_observations", "lynx_points", name="to_points"),
            Node(
                reproject,
                ["lynx_points", "params:target_crs"],
                "lynx_points_projected",
                name="reproject_points",
            ),
            ...
        ]
    )
```

---

<!-- _class: split -->

## Parameters

Parameters go to the `parameters.yml` files, which is namespaced by `env` and easy to change.

```yaml
# conf/{env}/parameters.yml
target_crs: "EPSG:3035"
```

---
<!-- _class: divider -->

## Explore the resulting DAG

`kedro viz`

---

## Hands-on exercise

- Add a node to the pipeline that filters the observations by one year
- Change the output to be vector file of N2K polygons annotated with lynx observations

---

## What doesn't work so well

TODO


---


---

<!-- _class: divider -->
<!-- _paginate: false -->

## Thank you

biel.stela@vizzuality.com
