#
# cogs/programming.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has commands for programming '''
import logging

import discord
from discord.ext import commands

__all__ = [
    'setup',
]

logger = logging.getLogger(__file__)

class Programming:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def exec(self, ctx, *, command: str):
        ''' Allows arbitrary execution of Python code '''

        logger.info(f'Running python: "{command}"')
        result = eval(command)
        if result is not None:
            embed = discord.Embed(type='rich', description=repr(result))
            embed.set_author(name=command)
            await ctx.send(embed=embed)

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Programming(bot)
    bot.add_cog(cog)
