import marimo

__generated_with = "0.25.1"
app = marimo.App(
    width="medium",
    layout_file="layouts/kedro-workshop-slides.slides.json",
)


@app.cell(hide_code=True)
def _():
    import marimo as mo

    mo.md("""
    # Geospatial pipelines with Kedro

    *Reproducible and testable geospatial data workflows*

    Biel Stela Ballester
    """).center()
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Why Kedro for geospatial?

    Geospatial projects tend to turn into a pile of notebooks and scripts:

    - Hard-coded paths to shapefiles and rasters
    - CRS conversions scattered everywhere
    - "Run cell 4, then cell 2, then cell 7"

    Kedro gives us:

    - **Data Catalog**: every dataset declared in one place
    - **Pipelines**: pure Python functions wired into a DAG
    - **Reproducibility**: same inputs give the same outputs
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
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
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
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
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
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
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md("## The resulting DAG"),
        mo.mermaid("""
        graph LR
            A[(admin_boundaries)] --> R[reproject]
            P[/params:target_crs/] --> R
            R --> AP[(admin_projected)]
            AP --> C[compute_area]
            C --> AA[(admin_with_area)]
            AA --> Z[zonal_statistics]
            L[(land_cover)] --> Z
            Z --> ZS[(zonal_stats)]
        """),
        mo.md("`kedro viz` renders this interactively for the real project."),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    resolution = mo.ui.slider(
        start=10, stop=1000, step=10, value=100, label="Pixel size (m)"
    )
    return (resolution,)


@app.cell(hide_code=True)
def _(mo, resolution):
    _area_km2 = 10_000
    _pixels = _area_km2 * 1e6 / resolution.value**2
    _mb = _pixels * 4 / 1e6
    mo.md(f"""
    ## Try it: raster size vs. resolution

    {resolution}

    A **{_area_km2:,} km²** region at **{resolution.value} m** resolution is
    **{_pixels:,.0f} pixels**, or about **{_mb:,.1f} MB** as float32.

    This is the kind of thing worth putting in `parameters.yml` instead of
    hard-coding it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Your turn: run some Python

    The cell below runs **in your browser**. Edit it and press Run (or Ctrl+Enter).
    """)
    return


@app.cell
def _():
    import sys

    print(f"Hello from Python {sys.version.split()[0]}")
    print("Platform:", sys.platform)  # 'emscripten' means it runs in your browser

    sum(i**2 for i in range(10))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Takeaways

    1. Declare geodata in the **catalog**, not in code
    2. Keep nodes **pure**: GeoDataFrame in, GeoDataFrame out
    3. Put CRS, resolution and thresholds in **parameters**
    4. Use `kedro viz` to explain the pipeline to others

    **Questions?**
    """).center()
    return


if __name__ == "__main__":
    app.run()
