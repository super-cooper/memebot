import discord.ext.commands


@discord.ext.commands.command(
    brief="Say \"hello\" to Memebot!",
    help="A simple ping command. Memebot should respond \"Hello!\""
)
async def hello(ctx: discord.ext.commands.Context):
    """
    Simple ping command. Say "hello" to Memebot!
    """
    author = ctx.author
    if author is not None:
        # display_name is the nickname if it exists else the username
        msg = f"Hello, {author.display_name}!"
    else:
        msg = "Hello!"
    await ctx.send(msg)
