# perform_docker_build.py
import shutil
import subprocess
from modules.custom_logger import setup_custom_logger
from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH, check_variable, get_nexus_url

# Setup custom logger
logger = setup_custom_logger(__name__)


def perform_docker_build():
    """
    Build a Docker image using Buildah, install RHEL 8 Minimal,
    add the required code and libraries using a Dockerfile,
    and commit the image to the Nexus repository.
    """
    try:
        logger.info("Building Docker image and committing to Nexus repository")

        # Read environment variables from env.properties file
        env_variables = read_properties_file(PROPERTIES_FILE_PATH)

        # Determine the Nexus URL based on the branch name and build tag
        branch_name = env_variables.get("BRANCH_NAME", "")
        check_variable(branch_name, "BRANCH_NAME")
        build_tag = env_variables.get("BUILD_TAG", "")
        check_variable(build_tag, "BUILD_TAG")
        nexus_url = get_nexus_url(branch_name, build_tag)

        # Build Docker image using Buildah
        subprocess.run(["buildah", "from", "rhel8-minimal"], check=True)

        # Run commands to set up the Docker image
        subprocess.run(["buildah", "run", "rhel8-minimal", "yum", "-y", "install", "required_packages"], check=True)

        # Copy the required code and libraries using a Dockerfile
        shutil.copy("Dockerfile", "docker_build")
        subprocess.run(["buildah", "commit", "--format", "docker", "rhel8-minimal", f"{nexus_url}/{build_tag}"],
                       check=True)

        logger.info("Docker image built and committed to Nexus repository successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred during Docker image build and commit: {e}")
        raise  # Re-raise the exception to propagate it further
