#
# __init__.py
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
__init__.py
mawabot - A discord selfbot to do basic tasks
'''

from . import client

__all__ = [
    '__version__',
    'client'
]

__version__ = '0.1.2'
