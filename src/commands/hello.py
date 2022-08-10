import discord.ext.commands


@discord.ext.commands.command(
    brief="Say \"hello\" to Memebot!",
    help="A simple ping command. Memebot should respond \"Hello!\""
)
async def hello(ctx: discord.ext.commands.Context) -> None:
    """
    Simple ping command. Say "hello" to Memebot!
    """
    # display_name is the nickname if it exists else the username
    await ctx.send(f"Hello, {ctx.author.display_name}!")
