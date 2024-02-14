# perform_maven_build.py

import os
import subprocess

from modules.custom_logger import setup_custom_logger
from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH, get_nexus_url, file_exists, check_variable

# Setup custom logger
logger = setup_custom_logger(__name__)


def set_java_home(java_version: str):
    """
    Set the JAVA_HOME environment variable based on the JAVA_VERSION.
    """
    # Check if the JDK directory exists
    if file_exists(java_version):
        os.environ["JAVA_HOME"] = java_version
        logger.info(f"Set JAVA_HOME to: {java_version}")
    else:
        raise FileNotFoundError(f"JAVA_HOME directory not found: {java_version}")


def perform_maven_build(branch_name, build_tag):
    """
    Perform Maven build and upload the artifact to Nexus.

    This function reads environment variables from the env.properties file,
    determines the Nexus URL based on the branch name and build tag, sets the
    JAVA_HOME environment variable based on the JAVA_VERSION, and executes
    the Maven build command using the configured Maven executable.

    Args:
    - branch_name (str): The name of the branch.
    - build_tag (str): The build tag.

    Returns:
    - None
    """
    try:
        logger.info("Performing Maven build and uploading artifact to Nexus")

        # Read environment variables from env.properties file
        env_variables = read_properties_file(PROPERTIES_FILE_PATH)

        # Get JAVA_VERSION from environment variables
        java_version = os.environ.get("JAVA_VERSION")
        check_variable(java_version, "JAVA_VERSION")

        # Set JAVA_HOME based on JAVA_VERSION
        set_java_home(java_version)

        # Determine the Nexus URL based on the branch name and build tag
        nexus_url = get_nexus_url(branch_name, build_tag)

        # Determine the Maven executable path from MVNRUN environment variable
        maven_executable = os.environ.get("MVNRUN", "mvn")

        # Check if the Maven executable exists
        if not file_exists(maven_executable):
            raise FileNotFoundError(f"Maven executable not found at: {maven_executable}")

        # Determine the Maven command
        maven_command = [maven_executable, "versions:set", "-DnewVersion=" + build_tag]
        if os.path.exists("assembly.xml"):
            maven_command.extend(["clean", "package", "assembly:single"])
        else:
            maven_command.extend(["clean", "package", "deploy"])

        # Set the overridden Nexus URL for the Maven build
        os.environ["MAVEN_OPTS"] = "-DaltDeploymentRepository=releases::default::" + nexus_url

        # Execute Maven build using the configured Maven executable
        subprocess.run(maven_command, check=True)

        logger.info("Maven build completed successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred during Maven build: {e}")
        raise  # Re-raise the exception to propagate it further

