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
        class_and_pkg_name = os.path.basename(path)
        # First we import the package
        pkg = importlib.import_module(f"commands.{class_and_pkg_name}")
        # Then, we retrieve the class from the imported package
        cmd_class = getattr(pkg, class_and_pkg_name.capitalize())
        # If the retrieved class is a Command, initialize it
        if issubclass(cmd_class, Command):
            cmd_class()


dynamically_register_commands()
registry.lock()
