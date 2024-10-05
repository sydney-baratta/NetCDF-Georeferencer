import sys
import os
from pathlib import Path
import xarray as xr
import rasterio
from rasterio.transform import from_origin  # Importing from_origin

if len(sys.argv) < 3:
    print("Error: invalid arguments #")
    sys.exit(1)

# Load the NetCDF file
file_path = sys.argv[1]
output_dir = sys.argv[2]
output_path = Path(output_dir) / f"{Path(file_path).stem}{".tif"}"

ds = xr.open_dataset(file_path)

# Print the dataset information
print(ds)

# Select the reflectance variable you want to save
reflectance_data = ds['Rw440']  # Change this to your desired reflectance variable

# Get latitude and longitude arrays
latitudes = ds['latitude'].values
longitudes = ds['longitude'].values

# Define the transformation
transform = from_origin(longitudes.min(), latitudes.max(), 30, 30)  # Adjust pixel size (30 here) as necessary

# Save the reflectance data as a GeoTIFF
with rasterio.open(
    output_path,
    'w',
    driver='GTiff',
    height=reflectance_data.shape[0],  # Use height directly
    width=reflectance_data.shape[1],   # Use width directly
    count=1,  # Number of bands
    dtype=reflectance_data.dtype,
    crs='EPSG:4326',  # Set the correct CRS
    transform=transform,
) as dst:
    dst.write(reflectance_data.values, 1)  # Write data to the first band
