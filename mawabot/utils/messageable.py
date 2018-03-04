#
# utils/messageable.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

import asyncio
import itertools
from functools import reduce

__all__ = [
    'MultiMessageable',
]

class MultiTyping:
    __slots__ = (
        'typings',
    )

    def __init__(self, typings):
        self.typings = typings

    def __enter__(self):
        for typing in self.typings:
            typing.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        for typing in self.typings:
            typing.__exit__(exc_type, exc, tb)

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc, tb):
        self.__exit__(exc_type, exc, tb)

class MultiMessageable:
    __slots__ = (
        'messageables',
    )

    def __init__(self, messageables):
        self.messageables = messageables

    async def send(self, *args, **kwargs):
        return await asyncio.gather(msgr.send(*args, **kwargs) for msgr in self.messageables)

    async def get_message(self, id):
        messages = await asyncio.gather(msgr.get_message(id) for msgr in self.messageables)
        return reduce(lambda x, y: x or y, messages)

    async def trigger_typing(self):
        await asyncio.gather(msgr.trigger_typing() for msgr in self.messageables)

    def typing(self):
        return MultiTyping(tuple(msgr.typing() for msgr in self.messageables))

    async def pins(self):
        pins_list = await asyncio.gather(msgr.pins() for msgr in self.messageables)
        return list(itertools.chain.from_iterable(pins_list))

    def history(self):
        return [msgr.history() for msgr in self.messageables]
