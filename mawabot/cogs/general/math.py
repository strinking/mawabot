#
# cogs/general/math.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Holds commands related to mathematics '''

import math

import discord
from discord.ext import commands

MATH_LOCALS = {name: getattr(math, name) for name in dir(math) if not name.startswith('_')}

__all__ = [
    'Math',
]

class Math:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def calc(self, ctx, *, expr: str = '(nothing)'):
        ''' Evaluates a mathematical expression and prints the result '''

        fut = ctx.message.delete()
        embed = discord.Embed(type='rich')
        embed.set_author(name='Calculator:')
        lines = [
            '**Input:**',
            expr.replace('*', r'\*'),
            '',
            '**Output:**',
        ]

        try:
            result = eval(expr, MATH_LOCALS)
            if type(result) == float:
                lines.append(f'{result:.4f}')
            else:
                lines.append(str(result))
            embed.color = discord.Color.teal()
        except Exception as ex:
            lines.append(f'Error: {ex}')
            embed.color = discord.Color.red()

        embed.description = '\n'.join(lines)
        await ctx.send(embed=embed)
        await fut
