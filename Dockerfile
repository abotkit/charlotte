FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install -y curl

COPY requirements.txt /
RUN pip install -r /requirements.txt

ARG work_dir=/opt/charlotte

COPY ./app $work_dir
RUN mkdir $work_dir/logs
RUN chmod +x $work_dir
WORKDIR $work_dir

EXPOSE 3080

ENTRYPOINT gunicorn main:app -b 0.0.0.0:3080 -p charlotte.pid -k uvicorn.workers.UvicornWorker --timeout 120 --workers=1 --access-logfile /opt/charlotte/logs/access.log --log-level DEBUG --log-file /opt/charlotte/logs/app.log