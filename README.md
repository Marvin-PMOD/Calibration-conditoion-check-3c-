# Calibration-conditoion-check-3c-
ancillary data for IPc calibration check website


README for 12957file_interpreter to image_name.py
# 12957file_interpreter to image_name.py

## Overview
This script is designed to interpret and process files from the IRCCAM camera system, specifically those with the `.12957` extension. These files contain image and metadata that need to be extracted and converted into a usable image format (e.g., PNG). The script also performs further processing such as logging information about the files and handling the detection of valid image keys.

## Main Functionalities
1. **Reading and parsing `.12957` files**: The script loads the files, extracts metadata, and reads the image data.
2. **Image extraction and decoding**: Once the correct key within the file is identified, the script decodes the image data.
3. **Image saving**: The script converts the raw image data to a human-readable format (e.g., PNG) for further analysis or viewing.
4. **Logging and error handling**: The script logs errors, unavailable image keys, and other important operations for future review.

## Key Functions

### 1. `find_highest_key(mat_data)`
This function is responsible for extracting all image keys from the `.12957` file. The keys follow the pattern `img_HHMMSS` where `HH` is the hour, `MM` is the minute, and `SS` is the second of the timestamp.
- **Input**: 
  - `mat_data`: The loaded data from the `.12957` file.
- **Output**: 
  - The function returns the highest key available in the file. If no valid keys are found, it returns `None`.

### 2. `process_images(image_directory)`
This is the main function that processes all the `.12957` files in a given directory. It identifies the latest file, extracts the necessary image data, and saves the image in PNG format.
- **Input**: 
  - `image_directory`: The directory containing `.12957` files.
- **Output**: 
  - Processes the latest file, extracts the image, and logs its progress.

## Usage Instructions
1. Ensure that all `.12957` files are stored in the specified directory.
2. Update the script's paths, such as `image_directory`, to point to your folder with `.12957` files.
3. Run the script as follows:

```bash
python 12957file_interpreter_to_image_name.py

Prerequisites
Python 3.x
Required libraries:
numpy
opencv-python
scipy
pip install numpy opencv-python scipy

Additional Notes
If the image key is not found in the file, the script will attempt to find the next available key. If no key is available, it will log the issue for further analysis.




---

### README for `aod2.py`

```markdown
# aod2.py

## Overview
This script processes Aerosol Optical Depth (AOD) data, integrates it with IRCCAM image data, and stores the combined result in a MySQL database. Aerosol Optical Depth is a measure of the amount of aerosols (tiny particles like dust, smoke, and pollution) in the atmosphere, which affects the clarity of the sky.

## Main Functionalities
1. **AOD Calculation**: The script calculates the AOD based on environmental and image data.
2. **Integration with IRCCAM data**: It merges the calculated AOD data with IRCCAM image data for better analysis.
3. **Data storage**: The script stores the processed data in a MySQL database for future reference and analysis.

## Key Functions

### 1. `calculate_aod(...)`
This function computes the Aerosol Optical Depth (AOD) using atmospheric data and IRCCAM image inputs.
- **Input**: Various environmental and image data.
- **Output**: Returns the computed AOD value.

### 2. `integrate_aod_with_image_data(...)`
This function combines the AOD values with the metadata and image data from the IRCCAM system, allowing cross-analysis.
- **Input**: Image and metadata along with computed AOD.
- **Output**: Stores the integrated data in the MySQL database.

## Usage Instructions
1. Ensure the required environmental and IRCCAM data are available.
2. Update the script with your MySQL database credentials.
3. Run the script using:

```bash
python aod2.py
Prerequisites
Python 3.x
Required libraries:
numpy
mysql-connector-python
pip install numpy mysql-connector-python

Additional Notes
The script can handle large datasets and ensures that the combined AOD and image data are correctly stored in the MySQL database.
Make sure the database is correctly set up to handle the incoming data, including necessary fields for storing AOD and image metadata.



---

### README for `irccam_12957_cloudettection_with_log.py`

```markdown
# irccam_12957_cloudettection_with_log.py

## Overview
This script performs cloud detection on IRCCAM image data. It reads the `.12957` files, processes the images to detect clouds, and logs the results. Additionally, the script calculates the sun's position based on the timestamp in the image data, and it stores the results (including sun position, cloud detection status, and the image itself) in a MySQL database.

## Main Functionalities
1. **Cloud Detection**: Identifies cloud clusters in the IRCCAM image using thresholding and contour detection techniques.
2. **Sun Position Calculation**: Computes the sun's azimuth and elevation for a given timestamp and geographic location.
3. **Data Logging**: Stores the processed results, including the cloud detection status, sun position, and image data in the MySQL database.

## Key Functions

### 1. `detect_cloud_clusters(image_data)`
This function performs cloud detection using basic image processing techniques like thresholding and contour detection.
- **Input**: 
  - `image_data`: Raw image data from the `.12957` file.
- **Output**: 
  - A list of cloud clusters identified in the image.

### 2. `calculate_sun_position(timestamp, latitude, longitude)`
This function calculates the position of the sun (azimuth and elevation) based on the geographic location and timestamp of the image.
- **Input**: 
  - `timestamp`: The timestamp of the image.
  - `latitude` and `longitude`: The geographic coordinates of the camera.
- **Output**: 
  - The azimuth and elevation of the sun.

## Usage Instructions
1. Ensure you have the `.12957` files and the MySQL database configured.
2. Update the `config.ini` file with your MySQL database credentials.
3. Run the script as follows:

```bash

The script will process the latest .12957 file, detect clouds, calculate the sun's position, and store the data in the MySQL database.


Prerequisites
Python 3.x
numpy
opencv-python
pysolar
mysql-connector-python
pip install numpy opencv-python pysolar mysql-connector-python

Additional Notes
Ensure that the MySQL database has appropriate fields for storing sun position, cloud detection status, and image data.
The script also handles errors and logs important events, making it easier to debug issues with file loading or database storage.



---

### README for `wind_data.py`

```markdown
# wind_data.py

## Overview
This script processes wind data files, extracts information about wind speed and direction, and stores the results in a MySQL database. The script allows you to analyze wind data in relation to other environmental data such as IRCCAM cloud detection.

## Main Functionalities
1. **Wind Data Processing**: Reads the wind data file, processes wind speed and direction, and prepares it for analysis.
2. **Data Storage**: Saves the wind data into a MySQL database, enabling integration with other datasets like IRCCAM image data.
3. **Data Handling and Logging**: Handles errors in the data processing pipeline and logs important steps for future reference.

## Key Functions

### 1. `process_wind_data(wind_file)`
This function reads the wind data from a specified file and processes it to extract wind speed and direction.
- **Input**: 
  - `wind_file`: The file containing wind data.
- **Output**: 
  - Returns processed wind data ready for storage in the database.

### 2. `store_wind_data_in_database(...)`
This function connects to a MySQL database and stores the processed wind data for further analysis.
- **Input**: 
  - Processed wind data.
- **Output**: 
  - Wind data is stored in the MySQL database, where it can be accessed and analyzed alongside other environmental data.

## Key Functions (continued)

### 2. `store_wind_data_in_database(wind_data, config_file)`
This function handles the connection to the MySQL database and stores the wind data.
- **Input**: 
  - `wind_data`: A dictionary or structured data that contains wind speed, direction, and timestamp information.
  - `config_file`: A configuration file (`config.ini`) containing database credentials.
- **Output**: 
  - Inserts the processed wind data into the appropriate table in the MySQL database.


Prerequisites
Python 3.x
Required Libraries:
mysql-connector-python
numpy
pip install mysql-connector-python numpy

Additional Notes
Make sure the wind data file is formatted correctly and contains the required fields (e.g., wind speed, wind direction, or U and V components).
Ensure that the database table for storing wind data exists and that it has the correct schema for storing the timestamp, wind speed, and wind direction.
The script logs each step, so you can track its progress and debug issues if the wind data or database connection fails.
