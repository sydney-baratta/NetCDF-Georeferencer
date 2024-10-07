import sys
import datetime
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

def debug_print(*args, **kwargs):
    # Get the current time
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    # Print with the timestamp
    print(f"[{current_time}] ", end='')  # Add timestamp
    print(*args, **kwargs)  # Print the original message
    

def main():
    debug = False
    # Check for the -d flag
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        print(('*' * 40) + '\nDEBUG ENABLED\n' + ('*' * 40))
        debug = True
        sys.argv.pop(1)  # Remove the -d flag from the arguments

    if len(sys.argv) < 4:
        debug_print("Error: invalid arguments #")
        sys.exit(1)

    # Load the NetCDF file
    file_path = sys.argv[1]
    output_dir = sys.argv[2]
    input_bands = parse_bands(sys.argv[3])
    if debug:
        debug_print('Input file path: ' + file_path)
        debug_print('Output Directory path: ' + output_dir)

    ds = xr.open_dataset(file_path)
    if debug:
        debug_print('Dataset opened successfully')

    bands = [ds['Rw865'], ds['Rw655'], ds['Rw560'], ds['Rw480'], ds['Rw440']]
    band_labels = ['Rw865', 'Rw655', 'Rw560', 'Rw480', 'Rw440']
    reflectance_data_selections = []
    
    for i in range(len(bands)):
        if input_bands[i]:
            reflectance_data_selections.append((bands[i], band_labels[i]))
    if debug:
        selected_bands = [band_labels[i] for i in range(len(bands)) if input_bands[i]]
        debug_print('Bands selected: ' + str(selected_bands))

    # Get latitude and longitude arrays
    latitudes = ds['latitude'].values
    longitudes = ds['longitude'].values
    if debug:
        if latitudes is not None:
            debug_print('Latitudes retrieved successfully')
        if longitudes is not None:
            debug_print('Longitudes retrieved successfully')

    # Define UTM projection for Zone 23N
    in_proj = Proj('epsg:4326')  # WGS84
    out_proj_code = get_out_proj(longitudes, latitudes)
    out_proj = Proj(out_proj_code)  # UTM Zone set dynamically
    if debug:
        debug_print('in_proj set to WGS84')
        debug_print('out_proj set to ' + out_proj_code)

    # Create a transformer
    transformer = Transformer.from_proj(in_proj, out_proj, always_xy=True)

    # Convert latitude and longitude to UTM
    utm_x, utm_y = transformer.transform(longitudes.flatten(), latitudes.flatten())
    if debug:
        debug_print('Latitudes and longitudes successfully converted to UTM')
    
    # Reshape back to the original dimensions
    utm_x = utm_x.reshape(latitudes.shape)
    utm_y = utm_y.reshape(latitudes.shape)
    if debug:
        debug_print('Latitudes and longitudes successfully reshaped to original dimensions')

    # Define the pixel size based on Landsat 8 resolution (30m)
    pixel_size_x = 30
    pixel_size_y = 30

    # Set top-left corner of the raster
    top_left_x = utm_x[0, 0]  # X coordinate of the top-left corner 
    top_left_y = utm_y[0, 0]  # Y coordinate of the top-left corner (max Y)
    if debug:
        debug_print('Origin set to (' + str(top_left_x) + ', ' + str(top_left_y) + ')')

    # Create the transformation
    transform_geo = from_origin(top_left_x, top_left_y, pixel_size_x, pixel_size_y)
    if debug:
        debug_print('Geo transformation successfully generated')

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
            crs=out_proj_code.upper(),  # Set the correct CRS for UTM Zone 23N
            transform=transform_geo,
        ) as dst:
            dst.write(reflectance_data.values, 1)  # Write data to the first band
            if debug:
                debug_print(label + ' band data successfully written to file')

if __name__ == "__main__":
    main()
