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
