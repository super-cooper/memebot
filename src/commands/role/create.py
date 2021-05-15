from typing import List

import discord

from commands import Command, CommandOutput, role


class Create(Command):
    """
    Create a new memebot-managed role.
    """

    def __init__(self):
        super().__init__("create", "Creates <role>", "<role>")

    def help_text(self) -> CommandOutput:
        return CommandOutput().set_text("Create a new role to be managed by memebot.")

    async def exec(self, args: List[str], message: discord.Message) -> CommandOutput:
        if len(args) != 1:
            return self.fail()

        guild = message.guild
        author = guild.get_member(message.author.id)
        target_name = args[0].lower()
        if '@' in target_name:
            return role.action_failure_message(self.name, target_name, "Created roles cannot contain the `@` symbol.")
        target_role = role.find_role_by_name(target_name, message.guild)
        if target_role is not None:
            return role.action_failure_message(self.name, target_name, f'The role `@{target_name}` already exists!')

        new_role = None
        try:
            new_role = await guild.create_role(name=target_name, mentionable=True, reason=role.get_reason(author.name))
        except discord.Forbidden:
            print(f'!role: Forbidden: create_role( {target_name} )')
            return role.permission_failure_message(self.name, target_name)
        except discord.HTTPException:
            print(f'!role: Failed API call create_role( {target_name} )')
            return role.action_failure_message(self.name, target_name, '')
        except discord.InvalidArgument:
            print(f'!role: Invalid arguments to call create_role( {target_name} )')
            return role.action_failure_message(self.name, target_name, '')
        finally:
            return CommandOutput().set_text(f'Created new role {new_role.mention}!')
