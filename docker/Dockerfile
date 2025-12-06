FROM python:3.14.1-slim AS build
WORKDIR /opt/memebot/

# Install requirements.
COPY requirements.txt requirements.txt
RUN \
    apt-get update -y && \
    # gcc is required to build package aiohttp (https://docs.aiohttp.org/en/stable/) required by discord.py
    apt-get install --no-install-recommends -y gcc=4:14.2.0-1 && \
    # Remove apt lists
    rm -rf /var/lib/apt/lists/*

# Set up venv.
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN python3 -m pip install --no-cache-dir -r requirements.txt

FROM build AS build-test
COPY tests tests
RUN python3 -m pip install --no-cache-dir -r tests/requirements.txt

# Prepare run image.
FROM python:3.14.1-slim AS run-base
WORKDIR /opt/memebot/
ENV PATH="/opt/venv/bin:$PATH"
COPY memebot memebot
COPY main.py main.py
ENTRYPOINT ["python3", "main.py"]

# Run release build.
FROM run-base AS release
COPY --from=build /opt/venv /opt/venv

# Run test build.
FROM run-base AS test
COPY tests tests
COPY --from=build-test /opt/venv /opt/venv
