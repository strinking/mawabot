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
import re
import unicodedata

import discord
from discord.ext import commands

__all__ = [
    'setup',
]

EMOJI_REGEX = re.compile(r'<:([A-Za-z~\-0-9]+):([0-9]+)>')

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
                for member in guild.members:
                    if member.name == name or member.nick == name:
                        members.append(member)
                        break
        return members

    # Commands
    @commands.command()
    async def uinfo(self, ctx, *names: str):
        ''' Gets information about the given user(s) '''

        if ctx.guild is None:
            users = self._get_users(names)
        else:
            users = self._get_members(ctx.guild, names)

        for user in users:
            lines = [user.mention]

            if isinstance(user, discord.Member):
                if user.game:
                    if user.game.type == 1:
                        lines.append(f'Streaming `{user.game.url}`')
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
            embed.add_field(name='Status:', value=user.status)
            embed.add_field(name='ID:', value=f'`{user.id}`')
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

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Info(bot)
    bot.add_cog(cog)
