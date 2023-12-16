#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 04:03:50 2020

@author: taylor
"""
# From the 'argparse' standard library module we'll import the ArgumentParser
# class which we'll use to...parse command line arguments.
from argparse import ArgumentParser

# Bring in the standard 'logging' librarys class getLogger which (if we
# reference it correctly) will bring our formatted logger in when we want it.
from logging import getLogger


# From the inspy_logger package we import the InspyLogger class, which we'll
# later instantiate as our log device.
from inspy_logger import InspyLogger

from inspy_logger import LEVELS as LOG_LVLS



app_name = "example_2.py"
app_desc = "A simple application used as a receipe for using inSPy-Logger in an application where one can set the verbosity of the programs output."


def start_logger(log_lvl, no_ver):

    # Instantiate an InspyLogger class that will have a `start` function
    log_device = InspyLogger(app_name, log_lvl)

    # Get a usable log writer from the start function
    log = log_device.start(no_version=no_ver)

    log.info("Root logger started!")



def arg_parser():

    # Set up the argument parser. Give it the name of our application and a
    # description for the help information
    parser = ArgumentParser(prog=app_name,
                            description=app_desc)

    # Add the `--log-level` argument to the program.
    parser.add_argument('-l', '--log-level',
                        nargs='?',
                        choices=LOG_LVLS,
                        default='info',
                        help=f"Indicate the level at which you want `{app_name}` to output log messages.")
    parser.add_argument('-n', '--no-log-info',
                        action='store_true',
                        default=False,
                        help="The logger will output some information when it starts. Call this argument and it will not."
                       )

    return parser.parse_args()


def run():
    args = arg_parser()
    print(args)
    start_logger(args.log_level, args.no_log_info)
    log_name = app_name + ".run"
    log = getLogger(log_name)
    debug = log.debug
    debug("Logger started for main runner")
    debug(f"Argument state from commandline at runtime was: {args}")
    try:
        raise NameError('Yep, so random')
    except NameError as e:
        log.exception(e)
        log.warning('An exception occurred but we recovered from it.')

    log.info("This test has been a success!")



if __name__ == '__main__':
    run()
