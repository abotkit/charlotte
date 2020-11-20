# charlotte
charlotte acts as a layer between rasa and abotkit and allows abotkit to spwan and update bots based on rasa

# Quickstart

```zsh
pip install -r requirements.txt
cd app
export ABOTKIT_CHARLOTTE_PORT=3080 # or any port you want to use

# use hot reload in development and during testing. Testing port is 8000
uvicorn main:app --reload

# use uvicorn wrapped by gunicorn in production
gunicorn main:app -b 0.0.0.0:${ABOTKIT_CHARLOTTE_PORT} -k uvicorn.workers.UvicornWorker --timeout 120 --workers=1 --log-level DEBUG
```

# Environment variables

|         name        |        description             |    default           |
|---------------------|--------------------------------|----------------------|
| ABOTKIT_CHARLOTTE_PORT | port for starting charlotte       |   3080               |
| ABOTKIT_CONFIG_PATH | configuration path  | None |

# Issues

We use our [main repository](https://github.com/abotkit/abotkit) to track our issues. Please use [this site](https://github.com/abotkit/abotkit/issues) to report an issue. Thanks! :blush:
