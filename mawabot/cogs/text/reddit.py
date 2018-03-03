#
# cogs/text/reddit.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

''' Has commands that integrate with Reddit '''
import logging

import aiohttp
import discord
from discord.ext import commands

__all__ = [
    'Reddit',
]

logger = logging.getLogger(__name__)

def check_reddit(func):
    async def wrapper(self, ctx):
        if self.bot.config['reddit'] is None:
            content = 'This command requires Reddit integration, but no token was given'
            logger.warning(content)
            await self.bot.send(content)
            return

        await func(self, ctx)
    wrapper.__name__ = func.__name__
    return wrapper

class Reddit:
    __slots__ = (
        'bot',
        'token',
        'session',
    )

    def __init__(self, bot):
        self.bot = bot
        self.token = None
        self.session = aiohttp.ClientSession()

    def __unload(self):
        self.session.close()

    def _headers(self):
        assert self.token
        return {'Authorization': f'bearer {self.token}',
                'User-Agent': 'mawabot/1 by aismallard & maware'}

    def _proxy(self):
        reddit = self.bot.config['reddit']

        proxy = reddit['proxy']
        if proxy is None:
            logging.debug("Not using a proxy")
            return {}

        logging.debug(f"Using proxy: {proxy}")
        proxy_auth = reddit['proxy-auth']
        if proxy_auth is not None:
            logging.debug("Proxy basic authentication specified")
            proxy_auth = aiohttp.BasicAuth(proxy_auth['user'], proxy_auth['password'])

        return {
            'proxy': proxy,
            'proxy_auth': proxy_auth,
        }

    async def request(self, path):
        url = 'https://oauth.reddit.com' + path
        logger.debug(f'Fetching reddit resource: {url}')

        if self.token is None:
            await self.refresh_token()

        async with self.session.get(url, headers=self._headers(), **self._proxy()) as req:
            if req.status == 401:
                logger.debug('Reddit token out of date, refreshing...')
                await self.refresh_token()

                # Try again with new token
                async with self.session.get(url, headers=self._headers()) as req:
                    req.raise_for_status()
                    data = await req.json()
            else:
                req.raise_for_status()
                data = await req.json()

        return data

    async def refresh_token(self,):
        logger.info('Getting new Reddit token')
        reddit = self.bot.config['reddit']
        async with self.session.post('https://www.reddit.com/api/v1/access_token',
                                    auth=aiohttp.BasicAuth(reddit['app-id'], reddit['app-secret']),
                                    data={'grant_type': 'client_credentials'},
                                    **self._proxy()) as req:
            req.raise_for_status()
            data = await req.json()
            self.token = data['access_token']

    @staticmethod
    def get_image(item, channel):
        # Check if nsfw images is given and channel is a nsfw channel
        nsfw = item['over_18']

        resolutions = item['preview']['images'][0]['resolutions']
        image = resolutions[1]
        image['url'] = image['url'].replace('&amp;', '&')

        embed = discord.Embed()
        embed.title = item['title']
        embed.url = 'https://www.reddit.com/' + item['permalink']
        embed.set_image(url=image['url'])
        embed.image.width = image['width']
        embed.image.height = image['height']

        if nsfw:
            safe = isinstance(channel, discord.abc.PrivateChannel) or channel.is_nsfw()
        else:
            safe = True

        return embed, safe

    async def try_sfw_image(self, path, channel, attempts=5):
        assert attempts > 0
        for _ in range(attempts):
            items = await self.request(path)
            item = items[0]['data']['children'][0]['data']

            embed, sfw_ok = self.get_image(item, channel)
            if sfw_ok:
                return embed

        return None

    async def safe_or_react(self, ctx, path, attempts=5):
        embed = await self.try_sfw_image(path, ctx.channel, attempts)
        if embed is not None:
            await ctx.send(embed=embed)
        else:
            await ctx.message.add_reaction('\N{NO ONE UNDER EIGHTEEN SYMBOL}')

    @commands.command()
    @check_reddit
    async def headpat(self, ctx):
        await self.safe_or_react(ctx, '/r/headpats/random')

    @commands.command()
    @check_reddit
    async def megane(self, ctx):
        await self.safe_or_react(ctx, '/r/megane/random')

    @commands.command()
    @check_reddit
    async def hentai(self, ctx):
        await self.safe_or_react(ctx, '/r/hentai/random', attempts=1)
