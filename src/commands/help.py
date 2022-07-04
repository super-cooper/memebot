import contextlib
import math

import discord.ext.commands


class MessageCache(discord.abc.Messageable):
    """
    Dummy class which disguises itself as a destination for a message to be sent.

    This is because HelpCommands by default do not include a mechanism for simply
    generating the help message, only to generate and send it all in the same function.
    This class is injected into the `send_pages` function of a HelpCommand so that
    the message is not actually sent, but stored in an internal buffer.
    """

    def __init__(self):
        self.message_text = None

    async def _get_channel(self):
        pass

    async def send(self, content=None, *, tts=False, embed=None, file=None,
                   files=None, delete_after=None, nonce=None,
                   allowed_mentions=None, reference=None,
                   mention_author=None):
        self.message_text = content


class Help(discord.ext.commands.DefaultHelpCommand):
    """
   Output general help text for each command.
   """

    def __init__(self, **options):
        super(Help, self).__init__(
            no_category="Commands",
            paginator=discord.ext.commands.Paginator(max_size=math.inf),
            **options
        )
        self.cache_next = False
        self.cache = MessageCache()

    def set_cache_next(self):
        self.cache_next = True

    def unset_cache_next(self):
        self.cache_next = False

    def get_ending_note(self) -> str:
        return f"Type {self.clean_prefix}{self.invoked_with} <command> for more info on a command."

    async def subcommand_not_found(self, command: discord.ext.commands.Command, string: str) -> str:
        # We will fake sending out the help text, and cache it in an internal buffer.
        # We do this because the help text is generated in the same function in which it is sent,
        # so there is no way to just gather the help message.
        # In order to get around this, we send a fake `Messageable` interface to "send" the
        # help text to, which is just an internal buffer managed by this class.
        self.set_cache_next()
        with contextlib.ExitStack() as stack:
            # Ensure that the cache is turned off regardless of whether caching the help text fails
            stack.callback(self.unset_cache_next)
            if isinstance(command, discord.ext.commands.Group):
                await self.send_group_help(command)
            else:
                await self.send_command_help(command)
        return f"{super(Help, self).subcommand_not_found(command, string)}\n{self.cache.message_text}"

    async def prepare_help_command(self, ctx: discord.ext.commands.Context, command: discord.ext.commands.Command):
        """
        Override which injects additional error information to the help output, if the help command was triggered
        by a user error
        """
        if error := ctx.kwargs.get("error"):
            prefix = self.paginator.prefix
            self.paginator.prefix = None 
            await super(Help, self).prepare_help_command(ctx, command)
            self.paginator.add_line(f"{str(error)}\n{prefix}")
            self.paginator.prefix = prefix
        else:
            await super(Help, self).prepare_help_command(ctx, command)

    def get_destination(self) -> discord.abc.Messageable:
        if self.cache_next:
            return self.cache
        else:
            return super(Help, self).get_destination()
