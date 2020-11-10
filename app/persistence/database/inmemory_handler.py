from persistence.database.idatabase_handler import IMessageHandler


class InMemoryMessageHandler(IMessageHandler):

    def __init__(self):
        self.db = dict()

    def publish_message(self, channel, data, message_type: str = 'str'):
        pass

    def get_key(self, key: str, message_type: str = 'json'):
        print(f"Get key {key}")
        return self.db[key]

    def set_key(self, key: str, data, message_type: str = 'json'):
        print(f"Set key {key} with data {data}")
        self.db[key] = data

    def subscribe_channel(self, channel: str, handler):
        pass