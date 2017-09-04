#
# cogs/general/core.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has general or miscellaneous commands '''

import discord
from discord.ext import commands

from mawabot import utils

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
    async def ping(self, ctx):
        ''' Pong '''

        await ctx.message.edit(content='Pong!')

    @commands.command()
    @commands.guild_only()
    async def nick(self, ctx, *, nickname: str = None):
        ''' Changes the user's nickname '''

        if nickname:
            content = f'Set nickname to `{nickname}`'
        else:
            content = 'Removed nickname'

        await ctx.guild.me.edit(nick=nickname)
        await ctx.send(content=content)

    @commands.command()
    async def playing(self, ctx, *, playing: str = None):
        ''' Changes the user's current game '''

        if playing:
            game = discord.Game(name=playing)
            content = f'Set game to `{playing}`'
        else:
            game = None
            content = f'Unset game'

        await self.bot.change_presence(game=game)
        await ctx.message.edit(content=content)

    def _get_user_mention(self, name):
        if name.isdigit():
            id = int(name)
            user = self.bot.get_user(id)
        else:
            name = utils.normalize_caseless(name)
            user = discord.utils.find(lambda u: utils.normalize_caseless(u.name) == name, self.bot.users)
        return getattr(user, 'mention', '(No such user)')

    @commands.command()
    async def mention(self, ctx, *names: str):
        ''' Mentions the given user(s) in an embed '''

        if not names:
            return

        fut = ctx.message.delete()
        desc = '\n\n'.join(map(self._get_user_mention, names))
        embed = discord.Embed(type='rich', description=desc)
        await ctx.send(embed=embed)
        await fut

    def _get_channel_mention(self, name, guild=None):
        if name.isdigit():
            id = int(name)
            chan = self.bot.get_channel(id)
        else:
            name = utils.normalize_caseless(name)
            channels = guild.channels if guild else self.bot.get_all_channels()
            chan = discord.utils.find(lambda c: utils.normalize_caseless(c.name) == name, channels)
        return getattr(chan, 'mention', '(No such channel)')

    @commands.command()
    async def cmention(self, ctx, *names: str):
        ''' Mentions the given channel(s) in an embed '''

        if not names:
            return

        fut = ctx.message.delete()
        desc = '\n\n'.join(self._get_channel_mention(name, ctx.guild) for name in names)
        embed = discord.Embed(type='rich', description=desc)
        await ctx.send(embed=embed)
        await fut

    def _get_role_mention(self, guild, name):
        if name.isdigit():
            id = int(name)
            role = discord.utils.find(lambda r: r.id == id, guild.roles)
        else:
            name = name.lower()
            role = discord.utils.find(lambda r: r.name.lower() == name, guild.roles)
        return getattr(role, 'mention', '(No such role)')

    @commands.command()
    @commands.guild_only()
    async def rmention(self, ctx, *names: str):
        ''' Mentions the given role(s) in an embed '''

        if not names:
            return

        fut = ctx.message.delete()
        desc = '\n\n'.join(self._get_role_mention(ctx.guild, name) for name in names)
        embed = discord.Embed(type='rich', description=desc)
        await ctx.send(embed=embed)
        await fut
