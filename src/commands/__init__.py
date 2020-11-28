import importlib
import os

from . import registry, execution
from .command import Command, CommandOutput


def dynamically_register_commands() -> None:
    """
    Dynamically import all Command classes. Should only be called once outside of this function.
    """

    # Get all the packages located in the command package
    top_level_packages = [f.path for f in os.scandir(os.path.dirname(os.path.realpath(__file__))) if
                          f.is_dir() and not f.name.endswith("__pycache__")]

    for path in top_level_packages:
        pkg_name = os.path.basename(path)
        pkg = importlib.import_module(f"commands.{pkg_name}")
        cmd_class = getattr(pkg, pkg_name.capitalize())
        if issubclass(cmd_class, Command):
            cmd_class()


dynamically_register_commands()
registry.lock()
