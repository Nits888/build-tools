import os
import pylint.lint as pylint

from modules.custom_logger import setup_custom_logger

# Setup custom logger
logger = setup_custom_logger(__name__)


def perform_pylint_checks(target_files):
    """Runs Pylint on specified files."""
    try:
        pylint.Run(target_files)  # Updated invocation
    except Exception as e:
        logger.error(f"Pylint checks failed: {e}")
        raise


if __name__ == '__main__':
    # Assuming source code will be in the workspace
    source_directory = os.path.join(os.environ.get("WORKSPACE", ""), "C:/Temp")
    py_files = [os.path.join(root, file)
                for root, _, files in os.walk(source_directory)
                for file in files if file.endswith('.py')]
    perform_pylint_checks(py_files)
