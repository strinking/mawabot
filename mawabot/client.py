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

import discord
from discord.ext import commands

COGS = [
    'mawabot.cogs.general',
    'mawabot.cogs.guild',
    'mawabot.cogs.info',
    'mawabot.cogs.messages',
    'mawabot.cogs.text',
]


class Bot(commands.Bot):
    ''' The custom discord ext bot '''

    __slots__ = (
        'config',
        'logger',
        'start_time',
        'output_chan',
    )

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
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
            self.logger.critical(err_msg)
        else:
            return super().run(self.config['token'], bot=False)

    async def on_ready(self):
        ''' When bot has fully logged on
        Log bots username and ID
        Then load cogs
        '''

        if self.config['output-channel'] is None:
            self.logger.warn('No output channel set in config.')
        else:
            self.output_chan = self.get_channel(int(self.config['output-channel']))

        for cog in COGS:
            self.load_extension(cog)
            self.logger.info(f'Loaded cog: {cog}')

        channels = sum(1 for _ in self.get_all_channels())
        self.logger.info(f'Logged in as {self.user.name} ({self.user.id})')
        self.logger.info('Connected to:')
        self.logger.info(f'* {len(self.guilds)} guilds')
        self.logger.info(f'* {channels} channels')
        self.logger.info(f'* {len(self.users)} users')
        self.logger.info('------')
        self.logger.info('Ready!')

    async def _send(self, *args, **kwargs):
        if self.output_chan is None:
            self.logger.warn('No output channel set!')
        else:
            await self.output_chan.send(*args, **kwargs)
