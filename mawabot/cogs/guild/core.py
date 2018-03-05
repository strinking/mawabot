#
# cogs/guild/core.py
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
import logging
import re

import discord
from discord.ext import commands

from mawabot.utils import normalize_caseless

ROLE_MENTION_REGEX = re.compile(r'<@&([0-9]+)>')

logger = logging.getLogger(__name__)

class Guild:
    __slots__ = (
        'bot',
        'autonick_guilds',
        'autonick_task',
    )

    def __init__(self, bot):
        self.bot = bot
        self.autonick_guilds = {}
        self.autonick_task = bot.loop.create_task(self._autonick())

    def __unload(self):
        self.autonick_task.cancel()

    @staticmethod
    async def _get_role(guild, name):
        id = None

        if name == 'everyone':
            return guild.default_role

        if name.isdigit():
            id = int(name)
        else:
            match = ROLE_MENTION_REGEX.match(name)
            if match:
                id = int(match[1])

        if id is None:
            name = name.lower()
            for role in guild.roles:
                if role.name.lower() == name:
                    return role
        else:
            for role in guild.roles:
                if role.id == id:
                    return role
        return None

    def _get_guild(self, ctx, name):
        if name is None:
            return ctx.guild

        if name.isdigit():
            return self.bot.get_guild(int(name))
        else:
            name = normalize_caseless(name)
            for guild in self.bot.guilds:
                if normalize_caseless(guild.name) == name:
                    return guild
        return None

    async def _autonick(self):
        delay = 5
        while True:
            logger.debug('Checking autonick status...')
            tasks = [asyncio.sleep(delay)]

            for guild, nickname in self.autonick_guilds.items():
                display_name = nickname or self.bot.user.name
                if guild.me.display_name != display_name:
                    logger.info(f'Changing nickname for {guild.name} to "{display_name}"')
                    tasks.append(guild.me.edit(nick=nickname))
                    delay = 1

            if len(tasks) == 1:
                logger.debug(f'No autonicks needed, increasing delay to {delay}')
                delay = min(delay * 2, 240)

            await asyncio.gather(*tasks)

    @commands.command()
    @commands.guild_only()
    async def autonick(self, ctx, enable: bool, nickname: str = None, hide=False):
        ''' Enable/disable task to automatically reset your username periodically '''

        if enable:
            self.autonick_guilds[ctx.guild] = nickname
        else:
            self.autonick_guilds.pop(ctx.guild)

        if hide:
            await ctx.mesage.delete()
        else:
            enabled = 'Enabled' if enable else 'Disabled'
            embed = discord.Embed(type='rich', description=f'**{enabled}** autonick for {ctx.guild.name}')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def ack(self, ctx, *names: str):
        ''' Marks all messages in the current guild as read. '''

        await ctx.guild.ack()

    @commands.command()
    async def ackall(self, ctx):
        ''' Marks all message in all guilds as read. '''

        for guild in self.bot.guilds:
            await guild.ack()

    @commands.command()
    @commands.guild_only()
    async def ginfo(self, ctx, use_current=True):
        ''' Prints information about the current guild '''

        text_count = len(ctx.guild.text_channels)
        voice_count = len(ctx.guild.voice_channels)
        role_count = len(ctx.guild.roles)
        emoji_count = len(ctx.guild.emojis)
        created = ctx.guild.created_at.strftime('%x @ %X')
        members_online = sum(1 for member in ctx.guild.members if member.status != discord.Status.offline)
        members_total = ctx.guild.member_count
        members_percent = members_online / members_total * 100

        text = '\n'.join((
            f'Created: `{created}`',
            f'Text Channels: `{text_count}`',
            f'Voice Channels: `{voice_count}`',
            f'Members: `{members_online} / {members_total} ({members_percent:.1f}% online)`',
            f'Roles: `{role_count}`',
            f'Emojis: `{emoji_count}`',
        ))
        embed = discord.Embed(type='rich', description=text)
        if ctx.guild.icon_url:
            embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(name=ctx.guild.name)

        embed.add_field(name='Owner:', value=ctx.guild.owner.mention)

        if use_current:
            await ctx.send(embed=embed)
        else:
            await asyncio.gather(
                ctx.message.delete(),
                self.bot._send(embed=embed),
            )

    @commands.command()
    @commands.guild_only()
    async def rinfo(self, ctx, *, name: str = None, use_current=True):
        ''' Lists information about roles on the guild '''

        if name is None:
            fmt_role = lambda role: f'{role.mention} ({len(role.members)})'
            desc = ', '.join(map(fmt_role, ctx.guild.role_hierarchy))
            embed = discord.Embed(type='rich', description=desc)
            embed.set_author(name=f'{len(ctx.guild.roles)} roles in {ctx.guild.name}')
        else:
            role = await self._get_role(ctx.guild, name)

            if role is None:
                desc = f'**No such role:** {name}'
                embed = discord.Embed(type='rich', description=desc, color=discord.Color.red())
            else:
                rgb = role.color.to_rgb()
                desc = '\n'.join((
                    role.mention,
                    f'Members: `{len(role.members)}`',
                    f'Hoisted: `{role.hoist}`',
                    f'Position: `{role.position}`',
                    f'Mentionable: `{role.mentionable}`',
                    f'Permissions: `{role.permissions.value}`',
                    f'Hex Color: `{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}`',
                ))

                embed = discord.Embed(type='rich', description=desc, color=role.color)
                embed.set_author(name=role.name)
                embed.add_field(name='ID:', value=role.id)
                embed.timestamp = role.created_at

        if use_current:
            await ctx.send(embed=embed)
        else:
            await asyncio.gather(
                ctx.message.delete(),
                self.bot._send(embed=embed),
            )

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx, name: str = None, use_current=True):
        ''' Lists all roles in the current (or given) guild. '''

        guild = self._get_guild(ctx, name)

        if guild is None:
            desc = f'**No such guild:** {name}'
            embed = discord.Embed(type='rich', description=desc, color=discord.Color.red())
        else:
            def fmt_role(role):
                default = 'Default ' if role.is_default() else ''
                mentionable = 'Mentionable ' if role.mentionable else ''
                mentions_everyone = 'Mention @everyone ' if role.permissions.mention_everyone else ''
                admin = 'Admin ' if role.permissions.administrator else ''
                mention = role.mention if ctx.guild == role.guild else f'@{role.name}'
                count = f'({len(role.members)})'
                return f'`{role.id}` {mention} {count} {default}{mentionable}{mentions_everyone}{admin}'

            desc = '\n'.join(map(fmt_role, guild.roles))
            embed = discord.Embed(type='rich', description=desc)
            embed.set_author(name=guild.name)

        if use_current:
            await ctx.send(embed=embed)
        else:
            await asyncio.gather(
                ctx.message.delete(),
                self.bot._send(embed=embed),
            )

    @commands.command()
    @commands.guild_only()
    async def channels(self, ctx, name: str = None, use_current=True):
        ''' Lists all channels in the current (or given) guild. '''

        guild = self._get_guild(ctx, name)

        if guild is None:
            desc = f'**No such guild:** {name}'
            embed = discord.Embed(type='rich', description=desc, color=discord.Color.red())
        else:
            def fmt_chan(chan):
                topic = f' - {chan.topic}' if chan.topic else ''
                return f'`{chan.id}` {chan.mention} {topic}'

            is_txt_chan = lambda chan: isinstance(chan, discord.TextChannel)
            desc = '\n'.join(map(fmt_chan, filter(is_txt_chan, guild.channels)))
            embed = discord.Embed(type='rich', description=desc)
            embed.set_author(name=guild.name)

        if use_current:
            await ctx.send(embed=embed)
        else:
            await asyncio.gather(
                ctx.message.delete(),
                self.bot._send(embed=embed),
            )

    @commands.command()
    @commands.guild_only()
    async def perms(self, ctx, *names: str, use_current=True):
        for name in names:
            role = await self._get_role(ctx.guild, name)

            if role is None:
                desc = f'**No such role:** {name}'
                embed = discord.Embed(type='rich', description=desc, color=discord.Color.red())
            else:
                perms = role.permissions
                desc = '\n'.join((
                    role.mention,
                    '',
                    f'Administrator: `{perms.administrator}`',
                    f'Ban members: `{perms.ban_members}`',
                    f'Kick members: `{perms.kick_members}`',
                    f'Manage guild: `{perms.manage_guild}`',
                    f'Manage channels: `{perms.manage_channels}`',
                    f'Manage nicknames: `{perms.manage_nicknames}`',
                    f'Manage roles: `{perms.manage_roles}`',
                    f'Manage webhooks: `{perms.manage_webhooks}`',
                    f'Manage emojis: `{perms.manage_emojis}`',
                    f'View audit log: `{perms.view_audit_log}`',
                    f'Read messages: `{perms.read_messages}`',
                    f'Send messages: `{perms.send_messages}`',
                    f'Add reactions: `{perms.add_reactions}`',
                    f'Send TTS messages: `{perms.send_tts_messages}`',
                    f'Embed links: `{perms.embed_links}`',
                    f'Attach files: `{perms.attach_files}`',
                    f'Read message history: `{perms.read_message_history}`',
                    f'Mention \\@everyone: `{perms.mention_everyone}`',
                    f'External emojis: `{perms.external_emojis}`',
                    f'Create instant invite: `{perms.create_instant_invite}`',
                    f'Can connect to voice: `{perms.connect}`',
                    f'Can speak in voice: `{perms.speak}`',
                    f'Mute members: `{perms.mute_members}`',
                    f'Deafen members: `{perms.deafen_members}`',
                    f'Move members: `{perms.move_members}`',
                    f'Use voice activation: `{perms.use_voice_activation}`',
                    f'Change nickname: `{perms.change_nickname}`',
                ))
                embed = discord.Embed(type='rich', description=desc, color=role.color)

            if use_current:
                await ctx.send(embed=embed)
            else:
                await asyncio.gather(
                    ctx.message.delete(),
                    self.bot._send(embed=embed),
                )
