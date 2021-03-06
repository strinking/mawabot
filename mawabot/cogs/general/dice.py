#
# cogs/general/dice.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Holds commands related to dice and probability '''

import random
import re

from discord.ext import commands

DICE_REGEX = re.compile(r'(?:([0-9]+)?\s*d)?\s*([0-9]+)', re.IGNORECASE)

__all__ = [
    'Dice',
]

class Dice:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, *, roll: str = ''):
        ''' "XdY" rolls X dice with Y sides '''

        if roll:
            match = DICE_REGEX.match(roll)
            if match is None:
                return

            dice = int(match[1]) if match[1] else 1
            sides = int(match[2])
        else:
            dice = 1
            sides = 6

        if dice == 1:
            result = random.randint(1, sides)
            await ctx.send(content=f'🎲 {result}')
        else:
            rolls = []
            total = 0
            for _ in range(dice):
                result = random.randint(1, sides)
                rolls.append(f'{result}')
                total += result

            rolls = ' + '.join(rolls)
            await ctx.send(content=f'🎲 {rolls} = {total}')
