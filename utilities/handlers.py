from abc import ABC, abstractmethod
import yaml
import os

from utilities import helpers


class IConfigHandler(ABC):
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


class ConfigHandler(IConfigHandler):

    def get_abotkit_charlotte_port(self):
        return os.getenv('ABOTKIT_CHARLOTTE_PORT', 3080)

    def get_rasa_server_port(self):
        return os.getenv('ABOTKIT_RASA_SERVER_PORT', 5005)

    def get_rasa_action_server_port(self):
        return os.getenv('ABOTKIT_RASA_ACTION_SERVER_PORT', 5055)

    def get_rasa_action_server_url(self):
        return f"{os.getenv('ABOTKIT_RASA_ACTION_SERVER_HOST', 'http://127.0.0.1')}:{os.getenv('ABOTKIT_RASA_ACTION_SERVER_PORT', 5055)}"

    def get_rasa_server_url(self):
        return f"{os.getenv('ABOTKIT_RASA_SERVER_HOST', 'http://127.0.0.1')}:{os.getenv('ABOTKIT_RASA_SERVER_PORT', 5005)}"

    def get_rasa_webhook(self):
        return f"{self.get_rasa_server_url()}/webhooks/rest/webhook"


class IDataHandler(ABC):

    @abstractmethod
    def read_yaml_file(self, path: str):
        raise NotImplementedError


class YAMLDataHandler(IDataHandler):
    def read_yaml_file(self, path: str):
        with open(path) as file:
            yaml_file = yaml.full_load(file)
        return yaml_file


class RasaAbstraction():

    def __init__(self, data_handler: IDataHandler, config_handler: IConfigHandler):
        self.data_handler = data_handler
        self.config_handler = config_handler

    def get_intents(self, path: str):
        domain_file = self.data_handler.read_yaml_file(path)
        return domain_file['intents']

    def get_examples(self, path: str):
        parsed_examples = dict()
        nlu_file = self.data_handler.read_yaml_file(path)
        for intent in nlu_file['nlu']:
            parsed_examples[intent['intent']] = helpers.parse_intent_examples(intent['examples'])
        return parsed_examples

    def get_responses(self, path: str):
        parsed_responses = dict()
        domain_file = self.data_handler.read_yaml_file(path)
        for response, elements in domain_file['responses'].items():
            parsed_responses[response] = [elem['text'] for elem in elements if 'text' in elem]
            #parsed_responses[response] = [v for k, v in d.items() if k == 'text' for d in elements]
        return parsed_responses


