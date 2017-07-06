''' Holds general commands for self bot '''
from random import randint

import discord
from discord.ext import commands
import upsidedown


class General:
    ''' Holds commands that don't have a suitable place else where '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        ''' Pong '''

        await ctx.message.edit(content='Pong')

    @commands.command()
    async def roll(self, ctx, number: int = 10):
        ''' Gives a random number from 0 to the number given '''

        result = randint(0, number)
        await ctx.message.edit(content=f'Rolled: {result}')

    @commands.command()
    async def upsidedown(self, ctx, *, text: str):
        ''' Gives a random number from 0 to the number given '''

        result = upsidedown.transform(text)
        await ctx.message.edit(content=f'{result}')

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = General(bot)
    bot.add_cog(cog)
