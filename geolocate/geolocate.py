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
    # TODO: Implement arguments to deal with preferences of multiple locator.
    verbosity_choices = parser.GeolocateInputParser.VERBOSITY_LEVELS
    arg_parser = argparse.ArgumentParser(description="Locate IP adresses and "
                                                 "URLs in given text.\n")
    arg_parser.add_argument(dest="text_to_parse", metavar="text to parse",
                            nargs="?", type=str, default=None,
                            help="Text to analyze surrounded by double quotes.")
    arg_parser.add_argument("-v", "--verbosity", dest="verbosity",
                            choices=verbosity_choices, type=int, default=0,
                            help="0-3 The higher the more geodata.")
    return arg_parser.parse_args()


def print_lines_parsed(parser):
    for line in parser:
        print(line, end="")

if __name__ == "__main__":
    arguments = parse_arguments()
    configuration = config.load_configuration()
    geoip_database = geowrapper.load_geoip_database(configuration)
    input_parser = parser.GeolocateInputParser(arguments.verbosity,
                                               geoip_database,
                                               arguments.text_to_parse)
    print_lines_parsed(input_parser)
    print()