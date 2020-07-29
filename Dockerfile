FROM arm32v6/python:3-alpine

COPY requirements.txt .
RUN apk update; apk add build-base; pip install -r requirements.txt
COPY mqtt_gpio_relay.py .

ENTRYPOINT ./mqtt_gpio_relay.py
