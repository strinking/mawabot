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

import discord
from discord.ext import commands

class Programming:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def exec(self, ctx, *, command: str):
        ''' Allows arbitrary execution of Python code '''

        self.logger.info(f'Running python: "{command}"')
        exec(command)

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Programming(bot)
    bot.add_cog(cog)
