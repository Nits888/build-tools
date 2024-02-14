# build_utils.py

import os
from modules.custom_logger import setup_custom_logger

from modules.build.perform_maven_build import perform_maven_build
from modules.build.perform_npm_build import perform_npm_build
from modules.build.perform_docker_build import perform_docker_build
from modules.build.perform_tar_build import perform_tar_build

# Setup custom logger
logger = setup_custom_logger(__name__)

# Map file patterns to build functions
build_mapping = {
    ("pom.xml", "Dockerfile"): perform_maven_build,
    ("package.json", "Dockerfile"): perform_npm_build,
    ("pom.xml",): perform_maven_build,
    ("package.json",): perform_npm_build,
    ("Dockerfile",): perform_docker_build,
    (): perform_tar_build,
}


def check_build_type(workspace_dir: str):
    """Checks the build type based on files in the Jenkins Workspace."""
    present_files = set(os.listdir(workspace_dir))

    for fileset, build_function in build_mapping.items():
        if all(file in present_files for file in fileset):
            return build_function  # Return the function object directly

    logger.info("No matching build type detected in the workspace directory. Defaulting to 'tar' build.")
    return perform_tar_build  # Return the default build function
