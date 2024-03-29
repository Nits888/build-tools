import os

from modules.build_utils import check_build_type
from modules.custom_logger import setup_custom_logger
from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH, add_variables_to_properties_file
from modules.rundeck_utils import determine_rundeck_config

# Setup custom logger
logger = setup_custom_logger(__name__)


# Function to trigger deployment job in Rundeck
def trigger_deployment_job(rundeck_config, env_variables, build_type):
    job_results = {}
    if "RUNDECK_JOB" in env_variables and "RUNDECK_NODES" in env_variables:
        job_name = env_variables["RUNDECK_JOB"]
        nodes = env_variables["RUNDECK_NODES"].split(',')
        job_results[''] = {"job_name": job_name, "nodes": [{"url": node, "token": ""} for node in nodes]}
    elif rundeck_config:
        for env_name, env_details in rundeck_config.items():
            if env_name in env_variables.get("ENV_NAME", ""):
                nodes = env_details.get(build_type, {}).get("nodes", [])
                job_name = env_details.get(build_type, {}).get("job_name")
                job_results[env_name] = {"job_name": job_name, "nodes": nodes}
    else:
        raise ValueError("No Rundeck configuration found.")
    return job_results


# Main function
def main():
    job_results = {}  # Initialize job_results as an empty dictionary
    try:
        # Read environment variables from env.properties file
        env_variables = read_properties_file(PROPERTIES_FILE_PATH)

        # Determine build type dynamically
        build_type = check_build_type(os.getcwd())

        # Determine Rundeck configuration based on project or environment variables
        rundeck_config = determine_rundeck_config(env_variables)

        # Trigger deployment job for each environment specified in ENV_NAME
        job_results = trigger_deployment_job(rundeck_config, env_variables, build_type)

        # Add Rundeck job IDs to the properties file
        add_variables_to_properties_file(job_results, PROPERTIES_FILE_PATH)

        logger.info("Code deployment process completed successfully")

    except Exception as e:
        logger.exception(f"An error occurred during code deployment: {e}")
        exit(1)


if __name__ == "__main__":
    main()
