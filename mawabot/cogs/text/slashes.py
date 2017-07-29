#
# cogs/text/slashes.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

import discord
from discord.ext import commands

__all__ = [
    'Slashes',
]

class Slashes:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tableflip(self, ctx, text: str = ''):
        ''' (╯°□°）╯︵ ┻━┻ '''

        content = text + r'(╯°□°）╯︵ ┻━┻'
        await ctx.message.edit(content=content)

    @commands.command()
    async def unflip(self, ctx, text: str = ''):
        ''' ┬──┬﻿ ノ( ゜-゜ノ) '''

        content = text + ' ┬─┬﻿ ノ( ゜-゜ノ)'
        await ctx.message.edit(content=content)

    @commands.command()
    async def justright(self, ctx, text: str = ''):
        ''' ✋😩👌 '''

        content = text + r' ✋😩👌'
        await ctx.message.edit(content=content)

    @commands.command()
    async def culol(self, ctx, text: str = ''):
        ''' 😂 👌 '''

        content = text + r' 😂 👌'
        await ctx.message.edit(content=content)

    @commands.command()
    async def shrug(self, ctx, text: str = ''):
        ''' ¯\\_(ツ)_/¯ '''

        content = text + r' ¯\_(ツ)_/¯'
        await ctx.message.edit(content=content)

    @commands.command()
    async def lenny(self, ctx, text: str = ''):
        ''' ( ͡° ͜ʖ ͡°) '''

        content = text + ' ( ͡° ͜ʖ ͡°)'
        await ctx.message.edit(content=content)

    @commands.command()
    async def wtf(self, ctx, text: str = ''):
        ''' ಠ_ಠ '''

        content = text + ' ಠ_ಠ'
        await ctx.message.edit(content=content)
