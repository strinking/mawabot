from .core import General

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = General(bot)
    bot.add_cog(cog)