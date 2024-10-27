# georefing.py

## **Overview**
`georefing.py` is a Python script designed to georeference netCDF files containing reflectance data, regardless of the UTM zone, particularly designed to work with [Polymer outputs](https://github.com/hygeos/polymer). This script uses python libraries: `xarray`, `rasterio`, `numpy`, and `pyproj` to convert geographical coordinates from individual netCDF layers into UTM projection, creating georeferenced GeoTIFF files for specified bands (RW: 440, 480, 560, 655, and 865).

## **Features**
- Georeferences netCDF files containing reflectance data of various wavelengths/bands.
- Dynamically determines the appropriate UTM zone based on the mean longitude of the input netCDF.
- Supports selecting specific bands for georeferencing (using a binary string input *"XXXXX"*).
- Outputs GeoTIFF files organized into a specified directory.

## **Requirements**
- Python 3.12 (or the latest version) 

- Required Python packages:

  - `xarray`
  - `rasterio`
  - `numpy`
  - `pyproj`

You can install the required packages using pip:

```bash
pip install xarray rasterio numpy pyproj
```

## **Usage**
To use this code, navigate to the root directory of the repository and run the script:

```bash
./run_geo.sh <optional_debugging> <input_nc_file> <output_directory> <band_selection>
```

***Where***,
1) **Optional Debugging (`-d`)**: Use this if you want to see debugging printouts. This argument is optional!

2) **Input netCDF File**: Specify the .nc file to be georeferenced - *either relative or absolute paths*.

3) **Output Directory**: Specify the name of the directory in which the georeferenced .tif files will be placed. If a directory has been specified but doesn't exist, it will be created.

4) **Band Selection**:  Use a binary string to indicate which bands need to be georeferenced, in order from largest band to smallest. For example, a band code of 11001 will georeference bands RW865, RW655, and RW440.

### Example Command

```bash
./run_geo.sh -d example_nc_file.nc ../georeferenced_files 10101
```

This command takes `example_nc_file.nc`, georeferences bands RW865, RW560, and RW440, and saves the outputs in the `georeferenced_files` directory (one level above the current directory).

## **Code Structure**
Here are the main functions of the script and what they do:

- **parse_bands(bands)**: Converts a binary string into a list of boolean values that indicate which bands to process.

- **get_out_proj(longitudes, latitudes)**: Determines the UTM projection using the mean longitude and latitude of the input data.

- **debug_print(*args, kwargs)**: Outputs debug messages with timestamps to track down any errors.

- **main()**: The main function that loads the input imagery, selects the desired bands, transforms the coordinates, and saves the output as GeoTIFF files.
 

## Contact
 For any questions or suggestions, you can reach out to me at `sydney.j.baratta@usace.army.mil` or `sydney.baratta@maine.edu`. 

Happy imagery processing!!