# syntax=docker/dockerfile:1

FROM python:3.8

COPY requirements.txt ./
RUN apt-get update -y && apt-get install tk -y && pip install -r requirements.txt

COPY /CMA ./CMA
ADD run.sh launcher.py ./

CMD ["run.sh"]