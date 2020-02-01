FROM python:3.8.1-slim

# pull in required files
WORKDIR /home/memebot/
COPY . .

# set up virtual environment
ENV VIRTUAL_ENV "/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

# install dependencies
RUN python -m pip install -r requirements.txt

# run memebot
CMD ["python3", "main.py"]
