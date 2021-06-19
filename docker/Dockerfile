FROM python:3.8.1-slim

ARG CLIENT_TOKEN_FILE
ARG TWITTER_API_TOKENS_FILE

ARG DATABASE_URI
ENV MEMEBOT_DATABASE_URI ${DATABASE_URI}

# pull in required files
WORKDIR /home/memebot/
COPY src src
COPY requirements.txt requirements.txt
COPY ${CLIENT_TOKEN_FILE} client_token
COPY ${TWITTER_API_TOKENS_FILE} twitter_api_tokens.json

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

# run memebot
CMD ${MEMEBOT_PYTHON} src/main.py --database-uri ${MEMEBOT_DATABASE_URI}
