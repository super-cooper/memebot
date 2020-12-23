import string
from typing import Dict

import discord

# official MemeBot color
COLOR: discord.Colour = discord.Colour(0x00BCD4)

# map of emoji names to unicode chars made for reactions
EMOJI_MAP: Dict[str, str] = {
    ':thumbsup:': '👍',
    ':thumbsdown:': '👎',
    ':0:': discord.PartialEmoji(name='0️⃣'),
    ':1:': discord.PartialEmoji(name='1️⃣'),
    ':2:': discord.PartialEmoji(name='2️⃣'),
    ':3:': discord.PartialEmoji(name='3️⃣'),
    ':4:': discord.PartialEmoji(name='4️⃣'),
}
# add regional indicator emoji to map
for c, i in zip(string.ascii_lowercase, range(len(string.ascii_lowercase))):
    EMOJI_MAP[f':regional_indicator_{c}:'] = chr(ord('🇦') + i)
