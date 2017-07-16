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
import math
import random
import re

from mawabot import utils

import discord
from discord.ext import commands

DICE_REGEX = re.compile(r'(?:([0-9]+)?\s*d)?\s*([0-9]+)', re.IGNORECASE)
MATH_LOCALS = {name: getattr(math, name) for name in dir(math) if not name.startswith('_')}

class General:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    def _get_user_mention(self, name):
        if name.isdigit():
            id = int(name)
            user = self.bot.get_user(id)
        else:
            name = utils.normalize_caseless(name)
            user = discord.utils.find(lambda u: utils.normalize_caseless(u.name) == name, self.bot.users)
        return getattr(user, 'mention', '(No such user)')

    @staticmethod
    def _get_role_mention(guild, name):
        if name.isdigit():
            id = int(name)
            role = discord.utils.find(lambda r: r.id == id, guild.roles)
        else:
            name = name.lower()
            role = discord.utils.find(lambda r: r.name.lower() == name, guild.roles)
        return getattr(role, 'mention', '(No such role)')

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

    @commands.command()
    async def mention(self, ctx, *names: str):
        ''' Mentions the given user(s) in an embed '''

        if not names:
            return

        fut = ctx.message.delete()
        desc = '\n\n'.join((self._get_user_mention(name) for name in names))
        embed = discord.Embed(type='rich', description=desc)
        await ctx.send(embed=embed)
        await fut

    @commands.command()
    @commands.guild_only()
    async def rmention(self, ctx, *names: str):
        ''' Mentions the given role(s) in an embed '''

        if not names:
            return

        fut = ctx.message.delete()
        desc = '\n\n'.join((self._get_role_mention(ctx.guild, name) for name in names))
        embed = discord.Embed(type='rich', description=desc)
        await ctx.send(embed=embed)
        await fut
