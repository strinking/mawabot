#
# cogs/programming/core.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has commands for programming '''
import logging
import subprocess

import discord
from discord.ext import commands

__all__ = [
    'Programming',
]

logger = logging.getLogger(__file__)

class Programming:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    # For embed.color
    # pylint: disable=assigning-non-slot

    @commands.command()
    async def exec(self, ctx, *, command: str):
        ''' Evaluates an arbitrary Python command '''

        logger.info(f'Running python: "{command}"')
        embed = discord.Embed(type='rich')
        embed.set_author(name=command)
        try:
            # pylint: disable=exec-used
            exec(command)
            embed.color = discord.Color.green()
            embed.description = 'Success'
            await ctx.send(embed=embed)
        except Exception as ex:
            embed.color = discord.Color.red()
            embed.description = f'{ex.__class__.__name__}: {ex}'
            await ctx.send(embed=embed)

    @commands.command()
    async def eval(self, ctx, *, expr: str):
        ''' Evaluates an abritrary Python expression '''

        logger.info(f'Evaluating python: "{expr}"')
        embed = discord.Embed(type='rich')
        embed.set_author(name=expr)
        try:
            # pylint: disable=eval-used
            result = eval(expr)
            embed.color = discord.Color.teal()
            embed.description = f'`{result!r}`'
        except Exception as ex:
            embed.color = discord.Color.red()
            embed.description = f'{ex.__class__.__name__}: {ex}'

        await ctx.send(embed=embed)

    @staticmethod
    def _get_text(binary):
        try:
            if 0 in binary:
                raise ValueError

            type = 'Text'
            text = binary.decode('utf-8').replace("```", "'''")
        except (UnicodeDecodeError, ValueError):
            chars = []
            for i, byte in enumerate(binary):
                chars.append(f'{byte:02x}')
                if i % 2 == 1:
                    chars.append(' ')

            type = 'Binary'
            text = ''.join(chars)

        if len(text) > 950:
            text = text[:950] + '\n...output too long...'

        return '\n'.join((
            f'{type}:',
            '```',
            text,
            '```',
        ))

    @commands.command()
    async def sh(self, ctx, *, command: str):
        ''' Evaluates an arbitrary shell command '''

        fut = ctx.message.delete()
        result = subprocess.run(['/bin/bash', '-c', command], timeout=3,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        embed = discord.Embed(type='rich')
        embed.set_author(name=command)
        embed.color = discord.Color.dark_red() if result.returncode else discord.Color.green()

        if result.returncode or not (result.stdout or result.stderr):
            embed.description = f'**Return Code:** {result.returncode}'

        if result.stdout:
            embed.add_field(name='stdout', value=self._get_text(result.stdout))
        if result.stderr:
            embed.add_field(name='stderr', value=self._get_text(result.stderr))

        await ctx.send(embed=embed)
        await fut
