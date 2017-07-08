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

''' Has several commands that deal with messages '''

import logging

import discord
from discord.ext import commands

__all__ = [
    'setup',
]

MAX_DELETE_POSTS = 30

logger = logging.getLogger(__name__)

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
    async def embed(self, ctx, *, content: str):
        ''' Inserts the given message into an embed. '''

        embed = discord.Embed(type='rich', description=content)
        await ctx.message.edit(content='', embed=embed)

    @commands.command()
    async def quote(self, ctx, id: int, cid: int = 0):
        ''' Quotes the given post(s) '''

        fut = ctx.message.delete()
        if cid:
            channel = self.bot.get_channel(cid)
            if channel is None:
                logger.warn(f'Cannot find the channel with ID {cid}')
                return
        else:
            channel = ctx.channel
        await fut

        to_quote = await self._get_messages(channel, (id,))
        for msg in to_quote:
            embed = discord.Embed(type='rich', description=msg.content)
            embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
            embed.timestamp = msg.created_at
            await ctx.send(embed=embed)

    @commands.command()
    async def dump(self, ctx, *ids: int):
        ''' Outputs the literal contents of the given post(s) '''

        fut = ctx.message.delete()
        to_copy = await self._get_messages(ctx.channel, ids)
        for msg in to_copy:
            if msg.content:
                content = '\n'.join((
                    '```',
                    msg.content.replace("`", "'"),
                    '```',
                ))
            else:
                content = '(Message is empty)'

            embed = discord.Embed(type='rich', description=content)
            embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
            embed.timestamp = msg.created_at
            await self.bot._send(embed=embed)

            for embed in msg.embeds:
                await self.bot._send(embed=embed)

        await fut

    @commands.command()
    async def delet(self, ctx, posts: int = 1):
        ''' Deletes the last X posts you made, including the trigger '''

        if posts > MAX_DELETE_POSTS:
            logger.error((f'Asked to delete {posts} posts which is greater than '
                          f'the self-imposed limit of {MAX_DELETE_POSTS}'))
            return

        fut = ctx.message.delete()
        deleted = 0
        async for msg in ctx.channel.history():
            if msg.author == self.bot.user:
                await msg.delete()
                deleted += 1
                if deleted >= posts + 1:
                    break

        await fut

    @commands.command()
    async def purge(self, ctx, posts: int = 1):
        ''' Deletes the last X posts in the channel, not including the trigger. '''

        if posts > MAX_DELETE_POSTS:
            logger.error((f'Asked to delete {posts} posts which is greater than '
                          f'the self-imposed limit of {MAX_DELETE_POSTS}'))
            return

        async for msg in ctx.channel.history(limit=posts + 1):
            try:
                await msg.delete()
            except discord.errors.DiscordException as ex:
                logger.error(f'Cannot delete message {msg.id}: {ex}')

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Messages(bot)
    bot.add_cog(cog)
