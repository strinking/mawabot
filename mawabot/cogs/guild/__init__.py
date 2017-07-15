from .core import Guild

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Guild(bot)
    bot.add_cog(cog)
