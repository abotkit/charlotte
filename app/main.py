import httpx
import os
import shutil
import subprocess
from fastapi import FastAPI, status, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv

import configuration.helpers as config_helpers
from api import models
from configuration.configuration_handler import ConfigHandler
from core.rasa_handler import RasaHandler
from persistence.database.inmemory_handler import InMemoryMessageHandler
from persistence.database.redis_handler import RedisHandler
from persistence.files.yaml_handler import YAMLDataHandler
from persistence.object_storage.minio_handler import MinioHandler
from persistence.object_storage.inmemory_handler import PlaceholderStorageHandler
from utilities import logger_config

logger = logger_config.get_logger(__name__)
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])


root = os.path.dirname(os.path.abspath(__file__))
data_handler = YAMLDataHandler()
config_handler = ConfigHandler(root=root, config=config_helpers.read_config_file(os.getenv('ABOTKIT_CONFIG_PATH', None)))

if config_handler.use_redis():
    message_handler = RedisHandler(config_handler.get_redis_configuration())
else:
    message_handler = InMemoryMessageHandler()
if config_handler.use_minio():
    object_handler = MinioHandler(config_handler.get_minio_config())
else:
    object_handler = PlaceholderStorageHandler()
rasa_handler = RasaHandler(
    data_handler=data_handler,
    config_handler=config_handler,
    message_handler=message_handler,
    object_handler=object_handler
)


def initialize_default_bot(target):
    os.chdir(os.path.join(root, 'rasa'))
    commands = ['rasa', 'init', '--no-prompt', '--init-dir', target]
    if os.name != 'nt':
        process = subprocess.run(commands, shell=False)
    else:
        process = subprocess.run(commands, shell=True)
    # set default model path
    if process.returncode == 0:
        rasa_handler.get_init_files_from_disk(root)


@app.on_event("startup")
def startup_event():
    logger.info(f"Starting application under root path '{root}'")
    if config_handler.use_minio():
        rasa_handler.get_init_files_from_object_storage()
    else:
        rasa_handler.get_init_files_from_disk(root)
    if config_handler.use_redis():
        rasa_handler.listen_to_model_deployment()


@app.on_event("shutdown")
def shutdown_event():
    rasa_handler.loop_thread.stop()


@app.get('/alive', status_code=status.HTTP_200_OK)
def alive():
    return ''


@app.get('/rasa-alive', status_code=status.HTTP_200_OK)
def rasa_server_alive():
    try:
        response = httpx.get(config_handler.get_rasa_server_url())
        return ''
    except httpx.ConnectError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='rasa server not available')


@app.get('/rasa-action-alive', status_code=status.HTTP_200_OK)
def rasa_action_server_alive():
    try:
        response = httpx.get(config_handler.get_rasa_action_server_url())
        return ''
    except httpx.ConnectError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='rasa action server not available')


@app.get('/init', status_code=status.HTTP_200_OK)
def init(background_tasks: BackgroundTasks):
    target = config_handler.get_storage_path()
    if not os.listdir(target):
        os.makedirs(target, exist_ok=True)
        try:
            background_tasks.add_task(initialize_default_bot, target)
            return 'successfully init an empty rasa bot'
        except Exception as e:
            os.rmdir(target)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='failed to initialize rasa bot')
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='a rasa bot already exists. You may need to use the /clean endpoint first.')


@app.get('/intents', status_code=status.HTTP_200_OK, response_model=List[models.IntentsOut])
def intents():
    intents = rasa_handler.get_intents() # change to explain intent
    if intents:
        return intents
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no domain.yml file yet')


@app.get('/example/{intent}', status_code=status.HTTP_200_OK, response_model=models.IntentOut)
def get_examples(intent: str):
    examples = rasa_handler.get_examples_for_single_intent(intent)
    if examples:
        return examples
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no data/nlu.yml file yet')


@app.get('/example', status_code=status.HTTP_200_OK, response_model=List[models.IntentsOut])
def get_examples():
    examples = rasa_handler.get_intents()
    if examples:
        return examples
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no data/nlu.yml file yet')


@app.post('/example', status_code=status.HTTP_200_OK)
def add_examples(examples: models.ExampleIn):
    success = rasa_handler.add_example(examples.example, examples.intent)
    if success:
        return "successfully added new example"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no data/nlu.yml file yet')


@app.delete('/example', status_code=status.HTTP_200_OK)
def delete_examples(examples: models.ExampleIn):
    success = rasa_handler.delete_example(examples.example, examples.intent)
    if success:
        return 'successfully deleted example'
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no data/nlu.yml file yet')


@app.get('/phrases', status_code=status.HTTP_200_OK, response_model=List[models.ResponsesOut])
def get_responses():
    responses = rasa_handler.get_responses()
    if responses:
        return responses
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no domain.yml file yet')


@app.delete('/clean', status_code=status.HTTP_200_OK)
def clean():
    target = config_handler.get_storage_path()
    if os.path.isdir(target):
        shutil.rmtree(target)
        return 'successfully cleaned rasa bot'
    else:
        raise HTTPException(status_code=400,
                            detail='there is no rasa bot to clean. Use the /init endpoint to build one')


@app.get('/rasa-server', status_code=status.HTTP_200_OK)
def start_rasa_server():
    model_path = message_handler.get_key(config_handler.get_rasa_model_key(), message_type='str')
    endpoints = os.path.join(config_handler.get_storage_path(), 'endpoints.yml')
    if config_helpers.is_valid_rasa_folder(endpoints, model_path):
        try:
            os.chdir(os.path.join(root, 'rasa'))
            commands = ['rasa', 'run', '--enable-api', '--cors', '"*"', '-p',
                        str(config_handler.get_rasa_server_port()),
                        config_handler.get_rasa_server_debug_level(),
                        '--endpoints', endpoints,
                        '--model', model_path
                        ]
            if os.name != 'nt':
                subprocess.Popen(commands, shell=False)
            else:
                subprocess.Popen(commands, shell=True)
            return 'successfully startet rasa server'
        except Exception as e:
            print(str(e))  # replace with logger
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='failed to start rasa server')
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='no rasa model trained yet')


@app.get('/rasa-action-server', status_code=status.HTTP_200_OK)
def start_rasa_action_server():
    if os.listdir(config_handler.get_rasa_action_folder()):
        try:
            os.chdir(config_handler.get_storage_path())
            commands = ['rasa', 'run', 'actions', '--cors', '"*"', '-p',
                        str(rasa_handler.config_handler.get_rasa_action_server_port()),
                        rasa_handler.config_handler.get_rasa_action_server_debug_level(),
                        ]
            if os.name != 'nt':
                subprocess.Popen(commands, shell=False)
            else:
                subprocess.Popen(commands, shell=True)
            return 'successfully startet rasa action server'
        except Exception as e:
            print(str(e))  # replace with logger
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='failed to start rasa action server')
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='no actions.py file found')


@app.post('/handle', status_code=status.HTTP_200_OK, response_model=List[models.MessageOut])
async def handle(message: models.MessageIn):
    data = dict(
        message=message.query,
        sender=message.identifier
    )

    response = rasa_handler.get_message(data)

    if response:
        return response
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='failed to handle message')


@app.post('/train', status_code=status.HTTP_200_OK)
def train_model(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(rasa_handler.train_model)
        return 'successfully started training of rasa bot with new data'
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='failed to train rasa bot')


@app.get('/train-status', status_code=status.HTTP_200_OK, response_model=models.TrainStatusOut)
def train_model():
    status = rasa_handler.get_train_status()
    if status:
        return status
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='failed to get status')


@app.put('/deploy', status_code=status.HTTP_202_ACCEPTED)
def deploy_model(deploy_model: models.DeployModelIn):
    try:
        rasa_handler.deploy_model(deploy_model.model_path)
        return 'successfully started deployment process'
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='failed to deploy model')


@app.get('/deploy', status_code=status.HTTP_200_OK)
def deploy_status():
    servers = rasa_handler.get_models_on_servers()
    if servers:
        return servers
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='no servers with any deployed models found')



