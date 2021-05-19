import typing

import discord

import memebot
from commands import Command, CommandOutput, role


class List(Command):
    """
    List all roles managed by Memebot, or all members of a role managed by Memebot.
    """

    def __init__(self):
        super().__init__("list", "List all roles managed by Memebot, or list all members of a role.", "[role]")

    def help_text(self) -> CommandOutput:
        return CommandOutput().set_text("List all roles managed by Memebot, or provide the name of a role and list "
                                        "all members of that role.")

    async def exec(self, args: typing.List[str], message: discord.Message) -> CommandOutput:
        if len(args) > 1:
            return self.fail()

        guild = message.guild

        if not args:
            roles = []
            can_manage = False
            # Memebot can manage all roles below its highest role.
            # Find that role and begin listing roles from that point onward.
            for role_obj in guild.roles[:0:-1]:  # Top-down, excluding @everyone
                if can_manage and role_obj.name != memebot.client.user.name:
                    roles.append(role_obj.name)
                elif memebot.client.user in role_obj.members:
                    can_manage = True
            output_list = list(sorted(roles))
            output_list.insert(0, "Roles managed through `!role` command:")
            return CommandOutput(content="\n- ".join(output_list))
        else:
            target_name = args[0].lower()
            target_role = role.find_role_by_name(target_name, message.guild)
            if target_role is None:
                return role.action_failure_message(self.name, target_name, f'The role `@{target_name}` was not found!')
            if not target_role.members:
                return CommandOutput().set_text(f'Role `@{target_role.name}` has no members!')

            member_names = []
            for member in target_role.members:
                if member.nick is not None:
                    member_names.append(f'{member.nick} ({member.name})')
                else:
                    member_names.append(member.name)

            member_names.sort()
            member_names.insert(0, f'Members of `@{target_role.name}`:')

            return CommandOutput(content='\n- '.join(member_names))
