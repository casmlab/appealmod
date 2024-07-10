# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV TZ="America/Detroit"

RUN chmod a+x run.sh

CMD [ "./run.sh"]