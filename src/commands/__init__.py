# The order of imports here could create circular dependencies... It might be a good idea to finish the current
# machinery ASAP
from . import registry, execution
from .command import Command
from .command_output import CommandOutput
from commands.help import Help
from commands.hello import Hello
from commands.poll import Poll
from commands.role import Role
from commands.role.join import Join
from commands.role.create import Create
from commands.role.leave import Leave
from commands.role.list import List
from commands.role.delete import Delete


def dynamically_register_commands():
    """
    Dynamically import all Command classes. Should only be called once outside of this function.
    TODO This is to be implemented by #52
    """
    raise NotImplementedError()


# TODO Manually registering commands like this is a temporary solution which will be fixed by #52
cmd_help = Help()
registry.register_top_level_command(cmd_help)

cmd_hello = Hello()
registry.register_top_level_command(cmd_hello)

cmd_poll = Poll()
registry.register_top_level_command(cmd_poll)

cmd_role = Role()
cmd_role_create = Create()
cmd_role_delete = Delete()
cmd_role_join = Join()
cmd_role_leave = Leave()
cmd_role_list = List()
role_parents = ["role"]
registry.register_top_level_command(cmd_role)
registry.register_subcommand(role_parents, cmd_role_create)
registry.register_subcommand(role_parents, cmd_role_delete)
registry.register_subcommand(role_parents, cmd_role_join)
registry.register_subcommand(role_parents, cmd_role_leave)
registry.register_subcommand(role_parents, cmd_role_list)

registry.lock()
