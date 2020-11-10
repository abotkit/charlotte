from abc import ABC, abstractmethod


class IDataHandler(ABC):

    @abstractmethod
    def read_yaml_file(self, path: str):
        raise NotImplementedError

    @abstractmethod
    def write_yaml_file(self, path: str, content: dict):
        raise NotImplementedError