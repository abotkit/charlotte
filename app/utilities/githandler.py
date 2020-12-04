import git
import os
import subprocess

from utilities import logger_config, helpers

logger = logger_config.get_logger(__name__)


class GitHandler:

    def __init__(self, repository_url, repository_path):
        self.repository_url = repository_url
        self.repository_path = repository_path

    def clone_repository(self, branch: str = 'main'):
        try:
            git.Repo.clone_from(self.repository_url, self.repository_path, branch=branch)
            logger.info(f"Successfully cloned repository to path '{self.repository_path}'")
        except Exception as e:
            logger.error(f"Failed to clone repository to path '{self.repository_path}'")
            logger.error(str(e))

    def install_requirements(self, file_name: str = 'requirements.txt'):
        if os.path.isdir(self.repository_path):
            requirements_file_path = helpers.find_file(self.repository_path, file_name)
            commands = ['pip', 'install', '-r', requirements_file_path]
            if os.name != 'nt':
                process = subprocess.run(commands, shell=False)
            else:
                process = subprocess.run(commands, shell=True)

            if process.returncode == 0:
                logger.info("Successfully installed requirements for action server...")
            else:
                logger.error("Failed to install requirements for action server...")
        else:
            logger.error(f"There is no directory under the given repository path '{self.repository_path}'")

    def get_actions_folder(self, action_folder: str = 'actions'):
        return helpers.find_folder(self.repository_path, action_folder)

    def delete_repository(self):
        logger.info(f"Delete customer repository under path '{self.repository_path}'")
        helpers.delete_folder(self.repository_path)


