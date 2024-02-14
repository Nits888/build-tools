# request_utils.py
from modules.custom_logger import setup_custom_logger
import requests

# Setup custom logger
logger = setup_custom_logger(__name__)


def call_api(url, method='GET', params=None, data=None, headers=None):
    """
    Function to make an HTTP request to the specified URL using the given method.

    Args:
        url (str): The URL of the API endpoint.
        method (str): The HTTP method to use (GET, POST, PUT, DELETE). Defaults to 'GET'.
        params (dict): Optional dictionary of URL parameters.
        data (dict): Optional dictionary of data to send in the request body (for POST and PUT requests).
        headers (dict): Optional dictionary of request headers.

    Returns:
        dict: The JSON response received from the API, or None if an error occurs.
    """
    try:
        response = requests.request(method, url, params=params, data=data, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling API: {e}")
        return None
