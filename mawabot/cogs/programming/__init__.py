from .core import Programming

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Programming(bot)
    bot.add_cog(cog)
