import geopandas as gpd
from shapely.geometry import Point, box

from simple_example.pipelines.lynx.nodes import flag_protected, summarise


def test_flag_protected():
    sites = gpd.GeoDataFrame(geometry=[box(0, 0, 10, 10)], crs="EPSG:3035")
    points = gpd.GeoDataFrame(
        geometry=[Point(5, 5), Point(20, 20), Point(1, 9)], crs="EPSG:3035"
    )

    result = flag_protected(points, sites)

    assert result["in_protected"].tolist() == [True, False, True]


def test_point_in_overlapping_sites_is_counted_once():
    sites = gpd.GeoDataFrame(
        geometry=[box(0, 0, 10, 10), box(5, 5, 15, 15)], crs="EPSG:3035"
    )
    points = gpd.GeoDataFrame(geometry=[Point(7, 7)], crs="EPSG:3035")

    summary = summarise(flag_protected(points, sites))

    assert summary.to_dicts() == [
        {"n_observations": 1, "n_protected": 1, "pct_protected": 100.0}
    ]
