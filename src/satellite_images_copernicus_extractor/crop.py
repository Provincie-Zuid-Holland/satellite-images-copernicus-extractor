import rasterio
import geopandas as gpd
from rasterio.mask import mask

def crop_tif_with_geojson(tif_path, geojson_path, output_path):
    try:
        # Open the GeoTIFF file
        with rasterio.open(tif_path) as src:
            # Read the GeoJSON file
            with open(geojson_path, "r") as geojson_file:
                geojson_data = gpd.read_file(geojson_file)
                geojson_data = geojson_data.set_crs("EPSG:4326").to_crs("EPSG:28992")

                # Extract the geometry from the GeoJSON
                geom = geojson_data.geometry.values[0]

                # Perform the crop operation
                out_image, out_transform = mask(src, [geom], crop=True)
                out_meta = src.meta.copy()

                # Update the metadata for the cropped image
                out_meta.update(
                    {
                        "driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform,
                    }
                )

                # Write the cropped image to a new GeoTIFF file
                with rasterio.open(output_path, "w", **out_meta) as dest:
                    dest.write(out_image)

                print(f"Cropped GeoTIFF saved to {output_path}")
    except Exception as e:
        print(f"Error cropping GeoTIFF: {e}")