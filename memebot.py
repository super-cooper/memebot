import discord


class MemeBot(discord.Client):
    """
    The main class that operates MemeBot, and directly controls all listeners
    """

    def __init__(self, **args):
        super().__init__(**args)

    async def on_ready(self):
        """
        Determines what the bot does as soon as it is logged into discord
        :return: None
        """
        print(f'Logged in as {self.user}')

    async def on_message(self, message: discord.message.Message):
        """
        Maintains all basic message listening commands that start with '!'
        :param message: The most recent message sent to the server
        :return: None
        """
        if message.author == self.user:
            return
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
