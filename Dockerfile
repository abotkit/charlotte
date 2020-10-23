FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install -y curl

RUN pip install requests

COPY requirements.txt /opt/rasa/requirements.txt
WORKDIR /opt/rasa

RUN pip install -r requirements.txt
RUN rasa init --no-prompt

EXPOSE 5005
EXPOSE 5055

RUN rasa run actions --cors "*" &

ENTRYPOINT ["rasa", "run", "--enable-api", "--cors", "*"]