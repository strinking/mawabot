#
# cogs/math.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Contains math-rel'''
import re

import discord
from discord.ext import commands


__all__ = [
    'setup',
]
class Math:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = General(bot)
    bot.add_cog(cog)
