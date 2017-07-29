#
# cogs/text/core.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has commands for text transformation '''
import codecs

import upsidedown

from discord.ext import commands

__all__ = [
    'Text',
]

class Text:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sep(self, ctx, posts_back: int = 1):
        ''' Adds a separator between posts, X posts back '''

        fut = ctx.message.delete()
        count = 0
        async for msg in ctx.channel.history():
            if msg.author == self.bot.client:
                count += 1
                if count >= posts_back + 1:
                    break

        assert msg.author == self.bot.client
        if not msg.content.startswith('.\n'):
            content = '.\n' + msg.content
            await msg.edit(content=content)
        await fut

    @commands.command()
    async def upsidedown(self, ctx, *, text: str):
        ''' Prints the given text upside down '''

        result = upsidedown.transform(text)
        await ctx.message.edit(content=result)

    @commands.command()
    async def rot13(self, ctx, *, text: str):
        ''' Rot13's the given text '''

        result = codecs.encode(text, 'rot_13')
        await ctx.message.edit(content=result)

    @commands.command()
    async def rev(self, ctx, *, text: str):
        ''' Reverses the text given '''

        await ctx.message.edit(content=text[::-1])
