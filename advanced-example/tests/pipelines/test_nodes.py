import geopandas as gpd
import numpy as np
import pandas as pd
import zarr
from shapely.geometry import Point, box

from advanced_example.pipelines.embeddings.nodes import (
    extract_embeddings,
    pixels_in_sites,
)
from advanced_example.pipelines.inference.nodes import area_window, classify_area
from advanced_example.pipelines.sampling.nodes import (
    background_sites,
    construction_sites,
)
from advanced_example.pipelines.training.nodes import split_data

PARAMS = {
    "inscribed_proportion": 0.7,
    "background_gap": 30,
    "background_radius": 10,
    "seed": 0,
}


def test_construction_sites_are_inside_polygons():
    polygons = gpd.GeoDataFrame(
        geometry=[box(0, 0, 100, 100), box(200, 0, 260, 20)], crs="EPSG:32631"
    )

    sites = construction_sites(polygons, PARAMS)

    assert sites.within(polygons).all()
    assert np.allclose(sites.area, np.pi * np.array([35.0, 7.0]) ** 2, rtol=0.05)


def test_background_sites_do_not_touch_any_polygon():
    polygons = gpd.GeoDataFrame(
        geometry=[box(0, 0, 100, 100), box(150, 0, 250, 100)], crs="EPSG:32631"
    )

    sites = background_sites(polygons, polygons, PARAMS)

    assert not sites.intersects(polygons.union_all()).any()
    assert np.allclose(sites.distance(polygons.union_all()), 30, atol=0.5)


def test_pixels_in_sites():
    sites = gpd.GeoDataFrame(
        {"site_id": [7], "label": [1]}, geometry=[box(10, -20, 30, 0)]
    )

    pixels = pixels_in_sites(sites, [10.0, 0.0, 0.0, 0.0, -10.0, 0.0])

    assert sorted(zip(pixels["row"], pixels["col"])) == [(0, 1), (0, 2), (1, 1), (1, 2)]
    assert (pixels["site_id"] == 7).all()


def _tiny_tessera() -> zarr.Group:
    """A tiny in-memory store with the same layout as TESSERA.

    4x4 pixels of 10 m, 3 bands. The embeddings change by 1.0 between the two
    years everywhere, and pixel (0, 0) has no data.
    """
    tessera = zarr.open_group(zarr.storage.MemoryStore(), mode="w")
    tessera.attrs.update(
        {"proj:code": "EPSG:32631", "spatial:transform": [10, 0, 0, 0, -10, 40]}
    )
    tessera["time"] = np.array([2017, 2025])
    embeddings = np.zeros((2, 3, 4, 4), dtype="int8")
    embeddings[1] = 2
    tessera["embeddings"] = embeddings
    scales = np.full((2, 4, 4), 0.5, dtype="float32")
    scales[:, 0, 0] = np.inf  # nodata
    tessera["scales"] = scales
    return tessera


def test_extract_embeddings_reads_the_change_between_years():
    tessera = _tiny_tessera()
    sites = gpd.GeoDataFrame(
        {"site_id": [0], "label": [1]},
        geometry=[Point(10, 30).buffer(9)],  # covers pixels (0,0) (0,1) (1,0) (1,1)
        crs="EPSG:32631",
    )

    table = extract_embeddings(sites, tessera, {"before": 2017, "after": 2025})

    assert len(table) == 3
    assert (table[["d0", "d1", "d2"]] == 1.0).all().all()


def test_split_keeps_each_site_on_one_side():
    pixels = pd.DataFrame(
        {"site_id": np.repeat(np.arange(20), 5), "label": np.repeat([0, 1], 50)}
    )

    train, test = split_data(pixels, {"test_size": 0.3, "seed": 0})

    assert set(train["site_id"]).isdisjoint(test["site_id"])
    assert len(train) + len(test) == len(pixels)


def test_area_window_snaps_the_bbox_to_whole_pixels():
    window = area_window(_tiny_tessera(), [5, 15, 25, 35])

    assert window["rows"] == [0, 3]
    assert window["cols"] == [0, 3]
    assert window["transform"] == [10, 0.0, 0, 0.0, -10, 40]


class _ChangeModel:
    """Stands in for the trained model: P(construction) is the mean change."""

    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        p = features.mean(axis=1).to_numpy()
        return np.column_stack([1 - p, p])


def test_classify_area_covers_the_window_tile_by_tile():
    tessera = _tiny_tessera()
    window = area_window(tessera, [0, 0, 40, 40])

    result = classify_area(
        tessera, _ChangeModel(), window, {"before": 2017, "after": 2025}, tile_size=3
    )

    probability = result["array"]
    assert probability.shape == (4, 4)
    assert np.isnan(probability[0, 0])  # nodata
    assert (np.delete(probability.ravel(), 0) == 1.0).all()
    assert result["crs"] == "EPSG:32631"
