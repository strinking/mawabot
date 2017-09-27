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

import discord
from discord.ext import commands

MAX_HIST_DUMP = 100

class History:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _to_bool(value):
        return value.lower() in ('true', 'yes', '1')

    async def _quote(self, num, msg):
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

        call = self._quote
        params = {
            'limit': limit + 1,
        }

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

        fut = ctx.message.delete()
        await self.bot._send(content=f'**{limit} messages from {ctx.channel.mention}:**')
        await fut

        i = 0
        async for msg in ctx.channel.history(**params):
            if msg != ctx.message:
                await call(i, msg)
                await asyncio.sleep(0.2)
                i += 1
                # Note: not using enumerate() since it doesn't work with async-iterators

        await self.bot._send(content=f'Done running `{ctx.message.content}`')
