from abc import ABC, abstractmethod


class IMessageHandler(ABC):

    @abstractmethod
    def publish_message(self, channel, data, message_type: str = 'str'):
        raise NotImplementedError

    @abstractmethod
    def get_key(self, key: str, message_type: str = 'json'):
        raise NotImplementedError

    @abstractmethod
    def get_keys(self, pattern: str, message_type: str = 'json'):
        raise NotImplementedError

    @abstractmethod
    def set_key(self, key: str, data: str, message_type: str = 'json'):
        raise NotImplementedError

    @abstractmethod
    def subscribe_channel(self, channel: str, handler):
        raise NotImplementedError

