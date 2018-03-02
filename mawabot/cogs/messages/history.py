#
# cogs/history.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has commands related to fetching channel history '''
import asyncio
import logging

import discord
from discord.ext import commands

MAX_HIST_DUMP = 100

logger = logging.getLogger(__name__)

class History:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _to_bool(value):
        return value.lower() in ('true', 'yes', '1')

    async def _hist_quote(self, num, msg):
        embed = discord.Embed(type='rich', description=msg.content)
        embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
        embed.set_footer(text=f'Message #{num}')
        embed.timestamp = msg.edited_at or msg.created_at
        await self.bot._send(embed=embed)

    async def _output_id(self, num, msg):
        await self.bot._send(content=f'`{num:2}: {msg.id}`')

    @commands.command()
    async def hist(self, ctx, limit: int, *args: str):
        ''' Fetches history from a channel. Accepts parameters to modify the result. '''

        if limit < 0:
            raise ValueError(f"Limit ({limit}) is negative.")
        elif limit > MAX_HIST_DUMP:
            raise ValueError(f"Limit ({limit}) is larger than the maximum, {MAX_HIST_DUMP}.")

        call = self._hist_quote
        params = {'limit': limit + 1}

        for arg in args:
            param, value = arg.split('=')
            param = param.lower()

            if param in ('before', 'after', 'around'):
                params[param] = discord.utils.snowflake_time(int(value))
                params['limit'] -= 1
            elif param == 'reverse':
                params[param] = self._to_bool(value)
            elif param == 'ids':
                if self._to_bool(value):
                    call = self._output_id
            else:
                raise ValueError(f"Unknown parameter: {param}")

        await asyncio.gather(
            self.bot._send(content=f'**{limit} messages from {ctx.channel.mention}:**'),
            ctx.message.delete(),
        )

        i = 0
        # Note: not using enumerate() since it doesn't work with async-iterators
        async for msg in ctx.channel.history(**params):
            if msg != ctx.message:
                await asyncio.gather(
                    call(i, msg),
                    asyncio.sleep(0.2),
                )
                i += 1

        await self.bot._send(content=f'Done running `{ctx.message.content}`')

    @commands.command()
    async def quote(self, ctx, start_id: int, count: int = 1, cid: int = 0):
        ''' Quotes the given post(s) '''

        await ctx.message.delete()
        if cid:
            channel = self.bot.get_channel(cid)
            if channel is None:
                logger.warning(f'Cannot find the channel with ID {cid}')
                return
        else:
            channel = ctx.channel

        builders = HistoryBuilder()
        after = discord.utils.snowflake_time(start_id)
        async for message in channel.history(after=after, limit=count):
            builders.append(message)

        print(builders)
        assert builders

        for embed in builders.build_embeds():
            await channel.send(embed=embed)

class MessageBuilder:
    __slots__ = (
        'author',
        'timestamp',
        'content',
        'attachments',
    )

    def __init__(self, message):
        self.author = message.author
        self.timestamp = message.created_at
        self.content = [message.content]
        self.attachments = list(message.attachments)

    def append(self, message):
        assert self.author == message.author
        self.content.append(message.content)
        self.attachments += message.attachments

    def append_or_new(self, message):
        if self.author == message.author:
            self.append(message)
            return True, self
        else:
            return False, MessageBuilder(message)

    def build_embed(self):
        embed = discord.Embed(type='rich', description='\n'.join(self.content))
        embed.set_author(name=self.author.display_name, icon_url=self.author.avatar_url)
        embed.timestamp = self.timestamp

        if self.attachments:
            urls = '\n'.join(attach.url for attach in self.attachments)
            embed.add_field(name='Attachments:', value=urls)

        return embed

    def __repr__(self):
        return f"<MessageBuilder author={self.author!r}, content={self.content!r}, attachments={self.attachments!r}>"

class HistoryBuilder:
    __slots__ = (
        'builders',
    )

    def __init__(self):
        self.builders = []

    def append(self, message):
        if self.builders:
            new, builder = self.builders[-1].append_or_new(message)
            if new:
                self.builders.append(builder)
        else:
            self.builders.append(MessageBuilder(message))

    def build_embeds(self):
        return [builder.build_embed() for builder in self.builders]

    def __bool__(self):
        return bool(self.builders)

    def __repr__(self):
        return f"<HistoryBuilder {self.builders!r}>"
