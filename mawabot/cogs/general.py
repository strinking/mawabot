#
# cogs/general.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Holds general commands for self bot '''

from random import randint
import codecs
import re

import discord
from discord.ext import commands
import upsidedown

__all__ = [
    'setup',
]

class General:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        ''' Pong '''

        await ctx.message.edit(content='Pong!')

    @commands.command()
    async def roll(self, ctx, number: int = 10):
        ''' Gives a random number from 0 to the number given '''

        result = randint(0, number)
        await ctx.message.edit(content=f'Rolled: {result}')

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = General(bot)
    bot.add_cog(cog)
