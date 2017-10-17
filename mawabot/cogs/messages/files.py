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
import io
import tarfile
import re
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

URL_REGEX = re.compile(r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)')
URL_FILENAME_REGEX = re.compile(r'^.*\/([^\/ ]+)$')

class Files:
    __slots__ = (
        'bot',
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def upload(self, ctx, *paths: str):
        ''' Uploads the given files from your filesystem to this channel '''

        if not paths:
            return

        fut = ctx.message.delete()
        files = []
        for path in files:
            with open(path, 'rb') as fh:
                data = fh.read()
            files.append(io.BytesIO(data))

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

    async def _dl(self, url, fileobj):
        async with aiohttp.request('GET', url) as req:
            fileobj.write(await req.read())

    @commands.command()
    async def dl(self, ctx, posts: int = 1):
        ''' Downloads the last X urls from the current channel '''

        urls = []
        files = []
        futures = []

        # Gather all items to download
        before = discord.utils.snowflake_time(ctx.message.id)
        async for msg in ctx.channel.history(limit=posts + 1, before=before):
            if msg == ctx.message:
                continue

            # Links
            for url in URL_REGEX.findall(msg.content):
                urls.append(url)
                fileobj = io.BytesIO()
                files.append(fileobj)
                futures.append(self._dl(url, fileobj))

            # Attachments
            for attach in msg.attachments:
                urls.append(attach.url)
                fileobj = io.BytesIO()
                files.append(fileobj)
                futures.append(attach.save(fileobj))

        # Queue the downloads
        await asyncio.gather(*futures)

        # Add files to tar archive
        tar_path = f'mawabot-dl-{ctx.message.id}.tar.gz'
        with open(tar_path, 'wb') as fh:
            with tarfile.open(fileobj=fh, mode='x:gz') as tar:
                # Add list of urls found
                fileobj = io.BytesIO('\n'.join(urls).encode('utf-8'))
                tarinfo = tar.gettarinfo(name='urls.txt', fileobj=fileobj)
                tar.addfile(tarinfo, fileobj)

                # Add downloaded files
                for i, fileobj in enumerate(files):
                    match = URL_FILENAME_REGEX.match(urls[i])
                    if match is None:
                        name = f'{i}'
                    else:
                        name = f'{i}-{match[1]}'

                    tarinfo = tar.gettarinfo(name=name, fileobj=fileobj)
                    tar.addfile(tarinfo, fileobj)

        # Announce that it's done
        embed = discord.Embed(type='rich', title=f'Download for {ctx.message.id} complete!')
        embed.timestamp = datetime.now()
        embed.set_footer(name=f'{len(urls)} files downloaded')
        await self.bot._send(embed=embed)
