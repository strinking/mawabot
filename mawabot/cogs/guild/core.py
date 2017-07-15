#
# cogs/guild.py
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

import discord
from discord.ext import commands

NUMERIC_REGEX = re.compile(r'[0-9]+')
ROLE_MENTION_REGEX = re.compile(r'<@&([0-9]+)>')

class Guild:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    # Helper methods
    @staticmethod
    async def _get_role(guild, name):
        id = None

        if name == 'everyone':
            return guild.default_role

        if NUMERIC_REGEX.match(name):
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

    # Commands
    @commands.command()
    @commands.guild_only()
    async def ginfo(self, ctx):
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
        embed.add_field(name='Default channel:', value=ctx.guild.default_channel.mention)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def rinfo(self, ctx, *, name: str = None):
        ''' Lists information about roles on the guild '''

        if name is None:
            fmt_role = lambda role: f'{role.mention} ({len(role.members)})'
            desc = ', '.join(map(fmt_role, ctx.guild.role_hierarchy))
            embed = discord.Embed(type='rich', description=desc)
            await ctx.send(embed=embed)
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
                    f'Color (RGB): `{rgb[0]}, {rgb[1]}, {rgb[2]}`',
                ))

                embed = discord.Embed(type='rich', description=desc, color=role.color)
                embed.set_author(name=role.name)
                embed.add_field(name='ID:', value=role.id)
                embed.timestamp = role.created_at

            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def perms(self, ctx, *names: str):
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
            await ctx.send(embed=embed)
