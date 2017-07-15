from .core import Messages

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Messages(bot)
    bot.add_cog(cog)
