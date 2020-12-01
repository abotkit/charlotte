import os
import shutil

from utilities import logger_config

logger = logger_config.get_logger(__name__)


def bot_exists(target):
    if os.path.exists(target) and os.path.isdir(target):
        if not os.listdir(target):
            logger.info(f"Folder '{target}' does exists but holds no files. Start initializing rasa bot... ")
            return False
        else:
            logger.info("a rasa bot already exists. You may need to use the /clean endpoint first.")
            return True
    else:
        logger.info(f"Target folder '{target}' does not exist. Start initializing rasa bot...")
        os.makedirs(target, exist_ok=True)
        return False


def find_file(path: str, file_name: str):
    for dirpath, subdirs, files in os.walk(path):
        for file in files:
            if file == file_name:
                return os.path.join(dirpath, file)


def find_folder(path: str, folder_name: str):
    for dirpath, subdirs, files in os.walk(path):
        for subdir in subdirs:
            if subdir == folder_name:
                return os.path.join(dirpath, subdir)


def delete_folder(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False)

