"""
 geolocate parser

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import re
import sys
import collections

import geolocate.classes.exceptions as exceptions


class GeolocateInputParser(object):

    _VERBOSITY_FIELDS = ["continent_name",
                         "country_name",
                         "city_name",
                         "lat-long"]
    VERBOSITY_LEVELS = range(len(_VERBOSITY_FIELDS))
    _IP_NOT_FOUND_MESSAGE = "[IP not found]"

    def __init__(self, verbosity, geoip_database, text=None):
        self._verbosity = verbosity
        self._geoip_database = geoip_database
        if text is None:
            self._entered_text = InputReader()
        else:
            self._entered_text = _get_lines(text)

    def __iter__(self):
        return self

    def __next__(self):
        """Read a line from entered text, search for an IP and get
        their geolocation data.
        """
        # We could analyze the whole text but it is expected that input
        # will come from another program's output through a shell pipe,
        # so in that case is more efficient reading lines as they
        # arrive from the pipe.
        for line in self._entered_text:
            try:
                ip_list = _find_ips_in_text(line)
                for ip in ip_list:
                    location = self._locate(ip)
                    line = _include_location_in_line(line, ip, location)
                return line
            except exceptions.IPNotFound as e:
                location_string = _join_ip_to_location(e.failed_IP,
                                                       self.__class__._IP_NOT_FOUND_MESSAGE)
                line = _include_location_in_line(line, e.failed_IP,
                                                 location_string)
                return line
        raise StopIteration()

    def _locate(self, ip):
        """Query database to get IP address location and format
        location depending of desired verbosity.

        :param ip: String with IP address.
        :type ip: str
        :return: String with location.
        :rtype: str
        :raises: exceptions.IPNotFound.
        """
        try:
            location_data = self._geoip_database.locate(ip)
        except exceptions.IPNotFound:
            raise
        location_string = self._format_location_string(location_data)
        returned_string = _join_ip_to_location(ip, location_string)
        return returned_string

    def _format_location_string(self, location_data):
        """Add location fields to returned string depending of desired
        verbosity.

        :param location_data: GeoIP record.
        :type location_data: geoip2.models.City
        :return: String with location.
        :rtype: str
        """
        # TODO: This code sucks, I have to refactor it.
        location_string = "["
        verbosity_levels_to_show = range(self._verbosity+1)
        VERBOSITY_FIELDS = self.__class__._VERBOSITY_FIELDS
        location_fields = _find_unknowns(location_data)
        # The more verbosity the more data you append to returned string.
        for i in verbosity_levels_to_show:
            if VERBOSITY_FIELDS[i] == "lat-long":
                lat_long = ", ".join([location_fields["lat-long"]["latitude"],
                                      location_fields["lat-long"]["longitude"]])
                location_string = " | ".join([location_string,
                                              lat_long])
            elif VERBOSITY_FIELDS[i] == "continent_name":
                # Continent_name is first level of verbosity so it is not
                # prepended by an "|"
                location_string = "".join([location_string,
                                          location_fields["continent_name"]])
            elif VERBOSITY_FIELDS[i] == "city_name":
                location_string = " | ".join([location_string,
                                              location_fields["city_name"]])
            elif VERBOSITY_FIELDS[i] == "country_name":
                location_string = " | ".join([location_string,
                                              location_fields["country_name"]])
        location_string = "".join([location_string, "]"])
        return location_string


def _find_unknowns(location_data):
    """ Find any unknown attribute and convert it in a informational string.

    :param location_data: GeoIP record.
    :type location_data: geoip2.models.City
    :return: Informational strings.
    :rtype: dict
    """
    location_strings = _default_location_strings()
    if location_data.continent.name is None:
        location_strings["continent_name"] = "Unknown continent"
    else:
        location_strings["continent_name"] = location_data.continent.name
    if location_data.country.name is None:
        location_strings["country_name"] = "Unknown country"
    else:
        location_strings["country_name"] = location_data.country.name
    if location_data.city.name is None:
        location_strings["city_name"] = "Unknown city"
    else:
        location_strings["city_name"] = location_data.city.name
    if location_data.location.latitude is None:
        location_strings["lat-long"]["latitude"] = "Unknown latitude"
    else:
        location_strings["lat-long"]["latitude"] = str(location_data.location.latitude)
    if location_data.location.longitude is None:
        location_strings["lat-long"]["longitude"] = "Unknown longitude"
    else:
        location_strings["lat-long"]["longitude"] = str(location_data.location.longitude)
    return location_strings


def _default_location_strings():
    """ Generates a dict object suitable for location strings.

    :return: location strings object.
    :rtype: dict
    """
    location_strings = collections.defaultdict()
    location_strings["lat-long"] = collections.defaultdict()
    return location_strings


def _find_ips_in_text(text):
    """Return a set with all IP addresses found in text

    :param text: Text with IP addresses embedded.
    :type text: str
    :return: A set with all addresses found.
    :rtype: set
    """
    ipv4_addresses = _find_ipv4_addresses(text)
    # TODO: Implement a _find_ipv6_addresses() so in the end we can do:
    #          found_addresses = ipv4_addresses.union(ipv6_addresses)
    found_addresses = ipv4_addresses
    return found_addresses


def _find_ipv4_addresses(text):
    """
    :param text: Text with IP addresses embedded.
    :type text: str
    :return: A set with all addresses found.
    :rtype: set
    """
    ip_filter = "[0-9]+(?:\.[0-9]+){3}"
    regex_filter = re.compile(ip_filter)
    addresses = regex_filter.findall(text)
    return set(addresses)


def _include_location_in_line(line, ip, location):
    """
    :param line: Original line to place location string into.
    :type line: str
    :param ip: IP address to be replaced with location.
    :type ip: str
    :param location: IP address string with location data appended.
    :type location: str
    :return: Line with ip addresses followed by location strings.
    :rtype: str
    """
    return line.replace(ip, location)


def _join_ip_to_location(ip, location):
    """
    :param ip: IP address.
    :type ip: str
    :param location: Location data string.
    :return: IP address with location data string appended.
    :rtype: str
    """
    location_string = " ".join([ip, location])
    return location_string


def _get_lines(text):
    """ Get a generator object with text lines.

    :param text: Text to parse.
    :type text: str
    :return: Text lines.
    :rtype: generator
    """
    lines = (line for line in text.split("\n"))
    return lines


class InputReader(object):
    """Iterator to read piped input from other programs."""

    def __init__(self):
        pass

    def __iter__(self):
        return self

    @staticmethod
    def __next__():
        for line in sys.stdin:
            return line
        raise StopIteration()