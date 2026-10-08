"""Custom Kedro datasets: the TESSERA embeddings Zarr store and GeoTIFF rasters."""

from pathlib import Path
from typing import Any

import numpy as np
import rasterio
import zarr
from affine import Affine
from kedro.io import AbstractDataset, DatasetError


class TesseraDataset(AbstractDataset[None, zarr.Group]):
    """Read-only access to one UTM zone of the TESSERA Zarr store.

    Loading only reads the group metadata. Pixels are fetched later, when
    the ``embeddings`` and ``scales`` arrays are indexed, so only the byte
    ranges that are actually needed travel over the network.
    """

    def __init__(self, url: str, group: str):
        self._url = url
        self._group = group

    def load(self) -> zarr.Group:
        return zarr.open_group(f"{self._url}/{self._group}", mode="r")

    def save(self, data: Any) -> None:
        raise DatasetError("TesseraDataset is read-only")

    def _describe(self) -> dict[str, Any]:
        return {"url": self._url, "group": self._group}


class COGDataset(AbstractDataset[dict, dict]):
    """A single-band raster saved as a Cloud Optimized GeoTIFF.

    Saves and loads a dict with ``array`` (2D numpy array), ``transform``
    (affine ``[a, b, x0, d, e, y0]``) and ``crs``.
    """

    def __init__(self, filepath: str):
        self._filepath = Path(filepath)

    def load(self) -> dict:
        with rasterio.open(self._filepath) as src:
            return {
                "array": src.read(1),
                "transform": list(src.transform)[:6],
                "crs": src.crs.to_string(),
            }

    def save(self, data: dict) -> None:
        array = data["array"]
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(
            self._filepath,
            "w",
            driver="COG",
            width=array.shape[1],
            height=array.shape[0],
            count=1,
            dtype=array.dtype,
            crs=data["crs"],
            transform=Affine(*data["transform"]),
            nodata=np.nan,
            compress="deflate",
        ) as dst:
            dst.write(array, 1)

    def _exists(self) -> bool:
        return self._filepath.exists()

    def _describe(self) -> dict[str, Any]:
        return {"filepath": str(self._filepath)}
