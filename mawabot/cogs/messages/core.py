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
import asyncio
import json
import logging

import discord
from discord.ext import commands

MAX_DELETE_POSTS = 80

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

    @staticmethod
    async def _hit(ctx, content):
        if content is not None:
            await ctx.send(content=content, delete_after=0)

    # Commands
    @commands.command()
    async def hit(self, ctx, *, content: str = None):
        ''' Sends the given message and then immediately deletes it '''

        await asyncio.gather(
            self._hit(ctx, content),
            ctx.message.delete(),
        )

    @commands.command()
    async def delay(self, ctx, seconds: float, *, content: str):
        ''' Sends the given message after the specified number of seconds '''

        logger.info(f'Queued up delayed message for {seconds} seconds from now')
        await asyncio.gather(
            asyncio.sleep(seconds),
            ctx.message.delete(),
        )
        logger.info(f'Posting delayed message: {content}')
        await ctx.send(content=content)

    @commands.command()
    async def embed(self, ctx, *, content: str):
        ''' Inserts the given message into an embed. '''

        try:
            args = json.loads(content)
            embed = discord.Embed(**args)
        except:
            embed = discord.Embed(type='rich', description=content)

        await asyncio.gather(
            ctx.send(embed=embed),
            ctx.message.delete(),
        )

    @commands.command()
    async def quote(self, ctx, id: int, cid: int = 0):
        ''' Quotes the given post(s) '''

        tasks = [ctx.message.delete()]
        if cid:
            channel = self.bot.get_channel(cid)
            if channel is None:
                logger.warning(f'Cannot find the channel with ID {cid}')
                return
        else:
            channel = ctx.channel

        to_quote = await self._get_messages(channel, (id,))
        for msg in to_quote:
            embed = discord.Embed(type='rich', description=msg.content)
            embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
            embed.timestamp = msg.created_at

            if msg.attachments:
                urls = '\n'.join(attach.url for attach in msg.attachments)
                embed.add_field(name='Attachments:', value=urls)
            tasks.append(ctx.send(embed=embed))
            tasks.append(self.bot.output_send(embed=embed))
        await asyncio.gather(*tasks)

    @commands.command()
    async def dump(self, ctx, *ids: int):
        ''' Outputs the literal contents of the given post(s) '''

        tasks = [ctx.message.delete()]
        to_copy = await self._get_messages(ctx.channel, ids)
        for msg in to_copy:
            if msg.content:
                content = '\n'.join((
                    'Plain:',
                    '```',
                    msg.content.replace("`", "'"),
                    '```',
                    '',
                    'Chars:',
                    '```',
                    ' '.join(f'{ord(c):02x}' for c in msg.content),
                    '```',
                ))
            else:
                content = '(Message is empty)'

            embed = discord.Embed(type='rich', description=content)
            embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
            embed.timestamp = msg.edited_at or msg.created_at

            if msg.attachments:
                urls = '\n'.join(attach.url for attach in msg.attachments)
                embed.add_field(name='Attachments:', value=urls)
            tasks.append(self.bot.output_send(embed=embed))
            tasks += [self.bot.send(embed=embed) for embed in msg.embeds]
        await asyncio.gather(*tasks)

    @commands.command(aliases=['delet'])
    async def delete(self, ctx, posts: int = 1):
        ''' Deletes the last X posts you made, including the trigger '''

        if posts > MAX_DELETE_POSTS:
            logger.error((f'Asked to delete {posts} posts which is greater than '
                          f'the self-imposed limit of {MAX_DELETE_POSTS}'))
            return

        tasks = [ctx.message.delete()]
        deleted = 0
        async for msg in ctx.channel.history():
            if msg.author == self.bot.user:
                tasks.append(msg.delete())
                deleted += 1
                if deleted >= posts + 1:
                    break

        await asyncio.gather(*tasks)

    @commands.command()
    async def purge(self, ctx, posts: int = 1):
        ''' Deletes the last X posts in the channel '''

        if posts > MAX_DELETE_POSTS:
            logger.error((f'Asked to delete {posts} posts which is greater than '
                          f'the self-imposed limit of {MAX_DELETE_POSTS}'))
            return

        tasks = []
        async for msg in ctx.channel.history(limit=posts + 1):
            tasks.append(msg.delete())

        await asyncio.gather(*tasks)
