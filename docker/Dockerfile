FROM python:3.8.1-slim

ARG CLIENT_TOKEN_FILE
ARG TWITTER_API_TOKENS_FILE

ARG DATABASE_URI
ENV DBURI $DATABASE_URI

# pull in required files
WORKDIR /home/memebot/
COPY src src
COPY requirements.txt requirements.txt
COPY $CLIENT_TOKEN_FILE client_token
COPY $TWITTER_API_TOKENS_FILE twitter_api_tokens.json

# set up virtual environment
ENV VIRTUAL_ENV "/venv"
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

RUN \
    apt update -y && \
    # gcc is required to build package aiohttp (https://docs.aiohttp.org/en/stable/) required by discord.py
    apt install -y gcc && \
    python -m venv $VIRTUAL_ENV && \
    # install dependencies
    python -m pip install -r requirements.txt

# run memebot
CMD python3 src/main.py --database-uri ${DBURI}