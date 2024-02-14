# perform_npm_build.py
import os
import subprocess
import shutil

from modules.custom_logger import setup_custom_logger
from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH, check_variable, get_nexus_url, file_exists

# Setup custom logger
logger = setup_custom_logger(__name__)


def set_node_environment(node_version: str):
    """
    Set the Node.js environment variables based on the NODE_VERSION.
    """
    # Set NODE_VERSION and NODE_HOME environment variables
    os.environ["NODE_VERSION"] = node_version
    os.environ["NODE_HOME"] = f"/opt/node/{node_version}"

    logger.info(f"Set NODE_VERSION to: {node_version}")
    logger.info(f"Set NODE_HOME to: {os.environ['NODE_HOME']}")


def create_tar_archive(repo_name: str, build_tag: str):
    """
    Create a TAR archive with REPO-NAME and BUILD_TAG combination.
    """
    tar_file = f"{repo_name}-{build_tag}.tar"
    shutil.make_archive(tar_file, "gztar", ".", build_tag)
    return tar_file


def perform_npm_build():
    """
    Perform npm and Node.js build and upload the artifact to Nexus.

    This function reads environment variables from the env.properties file,
    sets the Node.js environment variables based on the NODE_VERSION,
    installs npm dependencies, renames the build directory to BUILD_TAG,
    creates a TAR archive, and uploads it to Nexus using mvn deploy:file command.
    """
    try:
        logger.info("Performing npm and Node.js build and uploading artifact to Nexus")

        # Read environment variables from env.properties file
        env_variables = read_properties_file(PROPERTIES_FILE_PATH)

        # Get NPM_VERSION and NODE_VERSION from environment variables
        npm_version = env_variables.get("NPM_VERSION", "")
        check_variable(npm_version, "NPM_VERSION")
        node_version = env_variables.get("NODE_VERSION", "")
        check_variable(node_version, "NODE_VERSION")

        # Set Node.js environment variables
        set_node_environment(node_version)

        # Install npm dependencies
        subprocess.run(["npm", "install"], check=True)

        # Rename the build directory to BUILD_TAG
        build_tag = env_variables.get("BUILD_TAG", "")
        check_variable(build_tag, "BUILD_TAG")
        shutil.move("build", build_tag)

        # Create a TAR archive with REPO-NAME and BUILD_TAG combination
        repo_name = env_variables.get("REPO_NAME", "")
        check_variable(repo_name, "REPO_NAME")
        tar_file = create_tar_archive(repo_name, build_tag)

        # Determine the Nexus URL based on the branch name and build tag
        branch_name = env_variables.get("BRANCH_NAME", "")
        check_variable(branch_name, "BRANCH_NAME")
        nexus_url = get_nexus_url(branch_name, build_tag)

        # Upload the TAR file to Nexus using mvn deploy:file command
        subprocess.run(["mvn", "deploy:deploy-file", "-Dfile=" + tar_file, "-Durl=" + nexus_url], check=True)

        logger.info("npm and Node.js build completed successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred during npm and Node.js build: {e}")
        raise  # Re-raise the exception to propagate it further
