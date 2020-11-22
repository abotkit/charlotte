import json
import os
import subprocess
import time

import httpx

import configuration.helpers
import core.helpers
from configuration.iconfiguration_handler import IConfigHandler
from persistence.database.idatabase_handler import IMessageHandler
from persistence.files.ifile_handler import IDataHandler
from persistence.object_storage.iobjectstorage_handler import IObjectStorageHandler
from utilities import logger_config

logger = logger_config.get_logger(__name__)


class RasaHandler:

    def __init__(self, data_handler: IDataHandler, config_handler: IConfigHandler,
                 message_handler: IMessageHandler, object_handler: IObjectStorageHandler):
        self.data_handler = data_handler
        self.config_handler = config_handler
        self.message_handler = message_handler
        self.object_handler = object_handler
        self.loop_thread = None

    def get_intents(self):
        nlu_file = self.message_handler.get_key(self.config_handler.get_rasa_nlu_file_key())
        if nlu_file:
            logger.info("Returning intents")
            return core.helpers.get_intents(nlu_file)
        else:
            logger.info("No nlu.yml found")
            return None

    def add_example(self, example: str, intent: str):
        nlu_file = self.message_handler.get_key(self.config_handler.get_rasa_nlu_file_key())
        domain_file = self.message_handler.get_key(self.config_handler.get_rasa_domain_file_key())
        if nlu_file and domain_file:
            logger.info(f"Add example '{example}' to intent '{intent}'")
            nlu_file, domain_file = core.helpers.add_example(nlu_file, example, intent, domain_file)
            success_nlu = self.message_handler.set_key(self.config_handler.get_rasa_nlu_file_key(), nlu_file)
            success_domain = self.message_handler.set_key(self.config_handler.get_rasa_domain_file_key(), domain_file)
            if success_nlu and success_domain:
                return True
            else:
                return None
        else:
            logger.info("No nlu.yml or domain.yml found")
            return None

    def get_examples_for_single_intent(self, intent):
        nlu_file = self.message_handler.get_key(self.config_handler.get_rasa_nlu_file_key())
        if nlu_file:
            return core.helpers.get_examples(nlu_file, intent)
        else:
            return None

    def get_examples_for_all_intents(self):
        nlu_file = self.message_handler.get_key(self.config_handler.get_rasa_nlu_file_key())
        if nlu_file:
            return core.helpers.get_all_examples(nlu_file)
        else:
            return None

    def delete_example(self, example, intent):
        nlu_file = self.message_handler.get_key(self.config_handler.get_rasa_nlu_file_key())
        if nlu_file:
            nlu_file = core.helpers.delete_example(nlu_file, example, intent)
            if nlu_file:
                success = self.message_handler.set_key(self.config_handler.get_rasa_nlu_file_key(), nlu_file)
                return success
            else:
                return 0
        else:
            return None

    def get_responses(self):
        domain_file = self.message_handler.get_key(self.config_handler.get_rasa_domain_file_key())
        if domain_file:
            return core.helpers.get_responses(domain_file)
        else:
            return None

    def get_message(self, data: dict):
        try:
            r = httpx.post(self.config_handler.get_rasa_webhook(), data=json.dumps(data))
            if r.status_code == 200:
                if r.json():
                    return r.json()
                else:
                    logger.warning(r.content)
                    return None
            else:
                logger.warning(r.status_code)
                return None
        except Exception as e:
            logger.error(f"Message webhook exception: {str(e)}")
            return None

    def train_model(self):
        self.message_handler.set_key('train_status', 'started', message_type='str')
        config_file = self.config_handler.get_rasa_config_file()
        files = dict()
        for key, value in self.config_handler.get_minio_files().items():
            path = os.path.join(self.config_handler.get_storage_path(), self.config_handler.get_minio_data_folder(), value)
            files[key] = path
            if key == 'domain':
                domain_file = self.message_handler.get_key(self.config_handler.get_rasa_domain_file_key())
                self.data_handler.write_yaml_file(path, domain_file)
            elif key == 'nlu':
                nlu_file = self.message_handler.get_key(self.config_handler.get_rasa_nlu_file_key())
                self.data_handler.write_yaml_file(path, nlu_file)
            elif key == 'rules':
                rules_file = self.message_handler.get_key(self.config_handler.get_rasa_rules_key())
                self.data_handler.write_yaml_file(path, rules_file)
            elif key == 'stories':
                stories_file = self.message_handler.get_key(self.config_handler.get_rasa_stories_key())
                self.data_handler.write_yaml_file(path, stories_file)
        model_file_name = f"doctor_bot_model_{time.strftime('%d%m%Y%H%M%S')}"
        out_path = os.path.join(self.config_handler.get_storage_path(), self.config_handler.get_minio_model_folder())
        commands = [
            'rasa', 'train',
            '--data', files['nlu'], files['stories'], files['rules'],
            '--domain', files['domain'],
            '--config', config_file,
            '--out', out_path,
            '--fixed-model-name', model_file_name
        ]
        if os.name != 'nt':
            process = subprocess.run(commands, shell=False)
        else:
            process = subprocess.run(commands, shell=True)
        # set default model path
        if process.returncode == 0:
            model_path = os.path.join(out_path, f"{model_file_name}.tar.gz")
            if os.path.isfile(model_path):
                self.message_handler.set_key('train_status', 'done', message_type='str')
                self.message_handler.set_key(self.config_handler.get_rasa_model_key(), model_path, message_type='str')
                model_minio_path = f"{self.config_handler.get_minio_model_folder()}/{model_file_name}.tar.gz"
                res = self.object_handler.upload_file(self.config_handler.get_bot_name(), model_minio_path, model_path)
                if res:
                    self.message_handler.set_key(self.config_handler.get_rasa_model_minio_key(), model_minio_path, message_type='str')

    def get_init_files_from_disk(self, path: str):
        domain_file = self.data_handler.read_yaml_file(configuration.helpers.get_default_domain_file(path))
        self.message_handler.set_key(self.config_handler.get_rasa_domain_file_key(), domain_file)
        nlu_file = self.data_handler.read_yaml_file(configuration.helpers.get_default_nlu_file(path))
        self.message_handler.set_key(self.config_handler.get_rasa_nlu_file_key(), nlu_file)
        model_path = configuration.helpers.get_default_model(path)
        self.message_handler.set_key(self.config_handler.get_rasa_model_key(), model_path, message_type='str')

    def get_init_files_from_object_storage(self):
        # set files only when key is not None in redis
        bucket = self.config_handler.get_bot_name()
        if self.object_handler.bucket_exists(bucket):
            for key, value in self.config_handler.get_minio_files().items():
                if key != 'model':
                    storage_path = os.path.join(self.config_handler.get_storage_path(),
                                                self.config_handler.get_minio_data_folder())
                if key == 'model':
                    if 'models/' in value:
                        storage_path = self.config_handler.get_storage_path()
                    else:
                        storage_path = os.path.join(self.config_handler.get_storage_path(),
                                                    self.config_handler.get_minio_model_folder())
                    res = self.object_handler.download_file(bucket, value, storage_path)
                    if res:
                        model_path = self.message_handler.get_key(self.config_handler.get_rasa_model_key(),
                                                                  message_type='str')
                        if model_path is None or self.config_handler.force_redis_setting_data():
                            self.message_handler.set_key(self.config_handler.get_rasa_model_key(), os.path.join(storage_path, value), message_type='str')
                        model_minio_path = self.message_handler.get_key(self.config_handler.get_rasa_model_minio_key(), message_type='str')
                        if model_minio_path is None or self.config_handler.force_redis_setting_data():
                            self.message_handler.set_key(self.config_handler.get_rasa_model_minio_key(), value, message_type='str')
                elif key == 'nlu':
                    res = self.object_handler.download_file(bucket, value, storage_path)
                    if res:
                        nlu_file = self.message_handler.get_key(self.config_handler.get_rasa_nlu_file_key())
                        if nlu_file is None or self.config_handler.force_redis_setting_data():
                            file_content = self.data_handler.read_yaml_file(os.path.join(storage_path, value))
                            self.message_handler.set_key(self.config_handler.get_rasa_nlu_file_key(), file_content)
                elif key == 'rules':
                    res = self.object_handler.download_file(bucket, value, storage_path)
                    if res:
                        rules_file = self.message_handler.get_key(self.config_handler.get_rasa_rules_key())
                        if rules_file is None or self.config_handler.force_redis_setting_data():
                            file_content = self.data_handler.read_yaml_file(os.path.join(storage_path, value))
                            self.message_handler.set_key(self.config_handler.get_rasa_rules_key(), file_content)
                elif key == 'stories':
                    res = self.object_handler.download_file(bucket, value, storage_path)
                    if res:
                        stories_files = self.message_handler.get_key(self.config_handler.get_rasa_stories_key())
                        if stories_files is None or self.config_handler.force_redis_setting_data():
                            file_content = self.data_handler.read_yaml_file(os.path.join(storage_path, value))
                            self.message_handler.set_key(self.config_handler.get_rasa_stories_key(), file_content)
                elif key == 'domain':
                    res = self.object_handler.download_file(bucket, value, storage_path)
                    if res:
                        domain_file = self.message_handler.get_key(self.config_handler.get_rasa_domain_file_key())
                        if domain_file is None or self.config_handler.force_redis_setting_data():
                            file_content = self.data_handler.read_yaml_file(os.path.join(storage_path, value))
                            self.message_handler.set_key(self.config_handler.get_rasa_domain_file_key(), file_content)
        else:
            logger.info(f"Bucket '{bucket}' does not exists...")

    def get_train_status(self):
        status = self.message_handler.get_key('train_status', message_type='str')
        if status == 'done':
            return {'done': True}
        else:
            return {'done': False}

    def deploy_model(self, model_path):
        self.message_handler.publish_message(self.config_handler.get_redis_model_channel(), model_path)

    def handle_deployed_model(self, message):
        model_path = message['data'].decode('utf-8')
        channel = message['channel'].decode('utf-8')
        if channel == self.config_handler.get_redis_model_channel():
            logger.info(f"New model deployed from minio '{model_path}'")
            local_model_path = os.path.join(self.config_handler.get_storage_path(), model_path)
            if os.path.isfile(local_model_path):
                logger.info(f"File '{local_model_path}' already exists...")
                logger.info(f"Restarting server with model stored under: {local_model_path}")
                self.restart_rasa_server_with_new_model(model_path, local_model_path)

            else:
                logger.info(f"File '{local_model_path}' does not exists yet...")
                logger.info(f"Download file from minio...")
                res = self.object_handler.download_file(self.config_handler.get_bot_name(), model_path,
                                                        self.config_handler.get_storage_path())
                if res and os.path.isfile(local_model_path):
                    # restart server with model
                    logger.info(f"Restarting server with model stored under: {local_model_path}")
                    self.restart_rasa_server_with_new_model(model_path, local_model_path)
        # delete all models from local storage except current one

    def listen_to_model_deployment(self):
        if self.config_handler.get_redis_model_channel():
            self.loop_thread = self.message_handler.subscribe_channel(self.config_handler.get_redis_model_channel(), self.handle_deployed_model)
        else:
            logger.info("No channel to listen to...")

    def restart_rasa_server_with_new_model(self, model_path, local_model_path):
        success = None
        data = dict(
            model_file=local_model_path
        )
        url = f"{self.config_handler.get_rasa_server_url()}/model"
        try:
            r = httpx.put(url, data=json.dumps(data)).status_code
            if r == 204:
                logger.info(f"Successfully restarted rasa server")
                self.message_handler.set_key(self.config_handler.get_server_identifier(), model_path, message_type='str')
                self.message_handler.set_key(self.config_handler.get_rasa_model_minio_key(), model_path,
                                             message_type='str')
                self.message_handler.set_key(self.config_handler.get_rasa_model_key(), local_model_path,
                                             message_type='str')
                success = True
            else:
                logger.info(f"Restarting was not successfull. Ended with status code: {r.status_code}")
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            logger.info(f"Couldnt reach rasa server url {url} with new model stored under: {local_model_path}")
            logger.info(str(e))
        finally:
            return success

    def get_models_on_servers(self):
        return self.message_handler.get_keys('pod_name_*', message_type='str')



