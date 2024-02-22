import os
import json
import time
import requests

# Setup custom logger
logger = setup_custom_logger(__name__)

# Constants for Rundeck authentication
RUNDECK_USERNAME = os.getenv("RD_USR")
RUNDECK_PASSWORD = os.getenv("RD_PASS")
RUNDECK_URL = os.getenv("RUNDECK_URL")

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

def determine_deploy_type():
    """
    Determine the deploy type based on the presence of specific files in the workspace directory.
    You can customize this logic based on your project's requirements.
    """
    # Example: Check for the presence of pom.xml, package.json, etc.
    if os.path.exists("pom.xml"):
        return "maven"
    elif os.path.exists("package.json"):
        return "npm"
    else:
        return "tar"

def authenticate_with_rundeck(username, password, rundeck_url):
    """
    Authenticate with Rundeck and return the session object.
    """
    try:
        session = requests.Session()
        login_data = {
            "j_username": username,
            "j_password": password
        }
        response = session.post(f"{rundeck_url}/j_security_check", data=login_data)
        response.raise_for_status()
        return session
    except Exception as e:
        logger.error(f"Error authenticating with Rundeck: {e}")
        return None

def trigger_rundeck_job(session, job_id, argstring):
    """
    Trigger a Rundeck job with the provided job ID and arguments.
    """
    try:
        response = session.post(
            f"{RUNDECK_URL}/api/14/job/{job_id}/run",
            json={"argString": argstring},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        job_execution_id = response.json().get("id")
        return job_execution_id
    except Exception as e:
        logger.error(f"Error triggering Rundeck job: {e}")
        return None

def check_job_status(session, job_execution_id):
    """
    Check the status of a Rundeck job execution.
    """
    try:
        response = session.get(
            f"{RUNDECK_URL}/api/14/execution/{job_execution_id}",
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        job_status = response.json().get("status")
        return job_status
    except Exception as e:
        logger.error(f"Error checking job status: {e}")
        return None

def main():
    try:
        # Determine the deploy type based on the files in the workspace directory
        deploy_type = determine_deploy_type()

        # Load the JSON configuration file
        with open("path/to/config.json", "r") as json_file:
            config = json.load(json_file)

        # Get the nodes and job mappings for the deploy type
        deploy_config = config.get(deploy_type, {})
        if not deploy_config:
            logger.error("No configuration found for the deploy type.")
            return

        # Get the list of environments from the ENV_NAME variable
        env_names = os.getenv("ENV_NAME", "").split(",")

        # Authenticate with Rundeck
        session = authenticate_with_rundeck(RUNDECK_USERNAME, RUNDECK_PASSWORD, RUNDECK_URL)
        if not session:
            logger.error("Failed to authenticate with Rundeck.")
            return

        for env_name in env_names:
            env_config = deploy_config.get(env_name, {})
            if not env_config:
                logger.error(f"No configuration found for

def main():
    try:
        # Determine the deploy type based on the files in the workspace directory
        deploy_type = determine_deploy_type()

        # Load the JSON configuration file
        with open("path/to/config.json", "r") as json_file:
            config = json.load(json_file)

        # Get the nodes and job mappings for the deploy type
        deploy_config = config.get(deploy_type, {})
        if not deploy_config:
            logger.error("No configuration found for the deploy type.")
            return

        # Get the list of environments from the ENV_NAME variable
        env_names = os.getenv("ENV_NAME", "").split(",")

        # Authenticate with Rundeck
        session = authenticate_with_rundeck(RUNDECK_USERNAME, RUNDECK_PASSWORD, RUNDECK_URL)
        if not session:
            logger.error("Failed to authenticate with Rundeck.")
            return

        for env_name in env_names:
            env_config = deploy_config.get(env_name, {})
            if not env_config:
                logger.error(f"No configuration found for environment: {env_name}")
                continue

            nodes = env_config.get("nodes", [])
            job_name = env_config.get("job_name", "")

            # Construct the argstring with all nodes for the job
            argstring = ",".join([node["url"] for node in nodes])

            # Trigger the Rundeck job for the environment
            job_execution_id = trigger_rundeck_job(session, job_name, argstring)
            if not job_execution_id:
                logger.error(f"Failed to trigger job for environment: {env_name}")
                continue

            logger.info(f"Triggered Rundeck job '{job_name}' for environment '{env_name}'")

            # Check the status of the triggered job
            job_status = None
            timeout = 600  # Timeout in seconds (10 minutes)
            interval = 60   # Check status every 1 minute
            while timeout > 0:
                job_status = check_job_status(session, job_execution_id)
                if job_status in ["running", "scheduled"]:
                    logger.info(f"Job '{job_name}' in '{env_name}' is {job_status}, waiting...")
                    time.sleep(interval)
                    timeout -= interval
                elif job_status == "succeeded":
                    logger.info(f"Job '{job_name}' in '{env_name}' completed successfully.")
                    break
                else:
                    logger.error(f"Job '{job_name}' in '{env_name}' failed or terminated.")
                    break
            else:
                logger.error(f"Timeout exceeded while waiting for job '{job_name}' in '{env_name}'")

    except Exception as e:
        logger.exception(f"An error occurred during code deployment: {e}")
        exit(1)

if __name__ == "__main__":
    main()
