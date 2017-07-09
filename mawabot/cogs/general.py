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
import random
import re

from .. import calc

import discord
from discord.ext import commands

__all__ = [
    'setup',
]

DICE_REGEX = re.compile(r'(?:([0-9]+)?\s*d)?\s*([0-9]+)', re.IGNORECASE)

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
    async def roll(self, ctx, *, roll: str = ''):
        ''' "XdY" rolls X dice with Y sides '''

        if roll:
            match = DICE_REGEX.match(roll)
            if match is None:
                return

            dice = int(match[1]) if match[1] else 1
            sides = int(match[2])
        else:
            dice = 1
            sides = 6

        if dice == 1:
            result = random.randint(1, sides)
            await ctx.send(content=f'🎲 {result}')
        else:
            rolls = []
            total = 0
            for _ in range(dice):
                result = random.randint(1, sides)
                rolls.append(f'{result}')
                total += result

            rolls = ' + '.join(rolls)
            await ctx.send(content=f'🎲 {rolls} = {total}')

    @commands.command()
    async def calc(self, ctx, *, expr: str):
        ''' Evaluates a mathematical expression and prints the result '''

        fut = ctx.message.delete()
        embed = discord.Embed(type='rich')
        embed.set_author(name=expr)

        try:
            result = calc.parser.parse(expr)
            embed.description = f'= {result}'
            embed.color = discord.Color.teal()
        except:
            embed.description = 'Error parsing expression'
            embed.color = discord.Color.red()

        await ctx.send(embed=embed)
        await fut

    @commands.command()
    @commands.guild_only()
    async def nick(self, ctx, *, nickname: str = None):
        ''' Changes the user's nickname '''

        await ctx.guild.me.edit(nick=nickname)

    @commands.command()
    async def playing(self, ctx, *, playing: str = None):
        ''' Changes the user's current game '''

        if playing:
            game = discord.Game(name=playing)
        else:
            game = None

        await self.bot.change_presence(game=game)

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = General(bot)
    bot.add_cog(cog)
