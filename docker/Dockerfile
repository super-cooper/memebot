FROM python:3.9.6-slim as release

# pull in required files for environment
WORKDIR /opt/memebot/
COPY requirements.txt requirements.txt

RUN \
    apt-get update -y && \
    # gcc is required to build package aiohttp (https://docs.aiohttp.org/en/stable/) required by discord.py
    apt-get install --no-install-recommends -y gcc=4:10.2.1-1 && \
    # Remove apt lists
    rm -rf /var/lib/apt/lists/* && \
    # install dependencies
    python3 -m pip install --no-cache-dir -r requirements.txt

# bring in memebot source code
COPY src src

# run memebot
ENTRYPOINT ["python3", "src/main.py"]

FROM release as test

COPY . .

RUN python3 -m pip install --no-cache-dir -r tests/requirements.txt