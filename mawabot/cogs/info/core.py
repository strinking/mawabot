#
# cogs/info/core.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has several commands that get various pieces of information '''
import asyncio
import time

import discord
from discord.ext import commands

__all__ = [
    'General',
]

class General:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx):
        ''' Gets the uptime of this self-bot '''

        uptime = str(self.bot.uptime).split('.')[0]
        await ctx.message.edit(content=f'`{uptime}`')

    @commands.command()
    async def unixtime(self, ctx):
        ''' Gets the current UNIX timestamp '''

        await ctx.message.edit(content=f'`{time.time()}`')
