from .core import Text

def setup(bot):
    ''' Setup function to add cog to bot '''
    cog = Text(bot)
    bot.add_cog(cog)
