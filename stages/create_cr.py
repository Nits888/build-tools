import json
from modules.env_utils import read_properties_file, PROPERTIES_FILE_PATH
from modules.request_utils import call_api


# Function to read ServiceNow credentials
def read_servicenow_credentials():
    env_variables = read_properties_file(PROPERTIES_FILE_PATH)
    servicenow_username = env_variables.get("SERVICENOW_USERNAME")
    servicenow_password = env_variables.get("SERVICENOW_PASSWORD")
    return servicenow_username, servicenow_password


# Function to calculate CR_SCHEDULE_TIME
def calculate_cr_schedule_time(deploy_delay):
    deploy_delay_value = int(deploy_delay[:-1])
    deploy_delay_unit = deploy_delay[-1]
    if deploy_delay_unit == 'h':
        return deploy_delay_value * 60  # Convert hours to minutes
    elif deploy_delay_unit == 'm':
        return deploy_delay_value


# Function to replace placeholders in JSON data with actual values
def replace_placeholders(json_data, env_variables):
    for key, value in json_data.items():
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            variable_name = value[2:-2]
            if variable_name in env_variables:
                json_data[key] = env_variables[variable_name]
    return json_data


# Function to create a change order in ServiceNow
def create_change_order(json_file_path, deploy_delay):
    try:
        # Read ServiceNow credentials
        servicenow_username, servicenow_password = read_servicenow_credentials()

        # Calculate CR_SCHEDULE_TIME
        cr_schedule_time = calculate_cr_schedule_time(deploy_delay)

        # Read JSON schema from file
        with open(json_file_path, "r") as file:
            json_data = json.load(file)

        # Read environment variables
        env_variables = read_properties_file(PROPERTIES_FILE_PATH)

        # Replace placeholders with actual values
        json_data = replace_placeholders(json_data, env_variables)

        # ServiceNow API endpoint
        servicenow_api_url = "https://your-servicenow-instance.service-now.com/api/now/table/change_request"

        # Make API call to create change order
        response = call_api(servicenow_api_url, method='POST', data=json_data, headers={'Content-Type': 'application'
                                                                                                        '/json'})

        # Check response status
        if response.get('status_code') == 200:
            # Extract the change order number from the response JSON
            change_order_number = response.get("result", {}).get("number")
            if change_order_number:
                print(f"Change order created successfully with number: {change_order_number}")
                return change_order_number
            else:
                print("Failed to retrieve change order number from the response.")
                return None
        else:
            # Print error message including status code and response text
            print(
                f"Failed to create change order. Status code: {response.get('status_code')}, "
                f"Error: {response.get('text')}")
            return None

    except Exception as e:
        print(f"An error occurred while creating change order: {e}")
        return None


# Example usage
def main():
    # JSON file containing schema for change order
    json_file_path = "config/cr_schema.json"

    # Example deploy delay
    deploy_delay = "2h"

    # Create change order
    create_change_order(json_file_path, deploy_delay)


if __name__ == "__main__":
    main()
