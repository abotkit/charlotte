import os
from flask import Flask, jsonify, request, Response, abort
from flask_cors import CORS
from flask_api import status
import json
import requests
import subprocess
import shutil

from utilities import handlers, helpers

app = Flask(__name__)
root = os.path.dirname(os.path.abspath(__file__))
CORS(app)

data_handler = handlers.YAMLDataHandler()
rasa_handler = handlers.RasaAbstraction(data_handler=data_handler)


@app.route('/alive')
def alive():
  return '', status.HTTP_200_OK


@app.route('/init')
def init():
  target = os.path.join(root, 'rasa')
  if not os.path.isdir(target):
    os.mkdir(target)
    try:
      subprocess.run(['rasa', 'init', '--no-prompt', '--init-dir', target], shell=True)

      return 'successfully init an empty rasa bot', status.HTTP_200_OK
    except Exception as e:
      print(str(e))
      os.rmdir(target)
      return 'failed to initialize rasa bot', status.HTTP_500_INTERNAL_SERVER_ERROR
  else:
    return 'a rasa bot already exists. You may need to use the /clean endpoint first.', status.HTTP_400_BAD_REQUEST


@app.route('/clean')
def clean():
  target = os.path.join(root, 'rasa')
  if os.path.isdir(target):
    shutil.rmtree(target)
    return 'successfully cleaned rasa bot', status.HTTP_200_OK
  else:
    return 'there is no rasa bot to clean. Use the /init endpoint to build one', status.HTTP_400_BAD_REQUEST


@app.route('/intents', methods=["GET", "POST", "DELETE"])
def intents():

  if request.method == 'GET':
    domain_file_path = os.path.join(root, 'rasa', 'domain.yml')
    return jsonify(rasa_handler.get_intents(domain_file_path))


@app.route('/examples', methods=["GET", "POST", "DELETE"])
def examples():

  if request.method == 'GET':
    nlu_file_path = os.path.join(root, 'rasa', 'data', 'nlu.yml')
    return jsonify(rasa_handler.get_examples(nlu_file_path))


@app.route('/responses', methods=["GET", "POST", "DELETE"])
def responses():
  if request.method == 'GET':
    domain_file_path = os.path.join(root, 'rasa', 'domain.yml')
    return jsonify(rasa_handler.get_responses(domain_file_path))


@app.route('/rasa-server', methods=["GET", "POST"])
def start_rasa_server():
  try:
    if os.listdir(os.path.join(root, 'rasa', 'models')):
      try:
        os.chdir(os.path.join(root, 'rasa'))
        subprocess.Popen(
          ['rasa', 'run', '--enable-api', '--cors', '"*"', '-p', str(os.getenv('ABOTKIT_RASA_SERVER_PORT', 5005))],
          shell=True
        )
        rasa_server_unavailable = True
        while rasa_server_unavailable:
          rasa_server_unavailable = helpers.check_server(
            f"http://127.0.0.1:{os.getenv('ABOTKIT_RASA_SERVER_PORT', 5005)}",
            rasa_server_unavailable
          )
        return 'successfully startet rasa server', status.HTTP_200_OK
      except Exception as e:
        print(str(e)) # replace with logger
        return 'failed to start rasa server', status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
      return 'no rasa model trained yet', status.HTTP_400_BAD_REQUEST
  except Exception as e:
    print(str(e))
    return 'failed to start rasa server', status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/rasa-action-server', methods=["GET", "POST"])
def start_rasa_action_server():
  try:
    if os.path.exists(os.path.join(root, 'rasa', 'actions', 'actions.py')):
      try:
        os.chdir(os.path.join(root, 'rasa'))
        subprocess.Popen(
          ['rasa', 'run', 'actions', '--cors', '"*"', '-p', str(os.getenv('ABOTKIT_RASA_ACTION_SERVER_PORT', 5055))],
          shell=True
        )
        rasa_action_server_unavailable = True
        while rasa_action_server_unavailable:
          rasa_action_server_unavailable = helpers.check_server(
            f"http://127.0.0.1:{os.getenv('ABOTKIT_RASA_ACTION_SERVER_PORT', 5055)}",
            rasa_action_server_unavailable
          )
        return 'successfully startet rasa action server', status.HTTP_200_OK
      except Exception as e:
        print(str(e)) # replace with logger
        return 'failed to start rasa action server', status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
      return 'no actions.py file found', status.HTTP_400_BAD_REQUEST
  except Exception as e:
    print(str(e))
    return 'failed to start rasa action server', status.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == '__main__':
  port = os.getenv('ABOTKIT_CHARLOTTE_PORT', 3080)
  app.run(debug=True, port=port)