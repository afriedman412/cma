# syntax=docker/dockerfile:1

FROM python:3.10-slim

COPY requirements.txt ./
RUN apt-get update -y && apt-get install tk -y && pip install -r requirements.txt

COPY /src ./src

ADD launcher.py ./

CMD ["python", "launcher.py"]