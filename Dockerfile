FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install -y curl git
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
RUN source /root/.poetry/env
COPY requirements.txt /opt/charlotte/requirements.txt
WORKDIR /opt/charlotte
RUN poetry init
RUN for item in $(cat requirements.txt); do   poetry add "${item}"; done

RUN python -m spacy download de_core_news_lg
RUN python -m spacy link de_core_news_lg de

# ARG work_dir=/opt/charlotte

COPY ./app /opt/charlotte/app
RUN mkdir /opt/charlotte/app/logs
RUN chmod +x /opt/charlotte/app/logs
WORKDIR /opt/charlotte/app
RUN ls -la


EXPOSE 3080
ENV ABOTKIT_CHARLOTTE_PORT=3080

# ENTRYPOINT gunicorn main:app -b 0.0.0.0:3080 -p charlotte.pid -k uvicorn.workers.UvicornWorker --timeout 120 --workers=1 --access-logfile /opt/charlotte/app/logs/access.log --log-level DEBUG --log-file /opt/charlotte/app/logs/app.log
ENTRYPOINT gunicorn main:app -b 0.0.0.0:${ABOTKIT_CHARLOTTE_PORT} -k uvicorn.workers.UvicornWorker --timeout 120 --workers=1 --log-level DEBUG
