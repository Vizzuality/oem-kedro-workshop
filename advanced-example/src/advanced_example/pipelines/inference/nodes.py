import logging
import math

import numpy as np
import pandas as pd
import zarr
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


def area_window(tessera: zarr.Group, bbox: list[float]) -> dict:
    """The rows and columns of the TESSERA grid that cover ``bbox``.

    ``bbox`` is ``[minx, miny, maxx, maxy]`` in the CRS of the store. It is
    snapped outwards to whole pixels.
    """
    a, _, x0, _, e, y0 = tessera.attrs["spatial:transform"]
    minx, miny, maxx, maxy = bbox
    col0, col1 = math.floor((minx - x0) / a), math.ceil((maxx - x0) / a)
    # e is negative: rows grow southwards
    row0, row1 = math.floor((maxy - y0) / e), math.ceil((miny - y0) / e)
    return {
        "rows": [row0, row1],
        "cols": [col0, col1],
        "transform": [a, 0.0, x0 + col0 * a, 0.0, e, y0 + row0 * e],
        "crs": tessera.attrs["proj:code"],
    }


def read_window(
    tessera: zarr.Group, t: int, rows: slice, cols: slice
) -> np.ndarray | None:
    """Dequantised embeddings of time index ``t`` in a window, as ``(band, y, x)``.

    The scales are read first: if the whole window is nodata (the sea, for
    example) the embeddings are not downloaded and ``None`` is returned.
    """
    scales = tessera["scales"][t, rows, cols]
    if not np.isfinite(scales).any():
        return None
    quantised = tessera["embeddings"][t, :, rows, cols]
    return quantised.astype(np.float32) * scales[None]


def classify_area(
    tessera: zarr.Group, model: Pipeline, window: dict, years: dict, tile_size: int
) -> dict:
    """Probability of construction for every pixel in the window.

    The window is processed tile by tile, so only one tile of embeddings is
    in memory at a time. Pixels without data in either year are NaN.
    """
    times = list(tessera["time"][:])
    before, after = times.index(years["before"]), times.index(years["after"])
    (row0, row1), (col0, col1) = window["rows"], window["cols"]
    probability = np.full((row1 - row0, col1 - col0), np.nan, dtype=np.float32)

    tiles = [
        (r, c)
        for r in range(row0, row1, tile_size)
        for c in range(col0, col1, tile_size)
    ]
    for n, (r, c) in enumerate(tiles, start=1):
        logger.info("Classifying tile %d/%d", n, len(tiles))
        rows = slice(r, min(r + tile_size, row1))
        cols = slice(c, min(c + tile_size, col1))
        emb_before = read_window(tessera, before, rows, cols)
        if emb_before is None:
            continue
        emb_after = read_window(tessera, after, rows, cols)
        if emb_after is None:
            continue

        # (band, y, x) -> (pixel, band), same features as in training
        n_bands, height, width = emb_after.shape
        change = (emb_after - emb_before).reshape(n_bands, -1).T
        valid = np.isfinite(change).all(axis=1)
        if not valid.any():
            continue
        features = pd.DataFrame(
            change[valid], columns=[f"d{i}" for i in range(n_bands)]
        )
        tile = np.full(len(change), np.nan, dtype=np.float32)
        tile[valid] = model.predict_proba(features)[:, 1]
        probability[r - row0 : r - row0 + height, c - col0 : c - col0 + width] = (
            tile.reshape(height, width)
        )

    return {
        "array": probability,
        "transform": window["transform"],
        "crs": window["crs"],
    }
