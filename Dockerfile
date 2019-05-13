FROM python:3.6-alpine

RUN apk add --update alpine-sdk glib glib-dev linux-headers

RUN mkdir /app

WORKDIR /app

RUN pip install --upgrade pip

COPY ./tray_sensor/ /app/tray_sensor/
COPY ./setup.py /app/setup.py
COPY ./README.md /app/README.md

RUN pip install .

CMD ["python", "-m", "tray_sensor.tools.tray_sensor_app", "-d", "/data/", "-o", "capucine_tray_sensors", "-l", "WARNING"]
