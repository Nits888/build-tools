import json
from modules.env_utils import file_exists


def load_rundeck_config(project):
    config_file_path = f'{project}.json'
    if file_exists(config_file_path):
        with open(config_file_path, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Rundeck config not found for project: {project}")


def determine_rundeck_config(env_variables):
    if "RUNDECK_PROJECT" in env_variables:
        return load_rundeck_config(env_variables["RUNDECK_PROJECT"])
    else:
        return None
