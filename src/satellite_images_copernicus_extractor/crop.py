import rasterio
from rasterio.mask import mask
import geopandas as gpd
import os
import glob
import numpy as np
from matplotlib import pyplot as plt
from rasterio.plot import show

def __make_the_crop(
    path_to_geojson, raster_path, raster_path_cropped, plot
):
    """
    This crops the satellite image with a chosen shape.

    TODO: Make this accept a object of geopandas or shapely and crs independent.
    @param coordinates: Coordinates of the polygon to make the crop on.
    @param raster_path: path to the raster .tiff file.
    @param raster_path_cropped: path were the cropped raster will be stored.
    @param plot: Plot the results true or false
    """

    agdf = gpd.read_file(path_to_geojson)
    area_to_crop = agdf["geometry"]

    with rasterio.open(raster_path) as src:
        print("raster path opened")

        out_image, out_transform = rasterio.mask.mask(
            src, area_to_crop, crop=True, filled=True
        )
        out_profile = src.profile

        # Set the nodata value
        nodata_value = src.nodata if src.nodata is not None else 0
        out_profile.update(
            {
                "driver": "GTiff",
                "interleave": "band",
                "tiled": True,
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "nodata": nodata_value,
            }
        )

        # Create an alpha band for transparency
        alpha = np.where(out_image[0] == nodata_value, 0, 255).astype("uint8")
        out_image = np.concatenate([out_image, alpha[np.newaxis, ...]], axis=0)
        out_profile.update(count=out_image.shape[0])

        with rasterio.open(raster_path_cropped, "w", **out_profile) as dest:
            dest.write(out_image)

    if plot:
        print(
            "Plotting data for:"
            + raster_path_cropped
            + "-----------------------------------------------------"
        )
        with rasterio.open(raster_path_cropped) as src:
            data = src.read(masked=True)
            plt.figure(figsize=(10, 10))
            rasterio.plot.show(data, transform=src.transform)
