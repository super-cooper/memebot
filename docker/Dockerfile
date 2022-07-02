FROM python:3.9.6-slim

# pull in required files for environment
WORKDIR /opt/memebot/
COPY requirements.txt requirements.txt

RUN \
    apt update -y && \
    # gcc is required to build package aiohttp (https://docs.aiohttp.org/en/stable/) required by discord.py
    apt install -y gcc && \
    # install dependencies
    python3 -m pip install -r requirements.txt

# bring in memebot source code
COPY src src

# run memebot
ENTRYPOINT ["python3", "src/main.py"]
