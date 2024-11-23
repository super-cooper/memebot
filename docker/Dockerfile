FROM python:3.13.0-slim as build
WORKDIR /opt/memebot/

# Install requirements.
COPY requirements.txt requirements.txt
RUN \
    apt-get update -y && \
    # gcc is required to build package aiohttp (https://docs.aiohttp.org/en/stable/) required by discord.py
    apt-get install --no-install-recommends -y gcc=4:10.2.1-1 && \
    # Remove apt lists
    rm -rf /var/lib/apt/lists/*

# Set up venv.
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN python3 -m pip install --no-cache-dir -r requirements.txt

FROM build as build-test
COPY tests tests
RUN python3 -m pip install --no-cache-dir -r tests/requirements.txt

# Prepare run image.
FROM python:3.13.0-slim as run-base
WORKDIR /opt/memebot/
ENV PATH="/opt/venv/bin:$PATH"
COPY memebot memebot
ENTRYPOINT ["python3", "memebot/main.py"]

# Run release build.
FROM run-base as release
COPY --from=build /opt/venv /opt/venv

# Run test build.
FROM run-base as test
COPY tests tests
COPY --from=build-test /opt/venv /opt/venv