#
# cogs/info/info.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Contains in-depth commands that get information '''
import asyncio
import re
import unicodedata

import discord
from discord.ext import commands

__all__ = [
    'Info',
]

CHANNEL_REGEX = re.compile(r'<#([0-9]+)>')
EMOJI_REGEX = re.compile(r'<:([A-Za-z~\-0-9]+):([0-9]+)>')

class Info:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

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

            # For embed.color
            # pylint: disable=assigning-non-slot

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

    def _get_channel(self, ctx, name):
        if name is None:
            return ctx.channel
        else:
            match = CHANNEL_REGEX.match(name)
            if match:
                cid = int(match[1])
            elif name.isdigit():
                cid = int(name)
            elif ctx.guild is not None:
                return discord.utils.get(ctx.guild.channels, name=name)
        return self.bot.get_channel(cid)

    def _cinfo(self, ctx, name):
        channel = self._get_channel(ctx, name)

        # Couldn't find it
        if channel is None:
            embed = discord.Embed(description=f'No channel found that matched {name}', color=discord.Color.red())
            embed.set_author(name='Error')
            return embed
        else:
            embed = discord.Embed()
            embed.timestamp = channel.created_at
            desc = [f'ID: `{channel.id}`']

            # Check if it is a guild channel
            if isinstance(channel, discord.abc.GuildChannel):
                embed.set_author(name=channel.name)
                desc.append(f'Guild: `{channel.guild.name}`')

                if isinstance(channel, discord.TextChannel):
                    desc.append('Type: `Text`')
                    desc.append(f'Mention: {channel.mention}')
                    desc.append(f'NSFW: `{channel.is_nsfw()}`')
                    desc.append(f'Members: `{len(channel.members)}`')

                    if channel.topic is not None:
                        embed.add_field(name='Topic:', value=channel.topic)
                else:
                    desc.append('Type: `Voice`')
                    desc.append(f'Bitrate: `{channel.bitrate}`')
                    connected = len(channel.members)
                    limit = channel.user_limit

                    if limit == 0:
                        connstr = f'{connected}'
                    else:
                        connstr = f'{connected}/{limit}'
                    desc.append(f'Connected: `{connstr}`')

            else:
                # Must be a DM otherwise
                if isinstance(channel, discord.DMChannel):
                    desc.append('Type: `DM`')
                    embed.set_author(name=channel.recipient.name)
                else:
                    desc.append('Type: `DM Group`')
                    embed.set_author(name=channel.name)
                    desc.append(f'Owner: `{channel.owner.name}`')

            embed.description = '\n'.join(desc)
            return embed

    @commands.command()
    async def cinfo(self, ctx, *names: str):
        ''' Gets information about a given channel '''

        if names:
            embeds = (self._cinfo(ctx, name) for name in names)
        else:
            embeds = (self._cinfo(ctx, None),)

        await asyncio.gather(*[ctx.send(embed=embed) for embed in embeds])

    @commands.command(aliases=['snowflake'])
    async def id(self, ctx, *ids: int):
        ''' Gets information about the given snowflake(s) '''

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
    async def pins(self, ctx, name):
        pass
        # TODO

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
