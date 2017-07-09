#
# cogs/info.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has several commands that get guild information '''
import asyncio
import os
import re
import unicodedata

import aiohttp
import discord
import psutil
from discord.ext import commands

from mawabot import __version__ as version

__all__ = [
    'setup',
]

EMOJI_REGEX = re.compile(r'<:([A-Za-z~\-0-9]+):([0-9]+)>')

REPO = 'strinking/mawabot'
GIT_CONTRIBUTORS = f'https://api.github.com/repos/{REPO}/stats/contributors'
GITHUB_URL = f'https://github.com/{REPO}'

MiB = 1024 * 1024

class Info:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    # Helper methods
    def _get_users(self, names):
        if not names:
            return [self.bot.user]

        users = []
        for name in names:
            if name == 'me':
                users.append(self.bot.user)
                continue

            try:
                id = int(name)
                user = self.bot.get_user(id)
                if user:
                    users.append(user)
            except ValueError:
                for user in self.bot.users:
                    if user.name == name:
                        users.append(user)
                        break
        return users

    def _get_members(self, guild, names):
        if not names:
            return [guild.me]

        members = []
        for name in names:
            if name == 'me':
                members.append(guild.me)
                continue

            try:
                id = int(name)
                member = guild.get_member(id)
                if member:
                    members.append(member)
            except ValueError:
                member = guild.get_member_named(name)
                if member:
                    members.append(member)
        return members

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

    # Commands
    @commands.command()
    async def uinfo(self, ctx, *names: str):
        ''' Gets information about the given user(s) '''

        if ctx.guild is None:
            users = self._get_users(names)
        else:
            users = self._get_members(ctx.guild, names)

        for user in users:
            profile = None
            if not user.bot and not isinstance(user, discord.ClientUser):
                # Get user profile info
                profile = await user.profile()

            lines = [user.mention]

            if profile is not None:
                if profile.premium:
                    since = profile.premium_since.strftime('%x @ %X')
                    lines.append(f'Nitro user since `{since}`')

            if isinstance(user, discord.Member):
                if user.game:
                    if user.game.type == 1:
                        lines.append(f'Streaming [{user.game.name}]({user.game.url})')
                    else:
                        lines.append(f'Playing `{user.game.name}`')

                if user.voice:
                    mute = user.voice.mute or user.voice.self_mute
                    deaf = user.voice.deaf or user.voice.self_deaf

                    states = []
                    if mute:
                        states.append('muted')
                    if deaf:
                        states.append('deafened')

                    if states:
                        state = ', '.join(states)
                    else:
                        state = 'active'

                    lines.append(f'Voice: {state}')

                if user.nick:
                    lines.append(f'Nickname: {user.nick}')

                roles = ' '.join(map(lambda x: x.mention, user.roles[1:]))
                if roles:
                    lines.append(f'Roles: {roles}')

            embed = discord.Embed(type='rich', description='\n'.join(lines))
            embed.timestamp = user.created_at
            if hasattr(user, 'color'):
                embed.color = user.color

            name = f'{user.name}#{user.discriminator}'
            embed.set_author(name=name)
            embed.set_thumbnail(url=user.avatar_url)
            if isinstance(user, discord.Member):
                embed.add_field(name='Status:', value=f'`{user.status}`')
            embed.add_field(name='ID:', value=f'`{user.id}`')

            # Get connected accounts
            if profile is not None:
                if profile.connected_accounts:
                    accounts = []

                    for account in profile.connected_accounts:
                        if account['type'] == 'steam':
                            url = f'https://steamcommunity.com/profiles/{account["id"]}'
                            accounts.append(f'[{account["name"]}]({url})')
                        elif account['type'] == 'twitch':
                            url = f'https://www.twitch.tv/{account["name"]}'
                            accounts.append(f'[{account["name"]}]({url})')

                    if accounts:
                        embed.add_field(name='Connected Accounts:', value=', '.join(accounts))

            await ctx.send(embed=embed)

    @commands.command()
    async def id(self, ctx, *ids: int):
        ''' Gets information about the given snowflakes '''

        for id in ids:
            embed = discord.Embed(type='rich')
            embed.set_author(name=f'Snowflake {id}')
            embed.timestamp = discord.utils.snowflake_time(id)

            guild = self.bot.get_guild(id)
            if guild:
                embed.add_field(name='Guild:', value=guild.name)
                embed.set_thumbnail(url=guild.icon_url)

            channel = self.bot.get_channel(id)
            if channel:
                text = channel.mention
                if channel.guild != guild:
                    text += f' from "{channel.guild.name}"'
                embed.add_field(name='Channel:', value=text)

            user = self.bot.get_user(id)
            if user:
                embed.add_field(name='User:', value=user.mention)

            emoji = self.bot.get_emoji(id)
            if emoji:
                text = f'{emoji} ({emoji.name}) from "{channel.guild.name}"'
                embed.add_field(name='Emoji:', value=text)

            # Can't do get_message() since we're not a true bot

            await ctx.send(embed=embed)

    @commands.command()
    async def emoji(self, ctx, *emojis: str):
        ''' Gets information about the given emoji(s) '''

        for emoji in emojis:
            match = EMOJI_REGEX.match(emoji)
            lines = [emoji]
            if match:
                lines.append(f'Emoji: `{match[1]}`')
                lines.append(f'ID: `{match[2]}`')
            else:
                try:
                    name = unicodedata.name(emoji)
                    lines.append(f'Unicode name: `{name}`')
                    try:
                        lines.append(f'Ord: `{ord(name)}`')
                    except:
                        pass
                except TypeError:
                    lines.append('Not an emoji')

            await ctx.send(content='\n'.join(lines))

    @commands.command()
    async def uptime(self, ctx):
        ''' Gets the uptime of this self-bot '''

        uptime = str(self.bot.uptime).split('.')[0]
        await ctx.message.edit(content=f'`{uptime}`')

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

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Info(bot)
    bot.add_cog(cog)
