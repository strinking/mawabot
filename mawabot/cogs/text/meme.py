#
# cogs/text/meme.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has commands for meme-y text transformation '''

import discord
from discord.ext import commands

__all__ = [
    'Meme',
]

class Meme:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

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
    async def kerrhau(self, ctx, *text: str):
        ''' "kerrhau"-ifys the given text for meme emphasis '''

        text = list(text)
        words = []

        while text:
            word = []

            for _ in range(randint(1, 3)):
                if text:
                    word.append(text.pop(0))

            words.append(' '.join(word))

        last = words[-1][-1]
        words[-1] = words[-1][:-1]
        words.append(last)

        await ctx.message.edit(content='\n'.join(words))
