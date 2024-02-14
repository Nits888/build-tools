# perform_tar_build.py
import os
import subprocess
import shutil

from modules.custom_logger import setup_custom_logger
from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH, check_variable

# Setup custom logger
logger = setup_custom_logger(__name__)


def create_tar_archive(workspace_dir: str, repo_name: str, build_tag: str):
    """
    Create a TAR archive of all files under WORKSPACE and rename it as REPO-NAME and BUILD_TAG combination.
    """
    tar_file = f"{repo_name}-{build_tag}.tar"
    shutil.make_archive(tar_file, "gztar", workspace_dir)
    return tar_file


def perform_tar_build():
    """
    Create a TAR archive of all files under WORKSPACE and upload the TAR file to Nexus.

    This function reads environment variables from the env.properties file,
    creates a TAR archive with the combination of REPO_NAME and BUILD_TAG,
    and uploads the TAR file to Nexus using the mvn deploy:file command.
    """
    try:
        logger.info("Creating TAR archive of Jenkins Workspace and uploading to Nexus")

        # Read environment variables from env.properties file
        env_variables = read_properties_file(PROPERTIES_FILE_PATH)

        # Get WORKSPACE_DIR, REPO_NAME, and BUILD_TAG from environment variables
        workspace_dir = env_variables.get("WORKSPACE_DIR", "")
        check_variable(workspace_dir, "WORKSPACE_DIR")
        repo_name = env_variables.get("REPO_NAME", "")
        check_variable(repo_name, "REPO_NAME")
        build_tag = env_variables.get("BUILD_TAG", "")
        check_variable(build_tag, "BUILD_TAG")

        # Create a TAR archive of all files under WORKSPACE
        tar_file = create_tar_archive(workspace_dir, repo_name, build_tag)

        # Upload the TAR file to Nexus using mvn deploy:file command
        subprocess.run(["mvn", "deploy:deploy-file", "-Dfile=" + tar_file, "-Durl=nexus_url"], check=True)

        logger.info("TAR archive creation and upload completed successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred during TAR archive creation and upload: {e}")
        raise  # Re-raise the exception to propagate it further
