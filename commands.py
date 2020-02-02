import datetime
import io
from collections import defaultdict
from string import ascii_lowercase as alphabet
from threading import Lock
from typing import List, Callable, Union, ValuesView, KeysView

import discord

from lib import constants

# TODO: replace message saving temp solution with something better
message_lock = Lock()

# noinspection PyUnusedLocal
class Commands:
    """
    Manages all user-facing commands. The reason this is done as a class instead of just loose functions is so that
    the commands() method can be near the top of the file, so programmers remember to add their command to the
    dictionary. If this causes enough ire, it can easily be refactored.
    """

    client: discord.Client = None
    command_message: discord.Message = None

    @staticmethod
    def get_command_by_name(command: str) -> Callable[[List[str]], 'CommandOutput']:
        """
        Backbone of the command interface. Entries should be formatted as: ::

            '!command': function

        The function should be defined further down in this class as a static method.
        All functions must take in only a list of strings as their argument,
        and return a dictionary which represents keyword argument pairs to be used by
        channel.send()

        :return: A function that executes the requested command
        """
        return defaultdict(lambda: Commands.help, {
            '!hello': Commands.hello,
            '!poll': Commands.poll,
            '!role': Commands.role
        })[command]

    @staticmethod
    async def help(args: List[str]) -> 'CommandOutput':
        """
        Default command, lists all possible commands and a short description of each.
        :param args: Ignored
        :return: A formatted list of all commands
        """
        return CommandOutput().add_text("""Commands:
        `!help`  - Runs this command
        `!hello` - Prints "Hello!"
        `!poll`  - Runs a simple poll
        `!role`  - Manages mentionable roles""")

    @staticmethod
    async def hello(args: List[str]) -> 'CommandOutput':
        """
        Prints "Hello!" on input "!hello"
        :param args: ignored
        :return: The string "Hello!"
        """
        return CommandOutput().add_text("Hello!")

    @staticmethod
    async def poll(args: List[str]) -> 'CommandOutput':
        question, *options = args
        embed = discord.Embed(
            title=':bar_chart: **New Poll!**',
            description=f'_{question}_',
            color=constants.COLOR,
            timestamp=datetime.datetime.utcnow()
        )
        emojis = []
        if len(options) < 2 or options in (['yes', 'no'], ['no', 'yes'], ['yea', 'nay']):
            embed.add_field(name=':thumbsup:', value=':)' if len(options) < 1 else options[0]).add_field(
                name=':thumbsdown:', value=':(' if len(options) < 2 else options[1])
            emojis = [':thumbsup:', ':thumbsdown:']
        else:
            for i in range(len(options)):
                emoji = f':regional_indicator_{alphabet[i]}:'
                embed.add_field(name=emoji, value=options[i])
                emojis.append(emoji)

        # create side effect to react to poll after it is posted
        async def react(message: discord.Message):
            for emote in emojis:
                await message.add_reaction(constants.EMOJI_MAP[emote])

        SideEffects.task = react

        return CommandOutput().add_embed(embed)

    @staticmethod 
    async def role(args: List[str]) -> 'CommandOutput':
        """
        Controls creating, joining, and leaving permissonless mentionable
        roles. These roles are intended to serve as "tags" to allow mentioning
        multiple users at once.

        !role create <role>: Creates <role> 
        !role join <role>: Adds caller to <role> 
        !role leave <role>: Removes caller from <role> 
        !role delete <role>: Deletes <role> if <role> has no members
        !role list <role>: Lists members of <role>

        Note that because role names are not unique, these commands will act 
        on the first instance (hierarchically) of a role with name <role>

        :param args: Arguments to command. Must be of length 2
        :return: Message with result of creating, joining, or leaving role.
        """

        help_message = CommandOutput().add_text('`!role`: Self-contained '
        'role management\n\n'
        '`!role create <role>`: Creates <role>\n'
        '`!role join <role>`: Adds caller to <role>\n'
        '`!role leave <role>`: Removes caller from <role>\n'
        '`!role delete <role>`: Deletes <role> if <role> has no members\n'
        '`!role list <role>`: Lists members of <role>'
        )

        # ensure proper usage
        if len(args) != 2: 
            return help_message
 
        action, target_name = args
        failure_msg = lambda msg='': CommandOutput().add_text(
                f'Failed to {action} role {target_name}! {msg}')
        # TODO: factor this out to be common to all commands
        permission_msg = CommandOutput().add_text(
                f'Memebot doesn\'t have permission to {action} role '
                f'{target_name}. Are you sure you configured Memebot\'s '
                'permissions correctly?')

        # ensure access to command message
        if Commands.command_message is None:
            print('!role: Could not get command message')
            return failure_msg()

        # get guild and author from command message
        guild = Commands.command_message.guild

        if guild is None:
            print('!role: Could not get Guild')
            return failure_msg()

        author = guild.get_member(Commands.command_message.author.id)
        reason_str = f'Performed through MemeBot by {author.name}'

        if author is None:
            print('!role: Could not get author')
            return failure_msg()

        # fetch first instance of role with name 'target'
        target_role = None
        for role in guild.roles:
            if role.name == target_name:
                target_role = role
                break

        # handle create
        if action == 'create':
            if target_role is not None:
                return failure_msg(
                        f'The role `@{target_name}` already exists!')
            
            new_role = None

            try:
                new_role = await guild.create_role(name=target_name, 
                        mentionable=True, reason=reason_str)

                if new_role is None:
                    return failure_msg()
            except discord.Forbidden:
                print(f'!role: Forbidden: create_role( {target_name} )')
                return permission_msg
            except discord.HTTPException:
                print(f'!role: Failed API call create_role( {target_name} )')
                return failure_msg()
            except discord.InvalidArgument:
                print('!role: Invalid arguments to call '
                        f'create_role( {target_name} )')
                return failure_msg()
                
            return CommandOutput().add_text(
                    f'Created new role {new_role.mention}!')
        
        # ensure role exists for remaining actions
        if target_role is None: 
            return failure_msg(f'The role `@{target_name}` was not found!')

        # handle remaining actions
        if action == 'join':
            try:
                await author.add_roles(target_role, reason=reason_str)
            except discord.Forbidden:
                print('!role: Forbidden: '
                        f'{author.name}.add_role( {target_name} )')
                return permission_msg
            except discord.HTTPException:
                print('!role: Failed API call '
                        f'{author.name}.add_role( {target_name} )')
                return failure_msg()

            return CommandOutput().add_text(
                    f'{author.name} successfully joined `@{target_name}`')

        elif action == 'leave':
            try:
                await author.remove_roles(target_role, reason=reason_str)
            except discord.Forbidden:
                print('!role: Forbidden '
                        f'{author.name}.remove_role( {target_name} )')
                return permission_msg
            except discord.HTTPException:
                print('!role: Failed API call '
                        f'{author.name}.remove_role( {target_name} )')
                return failure_msg()

            return CommandOutput().add_text(
                    f'{author.name} successfully left `@{target_name}`')

        elif action == 'delete':
            # ensure role is empty before deleting
            if len(target_role.members) == 0:
                try:
                    await target_role.delete(reason=reason_str)
                except discord.Forbidden:
                    print(f'!role: Forbidden: delete( {target_name} )')
                    return permission_msg
                except discord.HTTPException:
                    print('!role: Failed API call delete( {target_name} )')
                    return failure_msg()

                return CommandOutput().add_text(
                        f'Deleted role `@{target_name}`!')
            else:
                return failure_msg('Roles must have no members to be deleted')

        elif action == 'list':
            members_string = ''
            if len(target_role.members) == 0:
                members_string = f'Role `@{target_name}` has no members!'
            else:
                members_string = f'Members of `@{target_name}`:'

                for member in target_role.members:
                    if member.nick is not None:
                        members_string += f'\n- {member.nick} ({member.name})'
                    else:
                        members_string += f'\n- {member.name}'

            return CommandOutput().add_text(members_string)

        # send help message if invalid action 
        return help_message
        

    @staticmethod
    async def execute(command: str, args: List[str], client: discord.Client = None, message: discord.Message = None) -> 'CommandOutput':
        """
        Executes the command with the given args
        :param command: The !command to execute
        :param args: The arguments for the command
        :param client: The Discord client being used (MemeBot)
        :param message: The Discord message which triggered the command execution
        :return: The result of running command with args, formatted as a CommandOutput object to be sent to Discord
        """
        if Commands.client is None:
            if client is None:
                raise ValueError("The Commands module does not have access to a client!")
            else:
                Commands.client = client
        #TODO: replace temp message saving solution with something better
        if message is None:
            raise ValueError("The Commands module does not have access to the command message!")
        message_lock.acquire()
        Commands.command_message = message
        r = await Commands.get_command_by_name(command)(args)
        message_lock.release()
        return r


class SideEffects:
    """
    This is a class for when a command needs extra information from the Discord client after
    the command has already been run (to execute certain operations from "beyond the grave"
    Since commands are asynchronous, this works by having the command leave a little job
    in the ``task`` variable. Upon returning control to memebot and sending the output of
    the command to Discord, memebot will send over any possibly needed data through the
    ``borrow()`` function, which will then trigger the execution of ``task``.

    I am going to guess this is a temporary measure, and there is probably a much better way
    to do this.
    """
    task = None

    @staticmethod
    async def borrow(message: discord.Message):
        if SideEffects.task is not None:
            await SideEffects.task(message)
        SideEffects.task = None


class CommandOutput:
    """
    A class to standardize building a command output. Methods correspond to
    kwargs in discord.message.message.channel.send()
    """
    CONTENT = 'content'
    EMBED = 'embed'
    TTS = 'tts'
    FILE = 'file'
    FILES = 'files'
    LIFETIME = 'delete_after'
    NONCE = 'nonce'

    def __init__(self, kwargs: dict = None):
        if type(kwargs) is dict:
            self.kwargs = kwargs
        else:
            # dict to hold keyword arguments
            self.kwargs = {}

    def add_content(self, content: str) -> 'CommandOutput':
        """
        Adds content to a message being sent to discord. This can plainly be regarded as
        a regular text message
        :param content: The text to be added to the output
        :return: self
        """
        self.kwargs[CommandOutput.CONTENT] = content
        return self

    def add_text(self, text: str) -> 'CommandOutput':
        """
        Wrapper method for add_content just in case the name isn't clear
        :param text: The text to send
        :return: self
        """
        return self.add_content(text)

    def add_embed(self, embed: discord.Embed) -> 'CommandOutput':
        """
        Adds an embed to a message being sent to discord
        :param embed: The embed object to add to the message
        :return: self
        """
        self.kwargs[CommandOutput.EMBED] = embed
        return self

    def set_tts(self, tts: bool = True) -> 'CommandOutput':
        """
        Enables or disables text-to-speech for a message being sent to discord
        :param tts: Tells if the content of this message will be read aloud (Default: True)
        :return: self
        """
        self.kwargs[CommandOutput.TTS] = tts
        return self

    def add_file(self, file: Union[str, io.BufferedIOBase], file_name: str = None,
                 spoiler: bool = False) -> 'CommandOutput':
        """
        Adds a file to a message that is being sent to discord
        :param file: The file being sent. Can either be a path (string) or file-like object (io.BufferedIOBase)
        :param file_name: An optional, alternate name to the file
        :param spoiler: Tells whether or not the file should be spoiler'd (Default: False)
        :return: self
        """
        self.kwargs[CommandOutput.FILE] = discord.File(fp=file, filename=file_name, spoiler=spoiler)
        return self

    def add_files(self, files: List[Union[str, io.BufferedIOBase]]) -> 'CommandOutput':
        """
        Adds multiple files at once to a message being sent to Discord. !! Maximum of 10 files !!
        :param files: list of file paths or file-like objects
        :return: self
        :raises ValueError if there is an attempt to add more than 10 files to the output
        """
        # check if, after this operation, there will be more than 10 files in the message
        total_files = (len(self.kwargs[CommandOutput.FILES]) if CommandOutput.FILES in self.kwargs else 0) + len(files)
        if total_files > 10:
            raise ValueError(f"Cannot send more than 10 files! (tried to send total of {total_files}")
        # if there are no files stored in the output, initialize it in the kwargs dict
        if total_files == len(files):
            self.kwargs[CommandOutput.FILES] = []
        self.kwargs[CommandOutput.FILES] += files
        return self

    def set_time_to_delete(self, time_to_delete: float) -> 'CommandOutput':
        """
        Wrapper for set_lifetime()
        :param time_to_delete: The time (in seconds) after which this message will be deleted after sending
        :return: self
        """
        return self.set_lifetime(time_to_delete)

    def set_lifetime(self, lifetime: float) -> 'CommandOutput':
        """
        Sets the output to expire (be deleted) a certain time after being posted
        :param lifetime: The expiration time of this message, in seconds
        :return: self
        """
        self.kwargs[CommandOutput.LIFETIME] = lifetime
        return self

    def __str__(self) -> str:
        return str(self.kwargs)

    def __contains__(self, item: str) -> bool:
        return item in self.kwargs

    def __add__(self, other: 'CommandOutput') -> 'CommandOutput':
        return CommandOutput(self.kwargs.update(other.kwargs))

    def keys(self) -> KeysView[str]:
        return self.kwargs.keys()

    def values(self) -> ValuesView:
        return self.kwargs.values()
