# perform_code_build.py

from modules.env_utils import (read_properties_file, PROPERTIES_FILE_PATH, WORKSPACE_DIR,
                               add_variables_to_properties_file)
from modules.custom_logger import setup_custom_logger
from modules.build_utils import check_build_type

# Setup custom logger
logger = setup_custom_logger(__name__)


def main():
    try:
        # Read environment variables from env.properties file
        env_variables = read_properties_file(PROPERTIES_FILE_PATH)

        # Explicitly assign required variables
        branch_name = env_variables.get("BRANCH_NAME", "")
        build_tag = env_variables.get("BUILD_TAG", "")

        # Check the type of build based on the files in the root folder
        build_function = check_build_type(WORKSPACE_DIR)

        if build_function is not None:
            build_function(branch_name, build_tag)  # Pass required variables explicitly

            # Pass required variables explicitly
            # Update properties file with new values
            env_variables["BRANCH_NAME"] = branch_name
            env_variables["BUILD_TAG"] = build_tag
            add_variables_to_properties_file(env_variables, PROPERTIES_FILE_PATH)
        else:
            raise ValueError("Unknown build type detected")

        logger.info("Code build process completed successfully")

    except Exception as e:
        logger.exception(f"An error occurred during code build: {e}")
        exit_code = 1
        exit(exit_code)


if __name__ == "__main__":
    main()
