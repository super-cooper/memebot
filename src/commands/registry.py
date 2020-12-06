"""
The command registry maintains the state of command hierarchy globally. Commands must be registered at load time of the
Commands module, but the registry can be _read_ at any time.
"""
from typing import Dict, List, Tuple

from commands.command import Command

DEFAULT_COMMAND = "help"


class RegistryEntry:
    """
    Defines a simple structure to hold together global metadata for commands. Binds names to command objects, and
    describes one layer of command hierarchy.

    IMPORTANT: This class should never be used outside of this module!
    """

    def __init__(self, command: Command):
        """
        Globally binds a command to a name, so the command can be searched by its name. Also, initializes a registry of
        subcommands for the given command.
        :param command: The command that is being registered
        """
        self.command = command
        self.subcommand_registry: Dict[str, RegistryEntry] = {}

    def add_subcommand(self, subcommand: Command) -> None:
        """
        Adds a subcommand to this entry's subcommand registry
        :param subcommand: The subcommand to attach to this entry
        :raise KeyError: If subcommand has already been registered
        """
        if subcommand.name in self.subcommand_registry:
            raise KeyError(f"Subcommand {subcommand.name} already registered for {self.command.name}.")
        self.subcommand_registry[subcommand.name] = RegistryEntry(subcommand)


# Binds top-level commands to names
top_level_command_registry: Dict[str, RegistryEntry] = {}
# Tells if the command registry should be locked
registry_write_lock: bool = False


def register_top_level_command(command: Command) -> None:
    """
    Links a top-level command to a name. This should only be called at package-load time.
    :param command: The command to register
    :raise KeyError: If the command has already been registered
    :raise RuntimeError: If the command registry has been locked
    """
    if registry_write_lock:
        raise RuntimeError("The command registry can only be written to at package load time")
    if command.name in top_level_command_registry:
        raise KeyError(f"Command {command.name} already registered.")
    top_level_command_registry[command.name] = RegistryEntry(command)


def register_subcommand(parents: List[str], subcommand: Command) -> None:
    """
    Registers a command as a subcommand of another command. This should only be called at package-load time.
    :param parents: A list of commands that describe the hierarchy of commands that lead to the currrent subcommand
    being registered. The list should start with the top-level command, and list all commands that preclude the
    subcommand. For example, if the command being registered was "!foo bar baz bop", then registering the subcommand
    "bop" would look like ``register_subcommand(["foo", "bar", "baz"], <Command name="bop">)``
    :param subcommand: The subcommand to be registered
    :raise KeyError: If the subcommand has already been registered, or if any of the parents have not yet been
    registered
    :raise RuntimeError: If the command registry has been locked
    :raise ValueError: If no parents are provided
    """
    if registry_write_lock:
        raise RuntimeError("The command registry can only be written to at package load time")
    if not parents:
        raise ValueError("Attempted to register Subcomamnd without any parent Command(s)")
    top_level_name = parents[0]
    registry_entry = top_level_command_registry[top_level_name]
    for parent in parents[1:]:
        registry_entry = registry_entry.subcommand_registry[parent]
    if subcommand.name in registry_entry.subcommand_registry:
        raise KeyError(f"Subcommand {subcommand.name} already registered for {registry_entry.command.name}.")
    registry_entry.subcommand_registry[subcommand.name] = RegistryEntry(subcommand)


def lock():
    """
    Locks the registry to prevent any new writes
    :return True if the registry was not already locked, False otherwise
    """
    global registry_write_lock
    prev = registry_write_lock
    registry_write_lock = True
    return not prev


def parse_command_and_args(invocation: List[str]) -> Tuple[Command, List[str]]:
    """
    Takes a full message body and attempts to parse out if the message is a registered ommand. Aside from splitting the
    message into a list, the content should be otherwise _unmodified_.
    :param invocation: The full invocation of the command, including all arguments i.e. the full message body
    :raise ValueError: If invalid input.
    :return: A list representing the path to the found (sub)command
    """
    if not invocation:
        raise ValueError("Attempted to parse an empty message as a command")
    top_level_name = invocation[0][1:]
    if top_level_name not in top_level_command_registry:
        # If the desired command is not actually a command, return the default help text
        return get_default_command(), []
    registry_entry = top_level_command_registry[top_level_name]
    i = 1
    while i < len(invocation) and invocation[i] in registry_entry.subcommand_registry:
        registry_entry = registry_entry.subcommand_registry[invocation[i]]
        i += 1
    return registry_entry.command, invocation[i:]


def get_default_command() -> Command:
    return top_level_command_registry[DEFAULT_COMMAND].command
