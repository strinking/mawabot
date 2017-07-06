#
# cogs/messages.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has several commands that deal with messages and text '''

import discord
from discord.ext import commands

__all__ = [
    'setup',
]

class Messages:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    # Helper methods
    @staticmethod
    async def _get_messages(channel, ids):
        ''' Gets a list of the messages with the given IDs, in that order '''

        messages = []
        async for msg in channel.history():
            try:
                messages.append((ids.index(msg.id), msg))
            except ValueError:
                pass

        return map(lambda t: t[1], sorted(messages))

    # Commands
    @commands.command()
    async def hit(self, ctx, *, content: str):
        ''' Sends the given message and then immediately deletes it '''

        fut = ctx.message.delete()
        await ctx.send(content=content, delete_after=0)
        await fut

    @commands.command()
    async def quote(self, ctx, *ids: int):
        ''' Quotes the given post(s) '''

        fut = ctx.message.delete()
        to_quote = await self._get_messages(ctx.channel, ids)
        for msg in to_quote:
            embed = discord.Embed(type='rich', description=msg.content)
            embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
            embed.timestamp = msg.created_at
            await ctx.send(embed=embed)
        await fut

    @commands.command()
    async def dump(self, ctx, *ids: int):
        ''' Outputs the literal contents of the given post(s) '''

        fut = ctx.message.delete()
        to_copy = await self._get_messages(ctx.channel, ids)
        for msg in to_copy:
            content = '\n'.join((
                '```',
                msg.content.replace("`", "'"),
                '```',
            ))
            embed = discord.Embed(type='rich', description=content)
            embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
            embed.timestamp = msg.created_at
            await self.bot._send(embed=embed)

        await fut

    @commands.command()
    async def sep(self, ctx, posts_back: int = 1):
        ''' Adds a separator between posts, X posts back '''

        fut = ctx.message.delete()
        async for msg in ctx.channel.history(limit=posts_back + 1):
            pass

        if not msg.content.startswith('.\n'):
            content = '.\n' + msg.content
            await msg.edit(content=content)

        await fut

    @commands.command()
    async def delet(self, ctx, posts: int = 1):
        ''' Deletes the last X posts, including this one '''

        async for msg in ctx.channel.history(limit=posts + 1):
            await msg.delete()
        await ctx.message.delete()

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Messages(bot)
    bot.add_cog(cog)
