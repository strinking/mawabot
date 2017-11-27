#
# cogs/files.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has commands related to file uploads and downloads '''

import asyncio
import os
import re
import traceback
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

URL_REGEX = re.compile(r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)')
URL_FILENAME_REGEX = re.compile(r'^https?:\/\/.*\/([^\/ ]+)$')

class Files:
    __slots__ = (
        'bot',
        'dir',
    )

    def __init__(self, bot):
        self.bot = bot
        self.dir = self.bot.config['download-dir']
        os.makedirs(self.dir, exist_ok=True)

    @commands.command(name='upload', aliases=['up'])
    async def upload(self, ctx, *paths: str):
        ''' Uploads the given files from your filesystem to this channel '''

        if not paths:
            return

        fut = ctx.message.delete()
        files = [discord.File(path) for path in paths]
        if len(files) == 1:
            kwargs = {
                'file': files[0],
            }
        else:
            kwargs = {
                'files': files,
            }

        await ctx.send(**kwargs)
        await fut

    @staticmethod
    def _get_path(dir_path, url, discrim):
        match = URL_FILENAME_REGEX.match(url)
        if match is None:
            name = f'{discrim}'
        else:
            name = f'{discrim}-{match[1]}'

        return os.path.join(dir_path, name)

    async def _save(self, url, path):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as req:
                data = await req.read()

        with open(path, 'wb') as fh:
            fh.write(data)

    @commands.command(name='download', aliases=['dl'])
    async def download(self, ctx, posts: int = 1):
        ''' Downloads the last X urls from the current channel '''

        fut = ctx.message.delete()

        # For "embed.color"
        # pylint: disable=assigning-non-slot

        try:
            count, path = await self._download(ctx, posts)
        except:
            embed = discord.Embed(type='rich', title='Download failed!')
            embed.color = discord.Color.red()
            embed.description = f'```py\n{traceback.format_exc()}\n```'
            embed.timestamp = datetime.now()
        else:
            embed = discord.Embed(type='rich', title=f'Download complete!')
            embed.color = discord.Color.green()
            embed.description = f'\U0001f4c1 Saved **{count} files** to `{path}`'
            embed.timestamp = datetime.now()

        await self.bot._send(embed=embed)
        await fut

    async def _download(self, ctx, posts):
        urls = []
        futures = []

        # Create exclusive dir
        dir_path = os.path.join(self.dir, f'mawabot-dl-{ctx.message.id}')
        os.mkdir(dir_path)

        # Gather all items to download
        before = discord.utils.snowflake_time(ctx.message.id)
        i = 0
        async for msg in ctx.channel.history(limit=posts + 1, before=before):
            if msg == ctx.message:
                continue

            # Links
            for url in URL_REGEX.findall(msg.content):
                urls.append(url)
                path = self._get_path(dir_path, url, i)
                i += 1

                futures.append(self._save(url, path))

            # Attachments
            for attach in msg.attachments:
                path = os.path.join(dir_path, f'{i}-{attach.filename}')
                i += 1

                futures.append(attach.save(path))

        # Save list of URLs
        path = os.path.join(dir_path, 'urls.txt')
        with open(path, 'w') as fh:
            fh.write('\n'.join(urls))

        # Queue the downloads
        await asyncio.gather(*futures)
        return i, dir_path
