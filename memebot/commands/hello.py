import discord


@discord.app_commands.command()
async def hello(interaction: discord.Interaction) -> None:
    """
    Simple ping command. Say "hello" to Memebot!
    """
    # display_name is the nickname if it exists else the username
    await interaction.response.send_message(f"Hello, {interaction.user.display_name}!")
