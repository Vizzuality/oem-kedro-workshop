import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.ops import nearest_points


def reproject(polygons: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    """Reproject to a metric CRS and fix invalid geometries."""
    polygons = polygons.to_crs(crs)
    # "structure" keeps only polygonal parts, no stray lines or points
    polygons["geometry"] = polygons.geometry.make_valid(
        method="structure", keep_collapsed=False
    )
    return polygons


def sample_polygons(polygons: gpd.GeoDataFrame, params: dict) -> gpd.GeoDataFrame:
    """Keep polygons big enough to hold a few pixels and pick a random subset.

    The subset keeps the amount of TESSERA data we download small.
    """
    big_enough = polygons[polygons.area >= params["min_area_m2"]]
    n = min(params["n_polygons"], len(big_enough))
    return big_enough.sample(n=n, random_state=params["seed"])


def construction_sites(polygons: gpd.GeoDataFrame, params: dict) -> gpd.GeoDataFrame:
    """A circle at the centre of each polygon, where we know there is construction.

    We use the largest inscribed circle, shrunk by ``inscribed_proportion``,
    because the centre of the polygon is where the annotator looked the most.
    """
    # maximum_inscribed_circle returns a line from the centre to the closest edge
    circles = shapely.maximum_inscribed_circle(polygons.geometry.values, 1.0)
    centres = shapely.get_point(circles, 0)
    radii = shapely.length(circles) * params["inscribed_proportion"]
    return gpd.GeoDataFrame(geometry=shapely.buffer(centres, radii), crs=polygons.crs)


def _satellite(
    poly: shapely.Geometry, gap: float, radius: float, rng: np.random.Generator
) -> shapely.Geometry:
    """A circle of ``radius`` placed ``gap`` metres away from the polygon edge,
    in a random direction."""
    angle = rng.uniform(0, 2 * np.pi)
    direction = np.array([np.cos(angle), np.sin(angle)])

    # cast a point far away in that direction and find the closest polygon edge
    minx, miny, maxx, maxy = poly.bounds
    centre = np.array([(minx + maxx) / 2, (miny + maxy) / 2])
    far = centre + direction * (max(maxx - minx, maxy - miny) + 1_000)
    edge, _ = nearest_points(poly.boundary, shapely.Point(far))

    # push the circle out from the edge, towards the far point
    edge = np.array([edge.x, edge.y])
    out = (far - edge) / np.linalg.norm(far - edge)
    return shapely.Point(edge + out * (gap + radius)).buffer(radius)


def background_sites(
    selected: gpd.GeoDataFrame, all_polygons: gpd.GeoDataFrame, params: dict
) -> gpd.GeoDataFrame:
    """A small circle next to each polygon, where we assume there is no construction.

    Circles touching any annotated polygon are dropped.
    """
    rng = np.random.default_rng(params["seed"])
    gap, radius = params["background_gap"], params["background_radius"]
    circles = gpd.GeoDataFrame(
        geometry=[_satellite(p, gap, radius, rng) for p in selected.geometry],
        crs=selected.crs,
    )
    touching = gpd.sjoin(circles, all_polygons[["geometry"]], predicate="intersects")
    return circles.drop(touching.index.unique())


def combine_sites(
    construction: gpd.GeoDataFrame, background: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Stack both kinds of sites with a ``label`` (1 = construction) and a ``site_id``."""
    sites = pd.concat(
        [construction.assign(label=1), background.assign(label=0)], ignore_index=True
    )
    sites["site_id"] = sites.index
    return sites[["site_id", "label", "geometry"]]
