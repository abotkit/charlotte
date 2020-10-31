import httpx
import uvicorn
import os
import shutil
import subprocess
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.api import models
from app.utilities import handlers

app = FastAPI()
root = os.path.dirname(os.path.abspath(__file__))
print("ROOT", root)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

session = None

data_handler = handlers.YAMLDataHandler()
config_handler = handlers.ConfigHandler()
rasa_handler = handlers.RasaAbstraction(
    data_handler=data_handler,
    config_handler=config_handler
)


@app.get('/alive', status_code=status.HTTP_200_OK)
def alive():
    return ''


@app.get('/rasa-alive', status_code=status.HTTP_200_OK)
def rasa_server_alive():
    try:
        response = httpx.get(rasa_handler.config_handler.get_rasa_server_url())
        return ''
    except httpx.ConnectError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='rasa server not available')


@app.get('/rasa-action-alive', status_code=status.HTTP_200_OK)
def rasa_action_server_alive():
    try:
        response = httpx.get(rasa_handler.config_handler.get_rasa_action_server_url())
        return ''
    except httpx.ConnectError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='rasa action server not available')


@app.get('/init', status_code=status.HTTP_200_OK)
def init():
    target = os.path.join(root, 'rasa')
    if not os.path.isdir(target):
        os.mkdir(target)
        try:
            subprocess.run(['rasa', 'init', '--no-prompt', '--init-dir', target], shell=True)
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
    domain_file_path = os.path.join(root, 'rasa', 'domain.yml')
    if os.path.isfile(domain_file_path):
        return rasa_handler.get_intents(domain_file_path)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no domain.yml file yet')


@app.get('/examples', status_code=status.HTTP_200_OK, response_model=List[models.ExamplesOut])
def examples():
    nlu_file_path = os.path.join(root, 'rasa', 'data', 'nlu.yml')
    if os.path.isfile(nlu_file_path):
        return rasa_handler.get_examples(nlu_file_path)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no data/nlu.yml file yet')


@app.get('/responses', status_code=status.HTTP_200_OK, response_model=List[models.ResponsesOut])
def responses():
    domain_file_path = os.path.join(root, 'rasa', 'domain.yml')
    if os.path.isfile(domain_file_path):
        return rasa_handler.get_responses(domain_file_path)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='there is no domain.yml file yet')


@app.delete('/clean', status_code=status.HTTP_200_OK)
def clean():
    target = os.path.join(root, 'rasa')
    if os.path.isdir(target):
        shutil.rmtree(target)
        return 'successfully cleaned rasa bot'
    else:
        raise HTTPException(status_code=400,
                            detail='there is no rasa bot to clean. Use the /init endpoint to build one')


@app.get('/rasa-server', status_code=status.HTTP_200_OK)
def start_rasa_server():
    if os.listdir(os.path.join(root, 'rasa', 'models')):
        try:
            os.chdir(os.path.join(root, 'rasa'))
            subprocess.Popen(
                ['rasa', 'run', '--enable-api', '--cors', '"*"', '-p',
                 str(rasa_handler.config_handler.get_rasa_server_port())],
                shell=True
            )
            return 'successfully startet rasa server'
        except Exception as e:
            print(str(e))  # replace with logger
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='failed to start rasa server')
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='no rasa model trained yet')


@app.get('/rasa-action-server', status_code=status.HTTP_200_OK)
def start_rasa_action_server():
    if os.path.exists(os.path.join(root, 'rasa', 'actions', 'actions.py')):
        try:
            os.chdir(os.path.join(root, 'rasa'))
            subprocess.Popen(
                ['rasa', 'run', 'actions', '--cors', '"*"', '-p',
                 str(rasa_handler.config_handler.get_rasa_action_server_port())],
                shell=True
            )
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


if __name__ == "__main__":
    uvicorn.run("main:app", port=rasa_handler.config_handler.get_abotkit_charlotte_port(), reload=True)
