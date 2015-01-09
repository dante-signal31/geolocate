#!/usr/bin/env python3
"""
 geolocate

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com

This scripts scan given text to find urls and IP addresses. The output is the
same text but every url and IP address is going to have its geolocation
appended.

Geolocate is possible thanks to `Maxmind GeoIP database <http://www.maxmind.com>`_
and their API.
"""
import argparse
from classes import geowrapper
from classes import parser
from classes import config


def parse_arguments():
    verbosity_choices = parser.GeolocateInputParser.VERBOSITY_LEVELS
    arg_parser = argparse.ArgumentParser(description="Locate IP adresses "
                                                 "in given text.\n")
    arg_parser.add_argument(dest="text_to_parse", metavar="\"text to parse\"",
                            nargs="?", type=str, default=None,
                            help="Text to analyze surrounded by double quotes.")
    arg_parser.add_argument("-v", "--verbosity", dest="verbosity",
                            choices=verbosity_choices, type=int, default=0,
                            help="0-3 The higher the more geodata.")
    arg_parser.add_argument("-l", "--enabled", dest="list_locators",
                            action="store_true", default=False,
                            help="Show enabled locators ordered by preference.")
    arg_parser.add_argument("-p", "--preference", dest="locator_preference",
                            nargs="?", type=list, default=None,
                            help="Preferred locator order.",
                            metavar="locator1 locator2 locator3")
    arg_parser.add_argument("-d", "--disabled",
                            dest="list_disabled_locators", action="store_true",
                            default=False, help="Show disabled locators.")
    arg_parser.add_argument("-r", "--reset", dest="reset_locators",
                            action="store_true", default=False,
                            help="Restore default locator order.")
    return arg_parser.parse_args()


def print_lines_parsed(parser):
    for line in parser:
        print(line, end="")


def process_optional_parameters(arguments):
    # TODO: Locators preference should be stored in configuration between
    # sessions. I have to connect configuration and geowrapper objects.
    if arguments.list_locators:
        print_enabled_locators()
    if arguments.list_disabled_locators:
        print_disabled_locators()
    if arguments.reset_locators:
        reset_locators()
    if arguments.locator_preference is not None:
        set_locator_preference(arguments.locator_preference)

if __name__ == "__main__":
    arguments = parse_arguments()
    configuration = config.load_configuration()
    process_optional_parameters(arguments)
    geoip_database = geowrapper.load_geoip_database(configuration)
    input_parser = parser.GeolocateInputParser(arguments.verbosity,
                                               geoip_database,
                                               arguments.text_to_parse)
    print_lines_parsed(input_parser)
    print()