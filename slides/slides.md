---
marp: true
title: Geospatial pipelines with Kedro
paginate: true
style: |
  /*
    Layouts
    -------
    (none)     Default content slide: `##` title + text, lists, code, images.
    cover      Title slide over satellite imagery. `#` title, then subtitle, then author.
    divider    Black section break. `##` statement with a yellow bar + optional line.
    split      Two columns. The LAST block (code, list, image…) goes on the right,
               everything before it stacks on the left.

    Extras that work on default and split slides:
    - `# 100×`  a `#` heading renders as a big teal number/stat.
    - `1. **Title** text`  ordered lists render as big numbered items.

    Usage:  <!-- _class: split -->
    Combine:  <!-- _class: split divider -->  (black two-column slide)
  */
  @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap");

  section {
    --primary: #2ba4a0;
    --cyan: #04ccc5;
    --yellow: #ffe334;
    --black: #000000;
    --ink: #2b2b2b;
    --muted: #6b6b6b;
    --code-bg: #f6f8fa;
    --border: #e1e4e8;

    font-family: Inter, sans-serif;
    font-size: 26px;
    line-height: 1.45;
    color: var(--ink);
    background: #fff;
    padding: 72px 88px;
  }
  section::after { font-size: 14px; color: var(--primary); right: 40px; bottom: 28px; }

  /* ---------- Typography ---------- */
  section h1,
  section h2,
  section h3 {
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.05;
    color: inherit;
    border: none;
    padding: 0;
    margin: 0;
  }
  section h2 { font-size: 56px; margin-bottom: 32px; }
  section h3 { font-size: 32px; }
  section h1 { font-size: 120px; letter-spacing: -0.05em; line-height: 1; color: var(--primary); margin-bottom: 16px; }
  section p,
  section ul,
  section ol,
  section pre { margin: 0 0 24px; }
  section strong { font-weight: 700; color: inherit; }
  section a { color: var(--primary); }
  section li + li { margin-top: 8px; }

  /* Big numbered lists */
  section ol { list-style: none; padding: 0; counter-reset: item; }
  section ol li {
    counter-increment: item;
    position: relative;
    margin: 0;
    padding: 14px 0 14px 80px;
    border-top: 1px solid var(--border);
  }
  section ol li::before {
    content: counter(item, decimal-leading-zero);
    position: absolute;
    left: 0;
    top: 6px;
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.04em;
    color: var(--primary);
  }
  section ol li strong { margin-right: 0.4em; }

  /* ---------- Code ---------- */
  section code {
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 0.9em;
    background: var(--code-bg);
    color: var(--ink);
    padding: 0.1em 0.3em;
    border-radius: 4px;
  }
  section pre {
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px 24px;
    font-size: 18px;
    line-height: 1.5;
  }
  section pre code { background: none; padding: 0; font-size: 1em; }
  section :is(h1, h2, h3) code { background: none !important; padding: 0; font-size: 1em; color: inherit !important; }

  /* GitHub light syntax colours */
  section pre .hljs-comment,
  section pre .hljs-quote { color: #6a737d; }
  section pre .hljs-keyword,
  section pre .hljs-selector-tag,
  section pre .hljs-type { color: #d73a49; }
  section pre .hljs-string,
  section pre .hljs-regexp { color: #032f62; }
  section pre .hljs-number,
  section pre .hljs-literal,
  section pre .hljs-attr,
  section pre .hljs-variable,
  section pre .hljs-built_in { color: #005cc5; }
  section pre .hljs-title,
  section pre .hljs-section { color: #6f42c1; }
  section pre .hljs-name,
  section pre .hljs-tag { color: #22863a; }
  section pre .hljs-meta,
  section pre .hljs-params,
  section pre .hljs-punctuation { color: var(--ink); }

  /* ---------- cover ---------- */
  section.cover {
    background:
      linear-gradient(90deg, rgba(0, 0, 0, 0.88) 0%, rgba(0, 0, 0, 0.55) 45%, rgba(0, 0, 0, 0) 80%),
      url("https://cdn.prod.website-files.com/6050a76fa6a633d5d54ae714/60db42e458a2686322b441ef_imagery-4.jpeg") center / cover;
    color: #fff;
    justify-content: flex-end;
    padding: 88px;
  }
  section.cover h1 { font-size: 104px; max-width: 900px; color: inherit; margin-bottom: 32px; }
  section.cover p { font-size: 26px; max-width: 640px; }
  section.cover p:last-child {
    margin: 32px 0 0;
    font-size: 16px;
    letter-spacing: 0.12em;
    color: var(--cyan);
  }

  /* ---------- divider ---------- */
  section.divider {
    background: var(--black);
    color: #fff;
    justify-content: center;
  }
  section.divider h2 { font-size: 80px; max-width: 960px; margin-bottom: 24px; }
  section.divider h2::before {
    content: "";
    display: block;
    width: 64px;
    height: 6px;
    margin-bottom: 32px;
    background: var(--yellow);
  }
  section.divider p { color: rgba(255, 255, 255, 0.65); }
  section.divider :not(pre) > code { background: rgba(255, 255, 255, 0.12); color: #fff; }

  /* GitHub dark code on divider slides */
  section.divider pre { background: #161b22; border-color: #30363d; }
  section.divider pre code { color: #e6edf3; }
  section.divider pre .hljs-comment,
  section.divider pre .hljs-quote { color: #8b949e; }
  section.divider pre .hljs-keyword,
  section.divider pre .hljs-selector-tag,
  section.divider pre .hljs-type { color: #ff7b72; }
  section.divider pre .hljs-string,
  section.divider pre .hljs-regexp { color: #a5d6ff; }
  section.divider pre .hljs-number,
  section.divider pre .hljs-literal,
  section.divider pre .hljs-attr,
  section.divider pre .hljs-variable,
  section.divider pre .hljs-built_in { color: #79c0ff; }
  section.divider pre .hljs-title,
  section.divider pre .hljs-section { color: #d2a8ff; }
  section.divider pre .hljs-name,
  section.divider pre .hljs-tag { color: #7ee787; }
  section.divider pre .hljs-meta,
  section.divider pre .hljs-params,
  section.divider pre .hljs-punctuation { color: #e6edf3; }

  /* ---------- split ---------- */
  section.split {
    display: grid;
    grid-template-columns: 5fr 7fr;
    grid-auto-rows: min-content;
    align-content: center;
    column-gap: 64px;
  }
  section.split > * { grid-column: 1; }
  section.split > :last-child {
    grid-column: 2;
    grid-row: 1 / span 20;
    align-self: center;
    margin: 0;
  }
---

<!-- _class: cover -->
<!-- _paginate: false -->

# Geospatial pipelines with Kedro

Reproducible and scalable geospatial data workflows.

Biel Stela Ballester — biel.stela@vizzuality.com

---

<!--_class: divider -->

Get the slides at

`https://vizzuality.github.io/oem-kedro-workshop`


---

## The context

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
4. **`kedro viz`** Show the pipeline, don't explain it

---

<!-- _class: divider -->
<!-- _paginate: false -->

## Thank you

biel.stela@vizzuality.com
