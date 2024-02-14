import requests
from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH


# Function to read JIRA credentials
def read_jira_credentials():
    env_variables = read_properties_file(PROPERTIES_FILE_PATH)
    jira_username = env_variables.get("JIRA_USERNAME")
    jira_password = env_variables.get("JIRA_PASSWORD")
    return jira_username, jira_password


# Function to create a JIRA issue
def create_jira_issue(summary, description, issue_type="Task"):
    try:
        # Read JIRA credentials
        jira_username, jira_password = read_jira_credentials()

        # JIRA API endpoint
        jira_api_url = "https://your-jira-instance.atlassian.net/rest/api/2/issue/"

        # Request headers
        headers = {
            "Content-Type": "application/json"
        }

        # Request body
        payload = {
            "fields": {
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": issue_type
                }
            }
        }

        # Make API call to create JIRA issue
        response = requests.post(
            jira_api_url,
            headers=headers,
            auth=(jira_username, jira_password),
            json=payload
        )

        # Check response status
        if response.status_code == 201:
            jira_issue_key = response.json().get("key")
            print(f"JIRA issue created successfully with key: {jira_issue_key}")
            return jira_issue_key
        else:
            print(f"Failed to create JIRA issue. Status code: {response.status_code}, Error: {response.text}")
            return None

    except Exception as e:
        print(f"An error occurred while creating JIRA issue: {e}")
        return None


# Function to transition JIRA issue status
def transition_jira_issue_status(issue_key, transition_id):
    try:
        # Read JIRA credentials
        jira_username, jira_password = read_jira_credentials()

        # JIRA API endpoint
        jira_api_url = f"https://your-jira-instance.atlassian.net/rest/api/2/issue/{issue_key}/transitions"

        # Request headers
        headers = {
            "Content-Type": "application/json"
        }

        # Request body
        payload = {
            "transition": {
                "id": transition_id
            }
        }

        # Make API call to transition JIRA issue status
        response = requests.post(
            jira_api_url,
            headers=headers,
            auth=(jira_username, jira_password),
            json=payload
        )

        # Check response status
        if response.status_code == 204:
            print(f"JIRA issue status transitioned successfully for issue: {issue_key}")
            return True
        else:
            print(
                f"Failed to transition JIRA issue status. Status code: {response.status_code}, Error: {response.text}")
            return False

    except Exception as e:
        print(f"An error occurred while transitioning JIRA issue status: {e}")
        return False


# Example usage
def main():
    # Create JIRA issue
    summary = "Summary of the issue"
    description = "Description of the issue"
    issue_key = create_jira_issue(summary, description)

    if issue_key:
        # Transition JIRA issue status
        transition_id = "ID_OF_TRANSITION"
        transition_jira_issue_status(issue_key, transition_id)


if __name__ == "__main__":
    main()
