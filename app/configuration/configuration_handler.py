import os

import configuration.helpers
from configuration.iconfiguration_handler import IConfigHandler


class ConfigHandler(IConfigHandler):

    def __init__(self, root, config=None):
        self.root = root
        self.config = config

    def get_server_identifier(self):
        return f"pod_name_{os.getenv('ABOTKIT_POD_NAME', 'server_0')}"

    def force_redis_setting_data(self):
        return str(os.getenv('ABOTKIT_REDIS_FORCE_SETTING_DATA', False)).lower() == 'true'

    def get_minio_model_folder(self):
        return os.getenv('ABOTKIT_MINIO_MODEL_FOLDER', 'models')

    def get_minio_data_folder(self):
        return os.getenv('ABOTKIT_MINIO_DATA_FOLDER', 'data')

    def get_config_path(self):
        return os.getenv('ABOTKIT_CONFIG_PATH', None)

    def get_bot_name(self):
        return os.getenv('ABOTKIT_BOT_NAME', 'default_bot')

    def get_minio_files(self):
        try:
            if 'MINIO' in self.config:
                if 'FILES' in self.config['MINIO']:
                    return self.config['MINIO']['FILES']
        except (TypeError, KeyError) as e:
            print(f"Configuration error. Check config.ini ... {str(e)}")

    def use_redis(self):
        return str(os.getenv('ABOTKIT_USE_REDIS', False)).lower() == 'true'

    def use_minio(self):
        return str(os.getenv('ABOTKIT_USE_MINIO', False)).lower() == 'true'

    def get_rasa_action_folder(self):
        return os.getenv('ABOTKIT_RASA_ACTION_FOLDER', os.path.join(self.root, 'rasa', 'actions'))

    def get_storage_path(self):
        return os.getenv('ABOTKIT_STORAGE_PATH', os.path.join(self.root, 'rasa'))

    def get_rasa_model_key(self):
        return 'model_path'

    def get_rasa_model_minio_key(self):
        return 'model_minio_path'

    def get_redis_configuration(self):
        return {
            'host': os.getenv('ABOTKIT_REDIS_HOST', 'http://192.168.99.100'),
            'port': os.getenv('ABOTKIT_REDIS_PORT', 6379),
            'db': os.getenv('ABOTKIT_REDIS_DB', 2),
            'password': os.getenv('ABOTKIT_REDIS_PASSWORD', None)
        }

    def get_redis_model_channel(self):
        return os.getenv('ABOTKIT_REDIS_MODEL_CHANNEL', None)

    def get_rasa_domain_file_key(self):
        return 'domain_file'

    def get_rasa_nlu_file_key(self):
        return 'nlu_file'

    def get_rasa_rules_key(self):
        return 'rules_file'

    def get_rasa_stories_key(self):
        return 'stories_file'

    def get_rasa_endpoints_file(self):
        return os.getenv('ABOTKIT_RASA_ENDPOINTS_PATH', os.path.join(self.root, 'rasa', 'endpoints.yml'))

    def get_rasa_config_file(self):
        return os.getenv('ABOTKIT_RASA_CONFIG_PATH', os.path.join(self.root, 'rasa', 'config.yml'))

    def get_minio_config(self):
        return dict(
            url=f"{os.getenv('ABOTKIT_MINIO_URL', 'localhost')}:{os.getenv('ABOTKIT_MINIO_PORT', 9000)}",
            access_key=os.getenv('ABOTKIT_MINIO_ACCESS_KEY', None),
            secret_key=os.getenv('ABOTKIT_MINIO_SECRET_KEY', None)
        )

    def start_rasa_action_server(self):
        return os.getenv('ABOTKIT_START_RASA_ACTION_SERVER', False)

    def get_rasa_server_debug_level(self):
        debug_level = os.getenv('ABOTKIT_RASA_SERVER_DEBUG_LEVEL', 'DEBUG')
        return configuration.helpers.get_debug_level(debug_level)

    def get_rasa_action_server_debug_level(self):
        debug_level = os.getenv('ABOTKIT_RASA_ACTION_SERVER_DEBUG_LEVEL', 'DEBUG')
        return configuration.helpers.get_debug_level(debug_level)

    def get_abotkit_charlotte_port(self):
        return os.getenv('ABOTKIT_CHARLOTTE_PORT', 3080)

    def get_rasa_server_port(self):
        return os.getenv('ABOTKIT_RASA_SERVER_PORT', 5005)

    def get_rasa_action_server_port(self):
        return os.getenv('ABOTKIT_RASA_ACTION_SERVER_PORT', 5055)

    def get_rasa_action_server_url(self):
        return f"{os.getenv('ABOTKIT_RASA_ACTION_SERVER_HOST', 'http://localhost')}:{os.getenv('ABOTKIT_RASA_ACTION_SERVER_PORT', 5055)}"

    def get_rasa_server_url(self):
        return f"{os.getenv('ABOTKIT_RASA_SERVER_HOST', 'http://localhost')}:{os.getenv('ABOTKIT_RASA_SERVER_PORT', 5005)}"

    def get_rasa_webhook(self):
        return f"{self.get_rasa_server_url()}/webhooks/rest/webhook"

    def get_github_connection_url(self):
        return f"https://{os.getenv('ABOTKIT_GITHUB_USER', None)}:{os.getenv('ABOTKIT_GITHUB_PASSWORD', None)}@{os.getenv('ABOTKIT_GITHUB_PROJECT', None)}"

    def get_github_repo_storage_path(self):
        return os.getenv('ABOTKIT_GITHUB_REPO_PATH', os.path.join(self.root, 'customer-repo'))

    def use_github(self):
        return str(os.getenv('ABOTKIT_USE_GITHUB', False)).lower() == 'true'