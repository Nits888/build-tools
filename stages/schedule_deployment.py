import os
from datetime import datetime, timedelta

from modules.build_utils import check_build_type
from modules.custom_logger import setup_custom_logger
from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH, add_variables_to_properties_file
from modules.rundeck_utils import determine_rundeck_config

# Setup custom logger
logger = setup_custom_logger(__name__)


# Function to schedule deployment job in Rundeck
def schedule_deployment_job(rundeck_config, env_variables, deploy_delay, build_type):
    job_results = {}
    if "RUNDECK_JOB" in env_variables and "RUNDECK_NODES" in env_variables:
        job_name = env_variables["RUNDECK_JOB"]
        nodes = env_variables["RUNDECK_NODES"].split(',')
        job_results[''] = {"job_name": job_name, "nodes": [{"url": node, "token": ""} for node in nodes]}
    elif rundeck_config:
        deploy_time = datetime.now() + timedelta(hours=int(deploy_delay))
        for env_name, env_details in rundeck_config.items():
            nodes = env_details.get(build_type, {}).get("nodes", [])
            job_name = env_details.get(build_type, {}).get("job_name")
            job_params = {
                "BUILD_TAG": env_variables.get("BUILD_TAG", ""),
                "REPO_NAME": env_variables.get("REPO_NAME", ""),
                "AT": deploy_time.strftime("%Y-%m-%dT%H:%M:%S")
            }
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

        # Get deploy delay from environment variables
        deploy_delay = env_variables.get("DEPLOY_DELAY", "0")

        # Schedule deployment job for each environment specified in ENV_NAME
        job_results = schedule_deployment_job(rundeck_config, env_variables, deploy_delay, build_type)

        # Add Rundeck job IDs to the properties file
        add_variables_to_properties_file(job_results, PROPERTIES_FILE_PATH)

        logger.info("Code deployment scheduled successfully")

    except Exception as e:
        logger.exception(f"An error occurred during code deployment scheduling: {e}")
        exit(1)


if __name__ == "__main__":
    main()
