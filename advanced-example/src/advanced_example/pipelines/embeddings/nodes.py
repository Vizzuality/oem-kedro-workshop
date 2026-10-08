import logging

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import zarr

logger = logging.getLogger(__name__)


def pixels_in_sites(sites: gpd.GeoDataFrame, transform: list[float]) -> pd.DataFrame:
    """Row/col of every pixel whose centre falls inside a site.

    ``transform`` is the affine ``[a, b, x0, d, e, y0]`` of the raster grid.
    """
    a, _, x0, _, e, y0 = transform
    pixels = []
    for site_id, label, geom in sites[["site_id", "label", "geometry"]].itertuples(
        index=False
    ):
        minx, miny, maxx, maxy = geom.bounds
        cols, rows = np.meshgrid(
            np.arange(int((minx - x0) // a), int((maxx - x0) // a) + 1),
            np.arange(int((maxy - y0) // e), int((miny - y0) // e) + 1),
        )
        inside = shapely.contains_xy(geom, x0 + (cols + 0.5) * a, y0 + (rows + 0.5) * e)
        pixels.append(
            pd.DataFrame(
                {
                    "site_id": site_id,
                    "label": label,
                    "row": rows[inside],
                    "col": cols[inside],
                }
            )
        )
    return pd.concat(pixels, ignore_index=True)


def read_embeddings(
    tessera: zarr.Group, year: int, rows: np.ndarray, cols: np.ndarray
) -> np.ndarray:
    """Read the dequantised embeddings of ``year`` at the given pixels.

    Returns an ``(n_pixels, n_bands)`` array. Only the 32x32 inner chunks that
    contain the pixels are downloaded.
    """
    t = list(tessera["time"][:]).index(year)
    n_bands = tessera["embeddings"].shape[1]
    times = np.full(len(rows), t)
    # coordinate (point-wise) selection, broadcast to (band, pixel)
    quantised = tessera["embeddings"].vindex[
        times[None, :], np.arange(n_bands)[:, None], rows[None, :], cols[None, :]
    ]
    # int8 values times a per-pixel scale; nodata pixels have an infinite scale
    scales = tessera["scales"].vindex[times, rows, cols]
    return quantised.T.astype(np.float32) * scales[:, None]


def extract_embeddings(
    sites: gpd.GeoDataFrame, tessera: zarr.Group, years: dict
) -> pd.DataFrame:
    """One row per pixel with the embedding change between two years as features."""
    sites = sites.to_crs(tessera.attrs["proj:code"])
    pixels = pixels_in_sites(sites, tessera.attrs["spatial:transform"])
    logger.info("Reading %d pixels from TESSERA", len(pixels))

    rows, cols = pixels["row"].to_numpy(), pixels["col"].to_numpy()
    before = read_embeddings(tessera, years["before"], rows, cols)
    after = read_embeddings(tessera, years["after"], rows, cols)
    change = after - before

    features = pd.DataFrame(change, columns=[f"d{i}" for i in range(change.shape[1])])
    table = pd.concat([pixels, features], axis=1)
    valid = np.isfinite(change).all(axis=1)
    logger.info("Dropping %d pixels without data", (~valid).sum())
    return table[valid].reset_index(drop=True)
