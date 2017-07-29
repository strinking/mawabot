#
# cogs/text/__init__.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

from .core import Text
from .meme import Meme
from .slashes import Slashes

__all__ = [
    'setup',
]

def setup(bot):
    ''' Setup function to add cog to bot '''
    bot.add_cog(Slashes(bot))
    bot.add_cog(Text(bot))
    bot.add_cog(Meme(bot))
