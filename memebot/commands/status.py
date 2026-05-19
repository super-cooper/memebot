import discord
from opengsq.protocols.minecraft import Minecraft
from opengsq.protocols.source import Source

from memebot.lib import exception


def _parse_address(address: str, default_port: int) -> tuple[str, int]:
    if ":" in address:
        host, port_str = address.rsplit(":", 1)
        try:
            return host, int(port_str)
        except ValueError:
            raise exception.MemebotUserError(f"Invalid port in address: {port_str}") from None
    return address, default_port


@discord.app_commands.command()
async def status(
    interaction: discord.Interaction,
    address: str,
    game: str,
) -> None:
    """Check the status of a game server"""
    await interaction.response.defer()

    match game.lower():
        case "minecraft":
            host, port = _parse_address(address, 25565)
            try:
                server = Minecraft(host=host, port=port, timeout=5.0)
                info = await server.get_status()
                description = info["description"]
                if isinstance(description, dict):
                    description = description.get("text", "")
                await interaction.followup.send(
                    f"**{host}:{port}** — Online\n"
                    f"Players: {info['players']['online']}/{info['players']['max']}\n"
                    f"Version: {info['version']['name']}\n"
                    f"MOTD: {description}"
                )
            except Exception:
                await interaction.followup.send(f"**{host}:{port}** — Offline or unreachable")

        case "source":
            host, port = _parse_address(address, 27015)
            try:
                server = Source(host=host, port=port, timeout=5.0)
                info = await server.get_info()
                await interaction.followup.send(
                    f"**{host}:{port}** — Online\n"
                    f"Name: {info.name}\n"
                    f"Game: {info.game}\n"
                    f"Map: {info.map}\n"
                    f"Players: {info.players}/{info.max_players}"
                )
            except Exception:
                await interaction.followup.send(f"**{host}:{port}** — Offline or unreachable")

        case _:
            raise exception.MemebotUserError(f"Unknown game type: {game}. Use 'minecraft' or 'source'")
