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
from pprint import pformat

import discord
from discord.ext import commands

from mawabot.utils import normalize_caseless

__all__ = [
    'Information',
]

CHANNEL_REGEX = re.compile(r'<#([0-9]+)>')
MENTION_REGEX = re.compile(r'<@!?([0-9]+)>')
EMOJI_REGEX = re.compile(r'<:([A-Za-z~\-0-9]+):([0-9]+)>')

class Information:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    async def _get_profile(self, user_or_id):
        if isinstance(user_or_id, discord.User):
            try:
                profile = await user_or_id.profile()
            except discord.NotFound:
                profile = None

            return profile, user_or_id
        else:
            try:
                profile = await self.bot.get_user_profile(user_or_id)
                return profile, profile.user
            except discord.NotFound:
                user = discord.utils.get(self.bot.users, id=user_or_id)
                return None, user

    async def _get_profiles(self, names):
        if not names:
            names = ['me']

        uids = []
        for name in names:
            if name == 'me' or name == 'myself':
                uids.append(self.bot.user.id)
                continue

            match = MENTION_REGEX.match(name)
            if match is not None:
                uid = int(match[1])
            elif name.isdigit():
                uid = int(name)
            else:
                nname = normalize_caseless(name)
                uid = discord.utils.find(lambda u, n=nname: normalize_caseless(u.name) == n, self.bot.users)

            uids.append(uid)

        profiles = await asyncio.gather(*[self._get_profile(uid) for uid in uids])
        return list(filter(lambda t: t[1] is not None, profiles))

    @staticmethod
    def _connected_accounts(connected_accounts):
        accounts = []
        for account in connected_accounts:
            id = account['id']
            name = account['name']
            type = account['type']
            verified = '`\N{WHITE HEAVY CHECK MARK}`' if account['verified'] else ''

            if type == 'battlenet':
                accounts.append(f'battle.net: {name} {verified}')
            elif type == 'facebook':
                url = f'https://www.facebook.com/{id}'
                accounts.append(f'[Facebook]({url}) {verified}')
            elif type == 'leagueoflegends':
                if '_' in id:
                    region, id = id.split('_')
                    url = f'http://lolking.net/summoner/{region}/{id}'
                    accounts.append(f'[League of Legends {verified}]({url})')
                else:
                    accounts.append(f'League of Legends: {name} {verified}')
            elif type == 'reddit':
                url = f'https://www.reddit.com/user/{name}'
                accounts.append(f'[Reddit {verified}]({url})')
            elif type == 'skype':
                accounts.append(f'Skype: {name} {verified}')
            elif type == 'spotify':
                url = f'https://open.spotify.com/user/{id}'
                accounts.append(f'[Spotify {verified}]({url})')
            elif type == 'steam':
                url = f'https://steamcommunity.com/profiles/{id}'
                accounts.append(f'[Steam {verified}]({url})')
            elif type == 'twitch':
                url = f'https://www.twitch.tv/{name}'
                accounts.append(f'[Twitch {verified}]({url})')
            elif type == 'twitter':
                url = f'https://twitter.com/{name}'
                accounts.append(f'[Twitter {verified}]({url})')
            elif type == 'youtube':
                url = f'https://www.youtube.com/channel/{id}'
                accounts.append(f'[YouTube {verified}]({url})')
            else:
                accounts.append(f'{type}: {name} `{id}` {verified}')

        return '\n'.join(accounts)

    @commands.command(aliases=['uinfo'])
    async def user_info(self, ctx, *names: str):
        ''' Gets information about the given user(s) '''

        profiles = await self._get_profiles(names)
        if not profiles:
            embed = discord.Embed(type='rich', description='No user profiles found.')
            await ctx.send(embed=embed)
            return

        for profile, user in profiles:
            lines = [user.mention]

            if profile is not None:
                # Nitro
                if profile.premium:
                    since = profile.premium_since.strftime('%x @ %X')
                    lines.append(f'- Nitro user since `{since}`')

                # Other markers
                if profile.staff:
                    lines.append('- Discord Staff')
                if profile.partner:
                    lines.append('- Discord Partner')
                if profile.hypesquad:
                    lines.append('- Hypesquad')

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

                roles = ' '.join(map(lambda r: r.mention, user.roles[1:]))
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

            if profile is not None:
                # Mutual guilds
                if profile.mutual_guilds:
                    guild_names = ', '.join(map(lambda g: g.name, profile.mutual_guilds))
                    embed.add_field(name=f'Mutual Guilds: ({len(profile.mutual_guilds)})', value=guild_names)

                # Get connected accounts
                if profile.connected_accounts:
                    accounts = self._connected_accounts(profile.connected_accounts)
                    if accounts:
                        embed.add_field(name='Connected Accounts:', value=accounts)

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

    @commands.command(aliases=['cinfo', 'vcinfo'])
    async def channel_info(self, ctx, *names: str):
        ''' Gets information about a given channel '''

        if names:
            embeds = (self._cinfo(ctx, name) for name in names)
        else:
            embeds = (self._cinfo(ctx, None),)

        await asyncio.gather(*[ctx.send(embed=embed) for embed in embeds])

    @commands.command(aliases=['id'])
    async def snowflake(self, ctx, *ids: int):
        ''' Gets information about the given snowflake(s) '''

        tasks = []
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

            tasks.append(ctx.send(embed=embed))

        await asyncio.gather(*tasks)

    @commands.command()
    async def pins(self, ctx, name: str = None):
        ''' Gets all the pins in the given channel '''

        channel = self._get_channel(ctx, name)
        if channel is not None:
            pins = await channel.pins()

            count = str(len(pins)) if pins else 'No'
            plural = '' if len(pins) == 1 else 's'
            embed = discord.Embed(type='rich', description=f'{count} pin{plural} in {channel.mention}')
            await asyncio.gather(
                ctx.message.delete(),
                self.bot._send(embed=embed),
            )

            for i, message in enumerate(pins):
                embed = discord.Embed(type='rich', description=message.content)
                embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
                embed.set_footer(text=f'Pin #{i+1}')
                embed.timestamp = message.edited_at or message.created_at
                await self.bot._send(embed=embed)

    @commands.command(aliases=['audit', 'alog'])
    async def audit_logs(self, ctx, limit: int = 20):
        ''' Retrieve the last 20 (or specified) entries in the audit log '''

        await ctx.message.delete()
        async for entry in ctx.guild.audit_logs(limit=limit):
            embed = discord.Embed(type='rich')
            embed.timestamp = entry.created_at
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar_url)
            embed.add_field(name='Type:', value=f'`{entry.action.name}`')
            embed.add_field(name='Target:', value=f'`{entry.target!r}`')
            embed.description = '\n'.join((
                '**Before:**',
                '```json',
                pformat(dict(entry.before)),
                '```\n',
                '**After:**',
                '```json',
                pformat(dict(entry.after)),
                '```',
            ))

            if entry.reason is not None:
                embed.add_field(name='Reason:', value=entry.reason)
            if entry.category is not None:
                embed.add_field(name='Category:', value=f'`{entry.category.name}`')
            if entry.extra is not None:
                embed.add_field(name='Extra:', value=f'`{entry.extra!r}`')

            await self.bot._send(embed=embed)

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
