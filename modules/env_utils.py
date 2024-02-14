# env_utils.py

import os
import subprocess
from modules.custom_logger import setup_custom_logger

# Setup custom logger
logger = setup_custom_logger(__name__)

# Define global constants
WORKSPACE_DIR = os.environ.get("WORKSPACE", "C:\\Temp")
PROPERTIES_FILE_NAME = "env.properties"
PROPERTIES_FILE_PATH = os.path.join(WORKSPACE_DIR, PROPERTIES_FILE_NAME)

FILES_TO_CONVERT = [
    os.path.join(WORKSPACE_DIR, "build-tools", "tools", "sonar", "conf", "sonar-scanner.properties"),
    os.path.join(WORKSPACE_DIR, "build-tools", "tools", "sonar", "bin", "sonar-scanner")
]

MINION_TOKEN_URL = 'https://example.com/getAuthToken'
GIT_BASE_URL = 'https://api.github.com/repos/your_org/your_repo'
JIRA_KEY_PATTERN = r'[A-Z]+-\d+'
NEXUS_URL = os.getenv("NEXUS_URL", "http://example.com/repository/")

# Rundeck Variables
RUNDECK_CONFIG = os.path.join(WORKSPACE_DIR, "config", "rundeck_config.json")
RUNDECK_DEPLOY_URL = 'https://rundeck.example.com/api/37/execution'
RUNDECK_SCHEDULE_URL = 'https://rundeck.example.com/api/37/execution'


def get_nexus_url(branch_name: str, build_tag: str) -> str:
    """Determines the Nexus URL based on branch name and build tag."""
    if branch_name == "master" and "REL" in build_tag:
        return f"{NEXUS_URL}maven-release"
    else:
        return f"{NEXUS_URL}maven-staging"


def write_properties_file(env_variables: dict, file_path: str) -> None:
    """Writes environment variables to a properties file."""
    try:
        with open(file_path, 'w') as file:
            for key, value in env_variables.items():
                file.write(f"{key}={value}\n")
        logger.info("Environment variables written to file successfully")
    except Exception as e:
        logger.error(f"Error writing environment variables to file: {e}")
        raise


def run_dos2unix(file_path: str) -> None:
    """Runs the dos2unix command on the specified file."""
    try:
        subprocess.run(["dos2unix", file_path])
        logger.info(f"Converted file '{file_path}' to Unix format")
    except Exception as e:
        logger.error(f"Error converting file '{file_path}' to Unix format: {e}")
        raise


def check_variable(variable, name):
    """
    Check if a variable is valid.

    Args:
        variable: The variable to check.
        name (str): The name of the variable (for logging purposes).

    Raises:
        ValueError: If the variable is None, blank, or null.
        ValueError: If the variable does not contain valid values (for ENV_NAME).
    """
    # Check if the variable is None, blank, or null
    if variable is None or variable.strip() == "":
        raise ValueError(f"{name} is not set or is blank")

    # Check if the variable is ENV_NAME and contains valid values
    if name == "ENV_NAME":
        valid_values = {"DEV", "UAT", "UAT1"}
        values = variable.split(",")
        if not all(value in valid_values for value in values):
            raise ValueError(f"{name} does not contain valid values")


# env_utils.py

def add_variables_to_properties_file(variables, file_path):
    """
    Add or update variables in the environment properties file.

    Args:
        variables (dict): A dictionary containing the variables to be added or updated.
        file_path (str): The path to the properties file.
    """
    try:
        # Read existing variables from the properties file
        existing_variables = read_properties_file(file_path)

        # Update existing variables with new values
        existing_variables.update(variables)

        # Write updated variables to the properties file
        with open(file_path, 'w') as file:
            for key, value in existing_variables.items():
                file.write(f"{key}={value}\n")

        logger.info("Variables added or updated in environment properties file successfully")
    except Exception as e:
        logger.error(f"Error adding or updating variables in environment properties file: {e}")


def read_properties_file(file_path):
    """
    Read environment variables from a properties file.

    Args:
        file_path (str): The path to the properties file.

    Returns:
        dict: A dictionary containing the environment variables read from the file.
    """
    env_variables = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env_variables[key.strip()] = value.strip()
        logger.info("Environment variables read from file successfully")
    except Exception as e:
        logger.error(f"Error reading environment variables from file: {e}")
        raise  # Raise exception to indicate failure
    return env_variables


def file_exists(file_path: str) -> bool:
    """Check if the specified file exists."""
    return os.path.isfile(file_path)
