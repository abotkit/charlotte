import requests
import time

def parse_intent_examples(examples: str):
    return [x.replace("- ", "") for x in examples.splitlines()]


def check_server(url, server_unavailable):
  try:
    response = requests.get(url)
    server_unavailable = False
  except requests.exceptions.ConnectionError as e:
    time.sleep(1)
  return server_unavailable