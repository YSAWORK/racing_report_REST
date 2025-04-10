# Monaco Racing Report

This project provides an API to generate a racing report for the Monaco Grand Prix (2018). It processes data from log files and generates a structured report containing driver information, race results, and any errors encountered during data processing.

# How it Works
## 1. Data Processing:
The application reads the following log files:<br>
+ log_data/abbreviations.txt: Contains driver abbreviations and their team names.<br>
+ log_data/start.log: Contains timestamps for when each driver starts their race.<br>
+ log_data/end.log: Contains timestamps for when each driver finishes their race.<br>

The bild_report.py file processes this data and calculates each driver's total time (end time - start time). It also handles errors, such as incorrect data formats or missing information.

## 2. API Endpoints:
The API exposes the following endpoints:
+ GET /api/{version}/report: Retrieves the full race report.
+ GET /api/{version}/drivers: Retrieves a list of all drivers and their race results.
+ GET /api/{version}/drivers/<driver_id>: Retrieves detailed information about a specific driver by their abbreviation.

The format of the response can be controlled via the format query parameter. By default, the response is returned in JSON format. To get XML, use the following query string: ?format=xml.

## 3. Error Handling:
The application checks for data errors, such as incorrect time formats or missing data. These errors are returned in the response, allowing users to identify issues with the source data.

## 4. Swagger API Documentation:
Swagger is integrated to provide interactive API documentation. You can view and test the API directly through the /swagger endpoint.

## 5. Usage
##### Run the Flask application:
```$ python racing_report/main_public.py```

##### Open a browser or API client (like Postman) and visit the endpoints:
+ ```.../api/{version}/report```
+ ```.../api/{version}/drivers```
+ ```.../api/{version}/drivers/{driver_id}```

## 6. Swagger Documentation: 
Visit .../apidocs to explore the API documentation and interact with the endpoints.

## 7. Example
#### To get the race results of all drivers in XML format:
```.../api/v1/drivers?format=xml```

#### To get the result of a specific driver:
```.../api/v1/drivers/ALO```

## 8. Configuration
Configuration options are stored in the `config_fldr/config.py` file. You can modify the following settings:

BASE_DIR: The base directory of the project.
+ version: The API version (e.g., v1).
+ debug: Whether to run the app in debug mode.
+ passthrough_errors: Whether to pass through errors or not.
+ use_debugger: Whether to use the Flask debugger.
+ use_reloader: Whether to use the Flask reloader.

## 9. Requirements
The requirements.txt file contains a list of required Python packages that the project depends on.

## 10. Contributing
If you'd like to contribute to this project, feel free to fork the repository, create a new branch, and submit a pull request with your changes. Be sure to write tests for any new functionality and ensure existing tests pass before submitting.

## 11. License
This project is licensed under the MIT License - see the LICENSE file for details.