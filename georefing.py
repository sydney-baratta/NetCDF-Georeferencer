import sys
import os
from pathlib import Path
import xarray as xr
import rasterio
from rasterio.transform import from_origin

def parse_bands(bands):
    return [bool(int(bit)) for bit in bands]

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

    # Define the transformation
    transform = from_origin(longitudes.min(), latitudes.max(), 30, 30)  # Adjust pixel size (30 here) as necessary

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
            height=reflectance_data.shape[0],  # Use height directly
            width=reflectance_data.shape[1],   # Use width directly
            count=1,  # Number of bands
            dtype=reflectance_data.dtype,
            crs='EPSG:4326',  # Set the correct CRS
            transform=transform,
        ) as dst:
            dst.write(reflectance_data.values, 1)  # Write data to the first band

if __name__ == "__main__":
    main()
