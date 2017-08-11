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

import random
import re
import subprocess

from discord.ext import commands

__all__ = [
    'Meme',
]

DISCORD_STRINGS = re.compile(r'(<\S*>)')

class Meme:
    __slots__ = (
        'bot',
        'regional_emojis',
    )

    def __init__(self, bot):
        self.bot = bot
        self.regional_emojis = {
            'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}',
            'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
            'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
            'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}',
            'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
            'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
            'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}',
            'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
            'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
            'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}',
            'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
            'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
            'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}',
            'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
            'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
            'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}',
            'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
            'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
            's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}',
            't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
            'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
            'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}',
            'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}',
            'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
            'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}',
            'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}',
            '0': '0\N{COMBINING ENCLOSING KEYCAP}',
            '1': '1\N{COMBINING ENCLOSING KEYCAP}',
            '2': '2\N{COMBINING ENCLOSING KEYCAP}',
            '3': '3\N{COMBINING ENCLOSING KEYCAP}',
            '4': '4\N{COMBINING ENCLOSING KEYCAP}',
            '5': '5\N{COMBINING ENCLOSING KEYCAP}',
            '6': '6\N{COMBINING ENCLOSING KEYCAP}',
            '7': '7\N{COMBINING ENCLOSING KEYCAP}',
            '8': '8\N{COMBINING ENCLOSING KEYCAP}',
            '9': '9\N{COMBINING ENCLOSING KEYCAP}',
            '!': '\N{HEAVY EXCLAMATION MARK SYMBOL}',
            '?': '\N{BLACK QUESTION MARK ORNAMENT}',
        }

    @commands.command()
    async def ri(self, ctx, *, text: str):
        ''' Makes the whole message into regional_indicator emojis '''

        def mapper(s):
            if s.startswith('<'):
                return s
            return '\u200b'.join(self.regional_emojis.get(c.lower(), c) for c in s)

        fut = ctx.message.delete()
        content = ''.join(map(mapper, DISCORD_STRINGS.split(text)))
        await ctx.send(content=content)
        await fut

    @commands.command()
    async def sw(self, ctx, *, text: str):
        ''' Spaces out words '''

        content = ' . '.join(' '.join(word) for word in text.split(' '))
        await ctx.message.edit(content=content)

    @commands.command()
    async def cw(self, ctx, *, text: str):
        ''' "Crossword"-ifys the given text '''

        text = text.upper()
        lines = [text] + list(text[1:])

        await ctx.message.edit(content='\n'.join(lines))

    @commands.command()
    async def kerrhau(self, ctx, *text: str):
        ''' "kerrhau"-ifys the given text '''

        text = list(text)
        words = []

        while text:
            word = []

            for _ in range(random.randint(1, 3)):
                if text:
                    word.append(text.pop(0))

            words.append(' '.join(word))

        last = words[-1][-1]
        words[-1] = words[-1][:-1]
        words.append(last)

        await ctx.message.edit(content='\n'.join(words))

    def _cowsay(self, args, text):
        text = text.replace('\n', '\n\n').replace("```", "'''")
        args.append(text)
        output = subprocess.check_output(args, stderr=subprocess.DEVNULL, timeout=0.5)
        content = '\n'.join((
            '```',
            output.decode('utf-8'),
            '```',
        ))
        return content

    @commands.command()
    async def cowsay(self, ctx, *, text: str):
        ''' Replaces the given text with cowsay '''
        content = self._cowsay(['cowsay'], text)
        await ctx.message.edit(content=content)

    @commands.command()
    async def cowthink(self, ctx, *, text: str):
        ''' Replaces the given text with cowthink '''
        content = self._cowsay(['cowthink'], text)
        await ctx.message.edit(content=content)

    @commands.command()
    async def cowcustom(self, ctx, cowfile: str, *, text: str):
        ''' Replaces the given text with the given cow file '''
        content = self._cowsay(['cowsay', '-f', cowfile], text)
        await ctx.message.edit(content=content)
