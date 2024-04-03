FROM python:3.12

RUN pip install --upgrade pip && \
    pip install \
    aiohttp==3.9.3 \
    python-socketio==5.11.2
COPY ./src /src