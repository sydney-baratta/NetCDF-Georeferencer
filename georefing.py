import sys
import os
from pathlib import Path
import xarray as xr
import rasterio
import numpy as np
from rasterio.transform import from_origin
from pyproj import Proj, Transformer

def parse_bands(bands):
    return [bool(int(bit)) for bit in bands]

def get_out_proj(longitudes, latitudes):
    out_proj_code = 'epsg:32'
    mean_lon = np.mean(longitudes)
    utm_zone = int(np.floor((mean_lon + 180) / 6)) + 1

    if np.mean(latitudes[:]) >= 0:
        out_proj_code = out_proj_code + '6'
    else:
        out_proj_code = out_proj_code + '7'
    
    out_proj_code = out_proj_code + str(utm_zone)
    return out_proj_code
    

def main():
    if len(sys.argv) < 4:
        print("Error: invalid arguments #")
        sys.exit(1)

    # Load the NetCDF file
    file_path = sys.argv[1]
    output_dir = sys.argv[2]
    input_bands = parse_bands(sys.argv[3])

    ds = xr.open_dataset(file_path)

    bands = [ds['Rw865'], ds['Rw655'], ds['Rw560'], ds['Rw480'], ds['Rw440']]
    band_labels = ['Rw865', 'Rw655', 'Rw560', 'Rw480', 'Rw440']
    reflectance_data_selections = []
    
    for i in range(len(bands)):
        if input_bands[i]:
            reflectance_data_selections.append((bands[i], band_labels[i]))

    # Get latitude and longitude arrays
    latitudes = ds['latitude'].values
    longitudes = ds['longitude'].values

    # Debug: Print input coordinates
    print("Input Longitudes (first 5):", longitudes.flatten()[:5])
    print("Input Latitudes (first 5):", latitudes.flatten()[:5])

    # Define UTM projection for Zone 23N
    in_proj = Proj('epsg:4326')  # WGS84
    out_proj = Proj(get_out_proj(longitudes, latitudes))  # UTM Zone set dynamically

    # Create a transformer
    transformer = Transformer.from_proj(in_proj, out_proj, always_xy=True)

    # Convert latitude and longitude to UTM
    utm_x, utm_y = transformer.transform(longitudes.flatten(), latitudes.flatten())
    
    # Reshape back to the original dimensions
    utm_x = utm_x.reshape(latitudes.shape)
    utm_y = utm_y.reshape(latitudes.shape)

    # Debug: Print transformed coordinates
    print("Transformed UTM X (first 5):", utm_x.flatten()[:5])
    print("Transformed UTM Y (first 5):", utm_y.flatten()[:5])

    # Define the pixel size based on Landsat 8 resolution (30m)
    pixel_size_x = 30
    pixel_size_y = 30

    # Set top-left corner of the raster
    top_left_x = utm_x[0, 0]  # X coordinate of the top-left corner
    top_left_y = utm_y[0, 0]  # Y coordinate of the top-left corner (max Y)

    # Create the transformation
    transform_geo = from_origin(top_left_x, top_left_y, pixel_size_x, pixel_size_y)

    # Create a new directory based on the original file name (without extension)
    output_subdir = Path(output_dir) / f"{Path(file_path).stem}"
    output_subdir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

    for reflectance_data, label in reflectance_data_selections:
        # Create a new output path for each band
        output_path = output_subdir / f"{Path(file_path).stem}_{label}.tif"

        # Save the reflectance data as a GeoTIFF
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=reflectance_data.shape[0],
            width=reflectance_data.shape[1],
            count=1,  # Number of bands
            dtype=reflectance_data.dtype,
            crs='EPSG:32623',  # Set the correct CRS for UTM Zone 23N
            transform=transform_geo,
        ) as dst:
            dst.write(reflectance_data.values, 1)  # Write data to the first band

if __name__ == "__main__":
    main()
