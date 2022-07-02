FROM python:3.9.6-slim

# pull in required files for environment
WORKDIR /home/memebot/
COPY requirements.txt requirements.txt

# set up virtual environment
ENV MEMEBOT_VIRTUAL_ENV "/venv"
ENV MEMEBOT_PYTHON "${MEMEBOT_VIRTUAL_ENV}/bin/python3"

RUN \
    apt update -y && \
    # gcc is required to build package aiohttp (https://docs.aiohttp.org/en/stable/) required by discord.py
    apt install -y gcc && \
    python3 -m venv ${MEMEBOT_VIRTUAL_ENV} && \
    # install dependencies
    ${MEMEBOT_PYTHON} -m pip install -r requirements.txt

# bring in memebot source code
COPY src src

# run memebot
ENTRYPOINT ${MEMEBOT_PYTHON} src/main.py
