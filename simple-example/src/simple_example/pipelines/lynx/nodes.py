import geopandas as gpd
import polars as pl


def to_points(observations: pl.DataFrame) -> gpd.GeoDataFrame:
    """Turn the lat/lon columns of the observations into point geometries."""
    observations = observations.drop_nulls(["decimalLatitude", "decimalLongitude"])
    geometry = gpd.points_from_xy(
        observations["decimalLongitude"], observations["decimalLatitude"]
    )
    return gpd.GeoDataFrame(
        observations.to_pandas(), geometry=geometry, crs="EPSG:4326"
    )


def reproject(gdf: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    return gdf.to_crs(crs)


def flag_protected(
    points: gpd.GeoDataFrame, sites: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Add an ``in_protected`` column, True when the point is inside any site."""
    inside = gpd.sjoin(points, sites, predicate="within").index.unique()
    points = points.copy()
    points["in_protected"] = points.index.isin(inside)
    return points


def summarise(points: gpd.GeoDataFrame) -> pl.DataFrame:
    n_observations = len(points)
    n_protected = int(points["in_protected"].sum())
    return pl.DataFrame(
        {
            "n_observations": [n_observations],
            "n_protected": [n_protected],
            "pct_protected": [round(100 * n_protected / n_observations, 1)],
        }
    )
