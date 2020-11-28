from typing import List

import discord

from commands import Command, CommandOutput, role


class Delete(Command):
    """
    Delete a Memebot-managed role that has no members.
    """

    def __init__(self):
        super().__init__("delete", "Deletes <role> if <role> has no members.", "<role>")

    def help_text(self) -> CommandOutput:
        return CommandOutput().set_text("Delete a Memebot-managed role if, and only if, the role has no members.")

    async def exec(self, args: List[str], message: discord.Message) -> CommandOutput:
        if len(args) != 1:
            return self.fail()

        guild = message.guild
        author = guild.get_member(message.author.id)
        target_name = args[0].lower()
        target_role = role.find_role_by_name(target_name, message.guild)
        if target_role is None:
            return role.action_failure_message(self.name, target_name, f'The role `@{target_name}` was not found!')

        # Ensure the role is empty before deleting.
        if len(target_role.members) == 0:
            try:
                await target_role.delete(reason=role.get_reason(author.name))
            except discord.Forbidden:
                print(f'!role: Forbidden: delete( {target_name} )')
                return role.permission_failure_message(self.name, target_name)
            except discord.HTTPException:
                print(f'!role: Failed API call delete( {target_name} )')
                return role.action_failure_message(self.name, target_name)
            finally:
                return CommandOutput().set_text(f"Deleted role `@{target_name}`")
        else:
            return role.action_failure_message(self.name, target_name, 'Roles must have no members to be deleted.')
