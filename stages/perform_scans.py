from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH, add_variables_to_properties_file
from modules.request_utils import call_api
from modules.custom_logger import setup_custom_logger

# Setup custom logger
logger = setup_custom_logger(__name__)


def perform_sast_scan(env_variables):
    # Perform SAST scan using relevant environment variables
    sast_url = env_variables.get("SAST_URL")
    sast_api_key = env_variables.get("SAST_API_KEY")
    if sast_url and sast_api_key:
        logger.info("Performing SAST scan...")
        response = call_api(sast_url, method='POST', headers={"Authorization": f"Bearer {sast_api_key}"})
        if response:
            # Process response and store scan results
            # Example:
            # sast_result = process_sast_scan_response(response)
            # return sast_result
            logger.info("SAST scan completed successfully")
            return response
        else:
            logger.error("Error performing SAST scan: No response received")
    else:
        logger.warning("SAST URL or API key not provided. Skipping SAST scan.")


def perform_dast_scan(env_variables):
    # Perform DAST scan using relevant environment variables
    dast_url = env_variables.get("DAST_URL")
    dast_api_key = env_variables.get("DAST_API_KEY")
    if dast_url and dast_api_key:
        logger.info("Performing DAST scan...")
        response = call_api(dast_url, method='POST', headers={"Authorization": f"Bearer {dast_api_key}"})
        if response:
            # Process response and store scan results
            # Example:
            # dast_result = process_dast_scan_response(response)
            # return dast_result
            logger.info("DAST scan completed successfully")
            return response
        else:
            logger.error("Error performing DAST scan: No response received")
    else:
        logger.warning("DAST URL or API key not provided. Skipping DAST scan.")


def perform_sonar_scan(env_variables):
    # Perform Sonar scan using relevant environment variables
    sonar_url = env_variables.get("SONAR_URL")
    sonar_api_key = env_variables.get("SONAR_API_KEY")
    if sonar_url and sonar_api_key:
        logger.info("Performing Sonar scan...")
        response = call_api(sonar_url, method='POST', headers={"Authorization": f"Bearer {sonar_api_key}"})
        if response:
            # Process response and store scan results
            # Example:
            # sonar_result = process_sonar_scan_response(response)
            # return sonar_result
            logger.info("Sonar scan completed successfully")
            return response
        else:
            logger.error("Error performing Sonar scan: No response received")
    else:
        logger.warning("Sonar URL or API key not provided. Skipping Sonar scan.")


def main(main_scan_type):
    try:
        # Read environment variables from env.properties file
        env_variables = read_properties_file(PROPERTIES_FILE_PATH)

        # Initialize scan result variables
        scan_functions = {
            "SAST": perform_sast_scan,
            "DAST": perform_dast_scan,
            "SONAR": perform_sonar_scan,
            "ALL": [perform_sast_scan, perform_dast_scan, perform_sonar_scan]
        }

        # Perform scans based on the specified type
        results = {}
        for scan_type, scan_function in scan_functions.items():
            if main_scan_type == scan_type or main_scan_type == "ALL":
                if isinstance(scan_function, list):
                    for func in scan_function:
                        results[scan_type.lower()] = func(env_variables)
                else:
                    results[scan_type.lower()] = scan_function(env_variables)

        # Add scan results to the properties file
        add_variables_to_properties_file(results, PROPERTIES_FILE_PATH)

        logger.info("Scans performed successfully")

    except Exception as e:
        logger.exception(f"An error occurred during scans: {e}")
        exit(1)
