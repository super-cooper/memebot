from memebot import MemeBot

client = MemeBot()

with open('client_token') as token_file:
    token = token_file.read()

client.run(token)
