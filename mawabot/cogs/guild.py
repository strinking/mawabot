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
    async def _guild_check(ctx):
        if ctx.guild is None:
            embed = discord.Embed(type='rich', description='This is not a guild.')
            await ctx.send(embed=embed)
            return False
        return True

    @staticmethod
    def _get_role(guild, name):
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
            for role in guild.roles:
                if role.name == name:
                    return role
        else:
            for role in guild.roles:
                if role.id == id:
                    return role
        return None

    # Commands
    @commands.command()
    async def ginfo(self, ctx):
        ''' Prints information about the current guild '''

        if not self._guild_check(ctx):
            return

        text_count = len(ctx.guild.text_channels)
        voice_count = len(ctx.guild.voice_channels)
        role_count = len(ctx.guild.roles)
        emoji_count = len(ctx.guild.emojis)
        created = ctx.guild.created_at.strftime('%x @ %X')

        text = '\n'.join((
            f'Created: `{created}`',
            f'Text Channels: `{text_count}`',
            f'Voice Channels: `{voice_count}`',
            f'Members: `{ctx.guild.member_count}`',
            f'Roles: `{role_count}`',
            f'Emojis: `{emoji_count}`',
        ))
        embed = discord.Embed(type='rich', description=text)
        if guild.icon_url:
            embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(name=ctx.guild.name)

        embed.add_field(name='Owner:', value=ctx.guild.owner.mention)
        embed.add_field(name='Default channel:', value=ctx.guild.default_channel.mention)

        await ctx.send(embed=embed)

    @commands.command()
    async def roles(self, ctx):
        ''' Lists all the roles and their IDs '''

        if not self._guild_check(ctx):
            return

        lines = []
        for role in ctx.guild.role_hierarchy:
            lines.append(f'{role.mention}: {role.id}')

            if len(lines) > 20:
                embed = discord.Embed(type='rich', description='\n'.join(lines))
                await ctx.send(embed=embed)
                lines = []

        if lines:
            embed = discord.Embed(type='rich', description='\n'.join(lines))
            await ctx.send(embed=embed)

    @commands.command()
    async def rinfo(self, ctx, name: str):
        ''' Prints more detailed information about a role '''

        role = self._get_role(ctx.guild, name)

        if role is None:
            desc = f'**No such role:** {name}'
            embed = discord.Embed(type='rich', description=desc, color=discord.Color.red())
        else:
            desc = '\n'.join((
                role.mention,
                f'ID: {role.id}',
                f'Created: {role.created_at}',
                f'Members: {len(role.members)}',
                f'Hoisted: {role.hoist}',
                f'Position: {role.position}',
                f'Mentionable: {role.mentionable}',
            ))
            embed = discord.Embed(type='rich', description=desc, color=role.color)
            embed.set_author(name=role.name)

        await ctx.send(embed=embed)

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Guild(bot)
    bot.add_cog(cog)
