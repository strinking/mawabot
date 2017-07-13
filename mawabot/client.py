#
# client.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

'''
client.py
Holds the custom discord client
'''

import datetime
import logging
import re
from os import listdir

import discord
from discord.ext import commands

from .utils import Reloader

logger = logging.getLogger(__name__)

PY_FILE_REGEX = re.compile(r'\.py$', re.IGNORECASE)

class Bot(commands.Bot):
    ''' The custom discord ext bot '''

    __slots__ = (
        'config',
        'logger',
        'start_time',
        'output_chan',
    )

    def __init__(self, config):
        self.config = config
        self.start_time = datetime.datetime.utcnow()
        self.output_chan = None
        super().__init__(command_prefix=config['prefix'],
                         description='maware\'s self-bot',
                         pm_help=False,
                         self_bot=True)

    @property
    def uptime(self):
        ''' Gets the uptime for the bot '''
        return datetime.datetime.utcnow() - self.start_time

    def run(self):
        '''Replace discord clients run command to inculde token from config
        If the token is empty or incorrect raises LoginError
        '''

        if not self.config['token']:
            err_msg = 'Token is empty. Please open the config file and add your token!'
            logger.critical(err_msg)
        else:
            return super().run(self.config['token'], bot=False)

    async def on_ready(self):
        ''' When bot has fully logged on
        Log bots username and ID
        Then load cogs
        '''

        if self.config['output-channel'] is None:
            logger.warn('No output channel set in config.')
        else:
            self.output_chan = self.get_channel(int(self.config['output-channel']))

        self.add_cog(Reloader(self))
        logger.info('Loaded cog: Reloader')

        files = [PY_FILE_REGEX.sub('', file) for file in listdir('mawabot/cogs') if '.py' in file]

        logger.debug(f'Files found: {files}')

        for file in files:
            try:
                self.load_extension(f'mawabot.cogs.{file}')
            except Exception as error:
                # Something made the loading fail
                # So log it with reason and tell user to check it
                logger.debug(f'Load failed: {file}', exc_info=error)
                continue
            else:
                logger.info(f'Loaded cog: {file}')

        channels = sum(1 for _ in self.get_all_channels())
        logger.info(f'Logged in as {self.user.name} ({self.user.id})')
        logger.info('Connected to:')
        logger.info(f'* {len(self.guilds)} guilds')
        logger.info(f'* {channels} channels')
        logger.info(f'* {len(self.users)} users')
        logger.info('------')
        logger.info('Ready!')

        await self.change_presence(status=discord.Status.invisible)
        logger.info('Setting status to invisible')
    
    async def on_resumed(self):
        ''' Used when the bot reconnects '''

        logger.info('Reconnected - setting status to invisible')
        await self.change_presence(status=discord.Status.invisible)

    async def _send(self, *args, **kwargs):
        if self.output_chan is None:
            logger.warn('No output channel set!')
        else:
            await self.output_chan.send(*args, **kwargs)
