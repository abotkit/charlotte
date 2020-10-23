import os
from flask import Flask, jsonify, request, Response, abort
from flask_cors import CORS
from flask_api import status
import json
import subprocess
import shutil

app = Flask(__name__)
root = os.path.dirname(os.path.abspath(__file__))
CORS(app)

@app.route('/alive')
def alive():
  return '', status.HTTP_200_OK

@app.route('/init')
def init():
  target = os.path.join(root, 'rasa')
  if not os.path.isdir(target):
    os.mkdir(target)
    try:
      subprocess.run(['rasa', 'init', '--no-prompt', '--init-dir', target])
      return 'successfully init an empty rasa bot', status.HTTP_200_OK
    except expression as identifier:
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


if __name__ == '__main__':
  port = os.getenv('ABOTKIT_CHARLOTTE_PORT', 3080)
  app.run(debug=True, port=port)