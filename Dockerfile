# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && apt-get clean

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV TZ="America/Detroit"

RUN chmod a+x run.sh

CMD [ "./run.sh"]
