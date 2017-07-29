#
# cogs/info/stats.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has commands related to the status of the bot '''
import asyncio
import os

import aiohttp
import psutil

import discord
from discord.ext import commands

from mawabot import __version__ as version

REPO = 'strinking/mawabot'
GITHUB_URL = f'https://github.com/{REPO}'
GIT_CONTRIBUTORS = f'https://api.github.com/repos/{REPO}/stats/contributors'

MiB = 1024 * 1024

__all__ = [
    'Stats',
]

class Stats:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    async def get_git_contributors(self):
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(GIT_CONTRIBUTORS) as resp:
                    status = resp.status
                    data = await resp.json()

            if status == 200:
                return data
            elif status == 202:
                await asyncio.sleep(2)
            else:
                return []

    @commands.command()
    async def stats(self, ctx):
        ''' Gets bot stats '''

        uptime = str(self.bot.uptime).split('.')[0]
        channels = sum(1 for _ in self.bot.get_all_channels())
        desc = [f'Uptime: `{uptime}`',
                f'Guilds: `{len(self.bot.guilds)}`',
                f'Channels: `{channels}`',
                f'Users: `{len(self.bot.users)}`',]

        embed = discord.Embed(title='mawabot', url=GITHUB_URL, description='\n'.join(desc))
        git = []
        contributors = await self.get_git_contributors()

        if contributors:
            contributors = sorted(contributors, key=lambda x: x.get('total'), reverse=True)
            for user in contributors:
                author = user['author']
                git.append(f'[{author["login"]}]({author["html_url"]}) ({user["total"]})')

        embed.add_field(name='Repo Info', value=f'Version: `{version}`\n{", ".join(git)}')

        # Get system info
        pid = os.getpid()
        py = psutil.Process(pid)

        cpu = py.cpu_percent()
        mem = py.memory_info()[0] / MiB

        embed.add_field(name='System Info', value=f'CPU: `{cpu}%` Mem: `{mem:.2f} MiB`', inline=False)

        await ctx.send(embed=embed)
