import importlib
import os
from typing import List

import config
from . import registry, execution
from .command import Command, CommandOutput


def dynamically_register_commands() -> None:
    """
    Dynamically import all Command classes. Should only be called once outside of this function.
    """

    def find_and_register_subcommands(top_level_command: Command, cmd_path: List[str]) -> None:
        # Do a depth-first search to register subcommands
        for subcommand in top_level_command.subcommands:
            if not (subcommand.requires_database and not config.database_enabled):
                registry.register_subcommand(cmd_path, subcommand)
                find_and_register_subcommands(subcommand, cmd_path + [subcommand.name])

    # Get all the packages located in the command package
    top_level_packages = [f.path for f in os.scandir(os.path.dirname(os.path.realpath(__file__))) if
                          f.is_dir() and not f.name.endswith("__pycache__")]

    for path in top_level_packages:
        class_and_pkg_name = os.path.basename(path)
        # First we import the package
        pkg = importlib.import_module(f"commands.{class_and_pkg_name}")
        # Then, we retrieve the class from the imported package
        cmd_class = getattr(pkg, class_and_pkg_name.capitalize())
        # If the retrieved class is a Command, initialize it
        if issubclass(cmd_class, Command):
            instance = cmd_class()
            # Registration machinery:
            # If the command is a top-level command and meets configuration requirements
            if type(cmd_class.parent) is Command and not (instance.requires_database and not config.database_enabled):
                registry.register_top_level_command(instance)
                find_and_register_subcommands(instance, [instance.name])


dynamically_register_commands()
registry.lock()
