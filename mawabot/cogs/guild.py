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

__all__ = [
    'setup',
]

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
            desc = ' '.join(map(lambda x: x.mention, ctx.guild.role_hierarchy))
            embed = discord.Embed(type='rich', description=desc)
            await ctx.send(embed=embed)
        else:
            role = await self._get_role(ctx.guild, name)

            if role is None:
                desc = f'**No such role:** {name}'
                embed = discord.Embed(type='rich', description=desc, color=discord.Color.red())
            else:
                desc = '\n'.join((
                    role.mention,
                    f'Members: `{len(role.members)}`',
                    f'Hoisted: `{role.hoist}`',
                    f'Position: `{role.position}`',
                    f'Mentionable: `{role.mentionable}`',
                ))
                embed = discord.Embed(type='rich', description=desc, color=role.color)
                embed.set_author(name=role.name)
                embed.add_field(name='ID:', value=role.id)
                embed.timestamp = role.created_at

            await ctx.send(embed=embed)

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Guild(bot)
    bot.add_cog(cog)
