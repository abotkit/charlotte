import os

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

