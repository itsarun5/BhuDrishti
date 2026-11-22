
import numpy as np
import rasterio
from rasterio.io import MemoryFile

def calculate_ndbi(swir_file, nir_file):

    with MemoryFile(swir_file.getvalue()) as swir_memory:
        with swir_memory.open() as swir_dataset:
            swir = swir_dataset.read(1, masked=True)
            profile = swir_dataset.profile
            transform = swir_dataset.transform
            crs = swir_dataset.crs

    with MemoryFile(nir_file.getvalue()) as nir_memory:
        with nir_memory.open() as nir_dataset:
            nir = nir_dataset.read(1, masked=True)

            if swir.shape != nir.shape:
                raise ValueError("SWIR and NIR images must have matching dimensions.")

            if transform != nir_dataset.transform:
                raise ValueError("Images must have matching pixel alignment.")

            if crs != nir_dataset.crs:
                raise ValueError("Images must use the same CRS.")

    swir_array = np.asarray(swir.filled(np.nan), dtype=np.float32)
    nir_array = np.asarray(nir.filled(np.nan), dtype=np.float32)

    denominator = swir_array + nir_array

    valid = (
        np.isfinite(swir_array) &
        np.isfinite(nir_array) &
        (denominator != 0)
    )

    ndbi = np.full(swir_array.shape, np.nan, dtype=np.float32)

    ndbi[valid] = (
        (swir_array[valid] - nir_array[valid]) /
        denominator[valid]
    )

    return ndbi, crs, profile
