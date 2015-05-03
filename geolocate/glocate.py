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

import geolocate.classes.arguments as arguments
import geolocate.classes.geowrapper as geowrapper
import geolocate.classes.parser as parser
import geolocate.classes.config as config

import sys

def print_lines_parsed(parser):
    for line in parser:
        print(line, end="")


def main():
    _arguments = arguments.parse_arguments()
    arguments.process_optional_parameters(_arguments)
    configuration = config.load_configuration()
    geoip_database = geowrapper.load_geoip_database(configuration)
    if _arguments.text_to_parse or _arguments.stream_mode:
        input_parser = parser.GeolocateInputParser(_arguments.verbosity,
                                                   geoip_database,
                                                   _arguments.text_to_parse)
        print_lines_parsed(input_parser)
    print()

if __name__ == "__main__":
    main()