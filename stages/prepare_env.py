# prepare_env.py

from modules.env_utils import PROPERTIES_FILE_PATH, run_dos2unix, FILES_TO_CONVERT, \
    check_variable, MINION_TOKEN_URL, add_variables_to_properties_file, GIT_BASE_URL, JIRA_KEY_PATTERN
from modules.request_utils import call_api
from modules.custom_logger import setup_custom_logger
import os
import re

# Setup custom logger
logger = setup_custom_logger(__name__)


def get_minion_auth_token():
    """Fetches the Minion Auth Token."""
    minion_token = os.environ.get("MINION_TOKEN")
    check_variable(minion_token, "MINION_TOKEN")
    headers = {'x-api-key': minion_token}
    response = call_api(MINION_TOKEN_URL, headers=headers)
    if response:
        return response.get('token')  # Assuming 'token' in the response
    else:
        raise Exception("Failed to fetch Minion Auth Token")


def fetch_git_info():
    """Fetches pull request and release information from the GitHub API."""
    git_headers = {'Authorization': 'Bearer YOUR_GIT_TOKEN'}  # Replace YOUR_GIT_TOKEN

    pr_url = f"{GIT_BASE_URL}/pulls?sort=created&direction=desc"
    pr_response = call_api(pr_url, headers=git_headers)
    if pr_response and pr_response[0].get('number'):
        git_pull_request = pr_response[0]['number']
    else:
        raise Exception("Failed to fetch Git pull request")

    release_url = f"{GIT_BASE_URL}/releases/latest"
    release_response = call_api(release_url, headers=git_headers)
    if release_response and release_response.get('tag_name'):
        git_release_version = release_response['tag_name']
    else:
        raise Exception("Failed to fetch Git release version")

    return git_pull_request, git_release_version


def main():
    """Orchestrates the environment preparation steps."""
    exit_code = 0  # Default to success

    try:
        # 1. Write environment variables to file
        # write_properties_file(dict(os.environ), PROPERTIES_FILE_PATH)

        # 2. Log Jenkins Build Information
        build_info = {
            "JOB_BASE_NAME": os.environ.get("JOB_BASE_NAME"),
            "BUILD_USER_ID": os.environ.get("BUILD_USER_ID"),
            "BUILD_USER": os.environ.get("BUILD_USER"),
            "BUILD_USER_EMAIL": os.environ.get("BUILD_USER_EMAIL"),
            "BUILD_TAG": os.environ.get("BUILD_TAG"),
        }
        logger.info("########## Build Information ##########")
        for key, value in build_info.items():
            logger.info(f"{key}: {value}")

        # 3. Run dos2unix on specific files
        logger.info("########## ENABLE DOS2UNIX Commands - Currently Disabled #######")
        for file_path in FILES_TO_CONVERT:
            logger.info("Converting File to UNIX Format : %s", file_path)
            run_dos2unix(file_path)

        # 4. Validation: Basic Checks
        env_name = os.environ.get("ENV_NAME")
        branch_name = os.environ.get("BRANCH_NAME")
        check_variable(env_name, "ENV_NAME")
        check_variable(branch_name, "BRANCH_NAME")
        if "UAT1" in env_name.split(","):
            if branch_name == "master":
                logger.info("Valid Branch for LIVE Build")
                logger.info("########## ENABLE MINION AUTH TOKEN VALIDATION - Currently Disabled #######")
                # a) Fetch Minion Auth Token
                auth_token = get_minion_auth_token()
                env_variables = {"AUTH_TOKEN": auth_token}

                # b, c) Fetch & Validate Pull Request & Release Version
                git_pull_request, git_release_version = fetch_git_info()
                env_variables["GIT_PULL_REQUEST"] = git_pull_request
                env_variables["GIT_RELEASE_VERSION"] = git_release_version

                add_variables_to_properties_file(env_variables, PROPERTIES_FILE_PATH)

                # d) Check PERFORM_SCANS value
                perform_scans = os.environ.get("PERFORM_SCANS")
                check_variable(perform_scans, "PERFORM_SCANS")
                if perform_scans.lower() not in ["True", "true"]:
                    raise Exception("Invalid value for PERFORM_SCANS, must be enabled for LIVE Build")

                # e) Check JIRA_KEY value
                jira_key = os.environ.get("JIRA_KEY")
                check_variable(jira_key, "JIRA_KEY")
                if not jira_key or jira_key == "JIRA-123456":
                    raise Exception("Invalid value for JIRA_KEY")

                # f) Check JIRA_KEY against regex
                # Match against Regex pattern for a valid JIRA key
                if not re.match(JIRA_KEY_PATTERN, jira_key):
                    raise Exception("JIRA_KEY does not match regex pattern")
                else:
                    raise ValueError("Invalid Branch for UAT1 Build")  # Specific Exception

            else:
                logger.info("Valid Branch & Environment for Non LIVE Build")

    except Exception as e:
        logger.error(f"An error occurred during Build Environment Preparation: {e}")
        exit_code = 1  # Indicate failure

    exit(exit_code)


if __name__ == "__main__":
    main()
