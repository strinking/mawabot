#
# __main__.py
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
__main__.py
Used to run the bot on it's own
'''

import argparse
import logging
import json
import sys

from . import client

LOG_FILE = 'mawabot.log'
LOG_FILE_MODE = 'w'
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "[%d/%m/%Y %H:%M]"

if __name__ == '__main__':
    # Parse arguments
    argparser = argparse.ArgumentParser(description='maware\'s self-bot')
    argparser.add_argument('-q', '--quiet', '--no-stdout',
        dest='stdout', action='store_false',
        help="Don't output to standard out.")
    argparser.add_argument('-d', '--debug',
            dest='debug', action='store_true',
            help="Set logging level to debug.")
    argparser.add_argument('config_file',
            help="Specify a configuration file to use. Keep it secret!")
    args = argparser.parse_args()

    # Set up logging
    log_fmtr = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    log_hndl = logging.FileHandler(filename=LOG_FILE,
                                   encoding='utf-8', mode=LOG_FILE_MODE)
    log_hndl.setFormatter(log_fmtr)
    log_level = logging.INFO

    logger = logging.getLogger(__package__)
    logger.setLevel(level=log_level)
    logger.addHandler(log_hndl)

    if args.debug:
        dis_logger = logging.getLogger('discord')
        dis_logger.setLevel(level=log_level)
        dis_logger.addHandler(log_hndl)

    if args.stdout:
        log_hndl = logging.StreamHandler(sys.stdout)
        log_hndl.setFormatter(log_fmtr)
        logger.addHandler(log_hndl)
        if args.debug:
            dis_logger.addHandler(log_hndl)

    try:
        # Load config
        with open(args.config_file, 'r') as jsonfile:
            config = json.load(jsonfile)
    except (json.decoder.JSONDecodeError, IOError) as err:
        logger.error("Configuration file was invalid.")
        exit(1)

    # Open and run client
    logger.info("Starting bot...")
    bot = client.Bot(config)
    bot.run()
