#
# utils/functions.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

import unicodedata

__all__ = [
    'normalize_caseless',
]

def normalize_caseless(s):
    return unicodedata.normalize('NFKD', s.casefold())
