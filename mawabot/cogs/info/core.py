#
# cogs/info/core.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has several commands that get miscellaneous pieces of information '''
from datetime import datetime
import bisect
import time

import astral

import discord
from discord.ext import commands

__all__ = [
    'General',
]

class General:
    __slots__ = (
        'bot',
        'astral',
        'zodiac',
        'moon_phases',
    )

    def __init__(self, bot):
        self.bot = bot
        self.astral = astral.Astral()
        self.zodiac = (
            (120, '\N{CAPRICORN}'),
            (218, '\N{AQUARIUS}'),
            (320, '\N{PISCES}'),
            (420, '\N{ARIES}'),
            (521, '\N{TAURUS}'),
            (621, '\N{GEMINI}'),
            (722, '\N{CANCER}'),
            (823, '\N{LEO}'),
            (923, '\N{VIRGO}'),
            (1023, '\N{LIBRA}'),
            (1122, '\N{SCORPIUS}'),
            (1222, '\N{SAGITTARIUS}'),
            (1231, '\N{CAPRICORN}'),
        )
        self.moon_phases = (
            (0, '\N{NEW MOON SYMBOL}'),
            (4, '\N{WAXING CRESCENT MOON SYMBOL}'),
            (7, '\N{FIRST QUARTER MOON SYMBOL}'),
            (11, '\N{WAXING GIBBOUS MOON SYMBOL}'),
            (14, '\N{FULL MOON SYMBOL}'),
            (18, '\N{WANING GIBBOUS MOON SYMBOL}'),
            (21, '\N{LAST QUARTER MOON SYMBOL}'),
            (26, '\N{WANING CRESCENT MOON SYMBOL}'),
        )

    def get_zodiac(self, month, day):
        date = 100 * month + day
        index = bisect.bisect(self.zodiac, (date, ''))
        return self.zodiac[index][1]

    def get_moon_phase(self, date):
        phase = self.astral.moon_phase(date)
        index = bisect.bisect(self.moon_phases, (phase, ''))
        return self.moon_phases[index][1]

    @commands.command()
    async def today(self, ctx):
        ''' Gets some information about today '''

        now = datetime.now()
        moon_phase = self.get_moon_phase(now)
        zodiac_sign = self.get_zodiac(now.month, now.day)

        desc = (f'Moon Phase: {moon_phase}\n'
                f'Zodiac sign: {zodiac_sign}\n')

        embed = discord.Embed(type='rich', description=desc)
        embed.set_author(name=f'Today is {now:%A, %B %d, %Y}')
        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        ''' Gets the uptime of this self-bot '''

        uptime = str(self.bot.uptime).split('.')[0]
        await ctx.message.edit(content=f'`{uptime}`')

    @commands.command()
    async def unixtime(self, ctx):
        ''' Gets the current UNIX timestamp '''

        await ctx.message.edit(content=f'`{time.time()}`')
