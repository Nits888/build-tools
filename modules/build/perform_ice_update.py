import json
from typing import Dict, Any
from modules.env_utils import read_properties_file
from modules.request_utils import call_api
from modules.custom_logger import setup_custom_logger

# Setup custom logger
logger = setup_custom_logger(__name__)


def read_json_with_placeholders(file_path: str) -> Dict[str, Any]:
    """Reads JSON file with placeholders."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def replace_placeholders(data: Dict[str, Any], env_variables: Dict[str, str]) -> Dict[str, Any]:
    """Replaces placeholders with actual values."""
    replaced_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            if value in env_variables:
                replaced_data[key] = env_variables[value]
            else:
                replaced_data[key] = value  # Placeholder not found in environment variables, keep it as is
        elif isinstance(value, dict):
            replaced_data[key] = replace_placeholders(value, env_variables)
        else:
            replaced_data[key] = value
    return replaced_data


def perform_ice_update(json_file_path: str, ice_api_url: str, properties_file_path: str) -> None:
    """Performs ICE update."""
    try:
        # Read environment variables from properties file
        env_variables = read_properties_file(properties_file_path)

        # Read JSON file with placeholders
        json_data = read_json_with_placeholders(json_file_path)

        # Replace placeholders with actual values
        updated_json_data = replace_placeholders(json_data, env_variables)

        # Call ICE API to update build information
        response = call_api(ice_api_url, method='POST', data=updated_json_data)

        if response.get('status_code') == 200:
            logger.info("ICE update successful")
        else:
            logger.error(f"Failed to update ICE: {response.get('text')}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.exception(f"An error occurred during ICE update: {e}")
        exit(1)


if __name__ == "__main__":
    # Define paths and URLs
    JSON_FILE_PATH = 'config/ice_schema.json'  # Path to your JSON file
    ICE_API_URL = 'https://example.com/api/update'
    PROPERTIES_FILE_PATH = 'env.properties'  # Path to properties file

    # Perform ICE update
    perform_ice_update(JSON_FILE_PATH, ICE_API_URL, PROPERTIES_FILE_PATH)
