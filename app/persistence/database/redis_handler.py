import json
import logging
import os
import redis

from persistence.database.idatabase_handler import IMessageHandler

logging.basicConfig(level=logging.INFO)


class RedisHandler(IMessageHandler):

    def __init__(self, config):
        self.redis_pool = redis.ConnectionPool(host=config['host'], port=config['port'], password=config['password'], db=config['db'])
        self.redis = redis.StrictRedis(connection_pool=self.redis_pool)
        self.prefix = os.getenv('ABOTKIT_REDIS_PREFIX', 'charlotte_')
        self.__connected()

    def __connected(self):
        self.redis.ping()
        logging.info("Successfully connected to redis...")

    def get_key(self, key: str, message_type: str = 'json'):
        try:
            print(f"Redis - getting data from key {self.prefix}_{key}")
            data = self.redis.get(f"{self.prefix}_{key}")
            if data:
                if message_type == 'json':
                    return json.loads(data)
                elif message_type == 'str':
                    return data.decode('utf-8')
            else:
                return None
        except Exception as e:
            print(f"Redis get_message exception: {str(e)}")

    def get_keys(self, pattern: str, message_type: str = 'json'):
        try:
            print(f"Redis - getting data from pattern {self.prefix}_{pattern}")
            cursor, keys = self.redis.scan(match=f"{self.prefix}_{pattern}")
            data = self.redis.mget(keys)
            if data:
                if message_type == 'str':
                    return [d.decode('utf-8') for d in data]
            else:
                return None
        except Exception as e:
            print(f"Redis get_keys exception: {str(e)}")

    def set_key(self, key: str, data, message_type: str = 'json'):
        success = None
        try:
            print(f"Redis - Setting data for key {self.prefix}_{key}")
            if message_type == 'str':
                self.redis.set(f"{self.prefix}_{key}", data)
                success = True
            elif message_type == 'json':
                self.redis.set(f"{self.prefix}_{key}", json.dumps(data))
                success = True
        except Exception as e:
            print(f"Redis send message exception occured: {str(e)}")
            success = False
        finally:
            return success

    def subscribe_channel(self, channel: str, handler):
        p = self.redis.pubsub()
        p.subscribe(**{channel: handler})
        thread = p.run_in_thread(sleep_time=2)
        return thread

    def publish_message(self, channel, data, message_type: str = 'str'):
        success = None
        try:
            if message_type == 'str':
                self.redis.publish(channel, data)
            success = True
        except Exception as e:
            print(f"Redis publish message exception: {str(e)}")
        finally:
            return success

