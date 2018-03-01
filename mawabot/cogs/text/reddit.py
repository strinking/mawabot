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
            await self.bot._send(content)
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

    async def request(self, path):
        url = 'https://oauth.reddit.com' + path
        logger.debug(f'Fetching reddit resource: {url}')

        if self.token is None:
            await self.refresh_token()

        async with self.session.get(url, headers=self._headers()) as req:
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
                                    data={'grant_type': 'client_credentials'}) as req:
            req.raise_for_status()
            data = await req.json()
            self.token = data['access_token']

    def get_image(self, item, channel):
        # Check if nsfw images is given and channel is a nsfw channel
        nsfw = item['over_18']

        if not nsfw:
            resolutions = item['preview']['images'][0]['resolutions']
            image = resolutions[1]
            image['url'] = image['url'].replace('&amp;', '&')
        else:
            if channel.is_nsfw():
                resolutions = item['preview']['images'][0]['resolutions']
                image = resolutions[1]
                image['url'] = image['url'].replace('&amp;', '&')
            else:
                return None
        
        embed = discord.Embed()
        embed.title = item['title']
        embed.url = 'https://www.reddit.com/' + item['permalink']
        embed.set_image(url=image['url'])
        embed.image.width = image['width']
        embed.image.height = image['height']

        return embed
    
    @commands.command()
    @check_reddit
    async def headpat(self, ctx):
        items = await self.request('/r/headpats/random')
        item = items[0]['data']['children'][0]['data']
        
        # If the image is nsfw and the channel isn't set as nsfw image is none
        image = self.get_image(item, ctx.channel)

        if image is not None:
            await ctx.send(embed=image)
        else:
            # Retry once more incase it was just that one

            items = await self.request('/r/headpats/random')
            item = items[0]['data']['children'][0]['data']
        
            image = self.get_image(item, ctx.channel)

            if image is not None:
                await ctx.send(embed=image)
            else:
                await ctx.message.add_reaction('🔞')
    
    @commands.command()
    @check_reddit
    async def megane(self, ctx):
        items = await self.request('/r/megane/random')
        item = items[0]['data']['children'][0]['data']
        
        # If the image is nsfw and the channel isn't set as nsfw image is none
        image = self.get_image(item, ctx.channel)

        if image is not None:
            await ctx.send(embed=image)
        else:
            # Retry once more incase it was just that one

            items = await self.request('/r/megane/random')
            item = items[0]['data']['children'][0]['data']
        
            image = self.get_image(item, ctx.channel)

            if image is not None:
                await ctx.send(embed=image)
            else:
                await ctx.message.add_reaction('🔞')
    
    @commands.command()
    @check_reddit
    async def hentai(self, ctx):
        items = await self.request('/r/hentai/random')
        item = items[0]['data']['children'][0]['data']
        
        # If the image is nsfw and the channel isn't set as nsfw image is none
        image = self.get_image(item, ctx.channel)

        if image is not None:
            await ctx.send(embed=image)
        else:
            # Retry once more incase it was just that one

            items = await self.request('/r/hentai/random')
            item = items[0]['data']['children'][0]['data']
        
            image = self.get_image(item, ctx.channel)

            if image is not None:
                await ctx.send(embed=image)
            else:
                await ctx.message.add_reaction('🔞')
