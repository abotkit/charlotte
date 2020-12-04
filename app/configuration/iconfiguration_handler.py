from abc import ABC, abstractmethod


class IConfigHandler(ABC):

    @abstractmethod
    def get_server_identifier(self):
        raise NotImplementedError

    @abstractmethod
    def force_redis_setting_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_minio_model_folder(self):
        raise NotImplementedError

    @abstractmethod
    def get_minio_data_folder(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_server_port(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_action_server_port(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_server_url(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_action_server_url(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_webhook(self):
        raise NotImplementedError

    @abstractmethod
    def get_abotkit_charlotte_port(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_server_debug_level(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_action_server_debug_level(self):
        raise NotImplementedError

    @abstractmethod
    def start_rasa_action_server(self):
        raise NotImplementedError

    @abstractmethod
    def get_minio_config(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_domain_file_key(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_nlu_file_key(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_model_key(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_model_minio_key(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_rules_key(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_stories_key(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_endpoints_file(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_config_file(self):
        raise NotImplementedError

    @abstractmethod
    def get_redis_configuration(self):
        raise NotImplementedError

    @abstractmethod
    def get_redis_model_channel(self):
        raise NotImplementedError

    @abstractmethod
    def get_storage_path(self):
        raise NotImplementedError

    @abstractmethod
    def get_rasa_action_folder(self):
        raise NotImplementedError

    @abstractmethod
    def use_redis(self):
        raise NotImplementedError

    @abstractmethod
    def use_minio(self):
        raise NotImplementedError

    @abstractmethod
    def get_minio_files(self):
        raise NotImplementedError

    @abstractmethod
    def get_bot_name(self):
        raise NotImplementedError

    @abstractmethod
    def get_config_path(self):
        raise NotImplementedError

    @abstractmethod
    def get_github_connection_url(self):
        raise NotImplementedError

    @abstractmethod
    def get_github_repo_storage_path(self):
        raise NotImplementedError

    @abstractmethod
    def use_github(self):
        raise NotImplementedError
