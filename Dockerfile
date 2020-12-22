FROM python:3.9.1-slim

# pull in required files
WORKDIR /home/memebot/
COPY . .

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
CMD ["python3", "src/main.py"]
