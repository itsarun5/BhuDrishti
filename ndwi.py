
import numpy as np
import rasterio
from rasterio.io import MemoryFile

def calculate_ndwi(green_file, nir_file):

    with MemoryFile(green_file.getvalue()) as green_memory:
        with green_memory.open() as green_dataset:
            green = green_dataset.read(1, masked=True)
            profile = green_dataset.profile
            transform = green_dataset.transform
            crs = green_dataset.crs

    with MemoryFile(nir_file.getvalue()) as nir_memory:
        with nir_memory.open() as nir_dataset:
            nir = nir_dataset.read(1, masked=True)

            if green.shape != nir.shape:
                raise ValueError("Green and NIR images must have matching dimensions.")

            if transform != nir_dataset.transform:
                raise ValueError("Images must have matching pixel alignment.")

            if crs != nir_dataset.crs:
                raise ValueError("Images must use the same CRS.")

    green_array = np.asarray(green.filled(np.nan), dtype=np.float32)
    nir_array = np.asarray(nir.filled(np.nan), dtype=np.float32)

    denominator = green_array + nir_array

    valid = (
        np.isfinite(green_array) &
        np.isfinite(nir_array) &
        (denominator != 0)
    )

    ndwi = np.full(green_array.shape, np.nan, dtype=np.float32)

    ndwi[valid] = (
        (green_array[valid] - nir_array[valid]) /
        denominator[valid]
    )

    return ndwi, crs, profile
