'''
client.py
Holds the custom discord client
'''
import datetime

import discord
from discord.ext import commands

COGS = [
    'mawabot.cogs.general',
]


class Bot(commands.Bot):
    ''' The custom discord ext bot '''

    def __init__(self, config, logger):
        self.config = config
        self.start_time = datetime.datetime.utcnow()
        self.logger = logger
        super().__init__(command_prefix=config['prefix'],
                         description='maware\'s self bot to do stuff',
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

        self.logger.info(('Logged in as: '
                          f'{self.user.name} ({self.user.id})'))

        for cog in COGS:
            self.load_extension(cog)
            self.logger.info(f'Loaded cog: {cog}')
