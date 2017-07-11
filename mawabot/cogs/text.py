#
# cogs/text.py
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
from random import randint

import discord
from discord.ext import commands
import upsidedown

__all__ = [
    'setup',
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
            if msg.author != self.bot.client:
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
    async def sw(self, ctx, *, text: str):
        ''' Spaces out words for meme emphasis '''

        words = text.split(' ')
        result = []
        for word in words:
            result.append(' '.join(word))

        await ctx.message.edit(content=' . '.join(result))

    @commands.command()
    async def cw(self, ctx, *, text: str):
        ''' "Crossword"-ifys the given text for meme emphasis '''

        text = text.upper()
        lines = [text] + list(text[1:])

        await ctx.message.edit(content='\n'.join(lines))

    @commands.command()
    async def rev(self, ctx, *, text: str):
        ''' Reverses the text given '''

        await ctx.message.edit(content=text[::-1])

    @commands.command()
    async def kerrhau(self, ctx, *text: str):
        ''' "kerrhau"-ifys the given text for meme emphasis '''

        text = list(text)
        words = []

        while text:
            rand_num = randint(1, 3)
            word = []

            try:
                for _ in range(rand_num):
                    word.append(text.pop(0))
            except:
                pass

            words.append(' '.join(word))

        last = words[-1][-1]
        words[-1] = words[-1][:-1]
        words.append(last)

        await ctx.message.edit(content='\n'.join(words))


def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Text(bot)
    bot.add_cog(cog)
