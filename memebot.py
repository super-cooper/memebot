import discord


class MemeBot(discord.Client):

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message: discord.message.Message):
        if message.author == self.user:
            return
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
