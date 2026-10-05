---
marp: true
title: Geospatial pipelines with Kedro
paginate: true
style: |
  @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap");

  /* ---------- Tokens ---------- */
  section {
    --primary: #2ba4a0;
    --cyan: #04ccc5;
    --yellow: #ffe334;
    --black: #000000;
    --white: #ffffff;
    --ink: #2b2b2b;
  }

  /* ---------- Base: Inter only. Big = Bold, small = Regular ---------- */
  section,
  section code,
  section pre,
  section pre code {
    font-family: Inter, sans-serif;
    font-weight: 400;
  }
  section {
    background: var(--white);
    color: var(--ink);
    font-size: 24px;
    line-height: 1.45;
    padding: 72px 88px;
  }
  section h1,
  section h2 {
    font-weight: 700;
    letter-spacing: -0.035em;
    line-height: 0.98;
    color: inherit;
    border: none;
    padding: 0;
    margin: 0;
  }
  section h2 { font-size: 64px; }
  section p { margin: 0; }
  section strong { font-weight: 700; color: inherit; }
  section em { font-style: normal; }
  section code {
    background: none;
    color: inherit;
    padding: 0;
    font-size: 1em;
  }
  section::after {
    font-family: Inter, sans-serif;
    font-size: 14px;
    color: var(--primary);
    right: 40px;
    bottom: 28px;
  }

  /* ---------- 1. Hero ---------- */
  section.hero {
    background:
      linear-gradient(90deg, rgba(0, 0, 0, 0.88) 0%, rgba(0, 0, 0, 0.55) 45%, rgba(0, 0, 0, 0) 80%),
      url("https://cdn.prod.website-files.com/6050a76fa6a633d5d54ae714/60db42e458a2686322b441ef_imagery-4.jpeg") center / cover;
    color: var(--white);
    justify-content: flex-end;
    align-items: flex-start;
    padding: 88px;
  }
  section.hero h1 {
    font-size: 112px;
    max-width: 900px;
    letter-spacing: -0.045em;
  }
  section.hero h1 + p {
    margin-top: 36px;
    font-size: 26px;
    max-width: 640px;
  }
  section.hero p:last-child {
    margin-top: 56px;
    font-size: 16px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--cyan);
  }

  /* ---------- 2. Split: black problem / white numbered answer ---------- */
  section.split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: repeat(3, auto);
    align-content: center;
    column-gap: 176px;
    background: linear-gradient(90deg, var(--black) 50%, var(--white) 50%);
  }
  section.split > :not(ol) { grid-column: 1; color: var(--white); }
  section.split h2 { font-size: 72px; }
  section.split h2 + p { margin-top: 40px; font-size: 22px; }
  section.split ul {
    margin: 24px 0 0;
    padding: 0;
    list-style: none;
    font-size: 20px;
  }
  section.split ul li {
    padding: 12px 0;
    border-top: 1px solid rgba(255, 255, 255, 0.25);
  }
  section.split ol {
    grid-column: 2;
    grid-row: 1 / span 3;
    align-self: center;
    margin: 0;
    padding: 0;
    list-style: none;
    counter-reset: item;
  }
  section.split ol li {
    counter-increment: item;
    display: grid;
    grid-template-columns: 150px 1fr;
    align-items: center;
    padding: 20px 0;
  }
  section.split ol li::before {
    content: counter(item, decimal-leading-zero);
    grid-row: 1 / span 2;
    font-size: 96px;
    font-weight: 700;
    letter-spacing: -0.05em;
    line-height: 1;
    color: var(--primary);
  }
  section.split ol li strong { display: block; font-size: 32px; letter-spacing: -0.02em; }
  section.split ol li { font-size: 20px; }

  /* ---------- 3, 4, 5, 7. Code: statement left, terminal right ---------- */
  section.code {
    display: grid;
    grid-template-columns: 5fr 7fr;
    grid-template-rows: 1fr auto auto auto 1fr;
    column-gap: 72px;
  }
  section.code > :not(pre) { grid-column: 1; }
  section.code > h2 { grid-row: 2; }
  section.code > h1 { grid-row: 3; margin-top: 32px; }
  section.code > p { grid-row: 3; margin-top: 32px; }
  section.code > h1 ~ p { grid-row: 4; }
  section.code h2 { font-size: 60px; }
  section.code h1 {
    font-size: 140px;
    letter-spacing: -0.06em;
    line-height: 0.85;
    color: var(--primary);
  }
  section.code p { font-size: 22px; max-width: 420px; }
  section.code p code { color: var(--primary); }
  section.code pre {
    grid-column: 2;
    grid-row: 1 / -1;
    align-self: center;
    margin: 0;
    padding: 64px 36px 36px;
    font-feature-settings: "calt" 0, "liga" 0;
    background: var(--black);
    color: var(--white);
    border: none;
    border-radius: 10px;
    font-size: 17px;
    line-height: 1.6;
    position: relative;
  }
  section.code pre::before {
    content: "";
    position: absolute;
    top: 24px;
    left: 36px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--yellow);
    box-shadow: 18px 0 0 var(--primary), 36px 0 0 var(--cyan);
  }
  section.code pre code { color: var(--white); }

  /* Syntax colours on the dark terminal */
  section pre .hljs-keyword,
  section pre .hljs-built_in,
  section pre .hljs-title { color: var(--cyan); }
  section pre .hljs-attr,
  section pre .hljs-params,
  section pre .hljs-type { color: var(--primary); }
  section pre .hljs-string,
  section pre .hljs-number,
  section pre .hljs-literal { color: var(--yellow); }
  section pre .hljs-comment { color: rgba(255, 255, 255, 0.45); }
  section pre .hljs-meta,
  section pre .hljs-bullet,
  section pre .hljs-punctuation { color: var(--white); }

  /* ---------- 6. Interlude ---------- */
  section.interlude {
    background: var(--yellow);
    color: var(--black);
    justify-content: center;
    align-items: center;
    text-align: center;
  }
  section.interlude h2 {
    font-size: 148px;
    letter-spacing: -0.055em;
    max-width: 1000px;
  }
  section.interlude p { margin-top: 48px; font-size: 26px; }

  /* ---------- 8. Bento ---------- */
  section.bento {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: 1fr 1fr;
    gap: 16px;
    padding: 56px;
    background: var(--black);
    color: var(--white);
    counter-reset: item;
  }
  section.bento h2 {
    grid-column: span 2;
    align-self: end;
    padding: 24px;
    font-size: 104px;
    letter-spacing: -0.05em;
  }
  section.bento ol { display: contents; }
  section.bento ol li {
    counter-increment: item;
    list-style: none;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    margin: 0;
    padding: 28px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    font-size: 18px;
    line-height: 1.35;
    color: rgba(255, 255, 255, 0.7);
  }
  section.bento ol li::before {
    content: counter(item, decimal-leading-zero);
    margin-bottom: auto;
    font-size: 16px;
    color: var(--cyan);
  }
  section.bento ol li:first-child {
    background: var(--primary);
    border-color: var(--primary);
    color: var(--white);
  }
  section.bento ol li:first-child::before { color: var(--white); }
  section.bento ol li strong {
    display: block;
    margin-bottom: 8px;
    font-size: 34px;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: var(--white);
  }
  section.bento ol li strong code { font-weight: 700; color: inherit; }
  section.bento > p {
    grid-column: span 2;
    display: flex;
    align-items: flex-end;
    padding: 28px;
    border-radius: 10px;
    background: var(--yellow);
    color: var(--black);
  }
  section.bento > p strong { font-size: 64px; letter-spacing: -0.045em; line-height: 1; }
---

<!-- _class: hero -->
<!-- _paginate: false -->

# Geospatial pipelines with Kedro

Reproducible and scalable geospatial data workflows

Biel Stela Ballester

---

<!-- _class: split -->

## Why Kedro for geospatial?

Geospatial projects tend to turn into a pile of notebooks and scripts:

- Hard-coded paths to shapefiles and rasters
- CRS conversions scattered everywhere
- "Run cell 4, then cell 2, then cell 7"

1. **Data Catalog** Every dataset declared in one place
2. **Pipelines** Pure Python functions wired into a DAG
3. **Reproducibility** Same inputs give the same outputs

---

<!-- _class: code -->

## The Data Catalog

Vector and raster data are declared like any other dataset.

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

<!-- _class: code -->

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

<!-- _class: code -->

## Wiring the pipeline

Nodes connect through dataset names. Kedro works out the run order.

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

<!-- _class: interlude -->
<!-- _paginate: false -->

## Demo: the resulting DAG

`kedro viz`

---

<!-- _class: code -->

## Parameters, not magic numbers

# 100×

more pixels at 10 m than at 100 m: 1 M to 100 M for a 10,000 km² region. Change it in `parameters.yml`, not in code.

```yaml
# conf/base/parameters.yml
target_crs: "EPSG:3035"
resolution_m: 100
```

---

<!-- _class: bento -->

## Takeaways

1. **Catalog, not code** Every dataset declared once
2. **Pure nodes** GeoDataFrame in, GeoDataFrame out
3. **Parameters** CRS, resolution, thresholds
4. **`kedro viz`** Show the pipeline, don't explain it

**Questions?**
