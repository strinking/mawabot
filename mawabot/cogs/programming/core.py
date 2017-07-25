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
        ''' Evaluates an arbitrary Python command '''

        logger.info(f'Running python: "{command}"')
        embed = discord.Embed(type='rich')
        embed.set_author(name=command)
        try:
            exec(command)
            embed.color = discord.Color.green()
            embed.description = 'Success'
            await ctx.send(embed=embed)
        except Exception as ex:
            embed.color = discord.Color.red()
            embed.description = f'{ex.__class__.__name__}: {ex}'
            await ctx.send(embed=embed)

    @commands.command()
    async def eval(self, ctx, *, expr: str):
        ''' Evaluates an abritrary Python expression '''

        logger.info(f'Evaluating python: "{expr}"')
        embed = discord.Embed(type='rich')
        embed.set_author(name=expr)
        try:
            result = eval(expr)
            embed.color = discord.Color.teal()
            embed.description = f'`{result!r}`'
        except Exception as ex:
            embed.color = discord.Color.red()
            embed.description = f'{ex.__class__.__name__}: {ex}'

        await ctx.send(embed=embed)
