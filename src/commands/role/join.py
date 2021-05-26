from typing import List

import discord

from commands import Command, CommandOutput, role


class Join(Command):
    """
    Join an existing Memebot-managed role
    """

    def __init__(self):
        super().__init__(
            name="join",
            description="Adds caller to <role>",
            long_description="Join an existing Memebot-managed role.",
            example_args="<role>"
        )

    async def exec(self, args: List[str], message: discord.Message) -> CommandOutput:
        if len(args) != 1:
            return self.fail()

        guild = message.guild
        author = guild.get_member(message.author.id)
        target_name = args[0].lower()
        target_role = role.find_role_by_name(target_name, message.guild)
        if target_role is None:
            return role.action_failure_message(self.name, target_name, f'The role `@{target_name}` was not found!')
        if author in target_role.members :
            return role.action_failure_message(self.name, target_role.name, f'User is already a member of `@{target_role.name}`.')

        try:
            await author.add_roles(target_role, reason=role.get_reason(author.name))
        except discord.Forbidden:
            print(f'!role: Forbidden: {author.name}.add_role( {target_role.name} )')
            return role.permission_failure_message(self.name, target_role.name)
        except discord.HTTPException:
            print(f'!role: Failed API call: {author.name}.add_role( {target_role.name} )')
            return role.action_failure_message(self.name, target_role.name)
        finally:
            return CommandOutput().set_text(f"{author.name} successfully joined `@{target_role.name}`")
