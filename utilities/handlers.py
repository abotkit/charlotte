from abc import ABC, abstractmethod
import yaml

from utilities import helpers


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

    def __init__(self, data_handler: IDataHandler):
        self.data_handler = data_handler

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


