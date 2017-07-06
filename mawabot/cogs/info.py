#
# cogs/info.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has several commands that get guild information '''
import re

import discord
from discord.ext import commands

__all__ = [
    'setup',
]

EMOJI_REGEX = re.compile(r'<:([A-Za-z~\-0-9]+):([0-9]+)>')

class Info:
    __slots__ = (
        'bots',
    )

    def __init__(self, bot):
        self.bot = bot

    # Commands
    @commands.command
    async def emoji(self, ctx, *args: str):
        for arg in args:
            match = EMOJI_REGEX.match(arg)
            if match:
                await ctx.send(f'Emoji: `{match[1]}`\nID: `{match[2]}`')
            else:
                try:
                    name = unicodedata.name(arg)
                    await ctx.send(f'Unicode name: `{name}`\nOrd: `{ord(name)}`')
                except:
                    self.logger.warn(f'Not an emoji: {arg}')

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Guild(bot)
    bot.add_cog(cog)
