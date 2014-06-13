"""
 geolocate parser

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import fileinput
import re
import sys

############
# CLASSES
############
class GeolocateInputParser(object):

    _VERBOSITY_FIELDS = ["continent_name",
                         "country_name",
                         "city_name",
                         "lat-long"]
    VERBOSITY_LEVELS = range(len(_VERBOSITY_FIELDS))

    def __init__(self, verbosity, geoip_database):
        self._verbosity = verbosity
        self._geoip_database = geoip_database
        self._entered_text = InputReader()

    def __iter__(self):
        return self

    ## TODO: Write unittest for __next__().
    def __next__(self):
        """Read a line from entered text, search for an IP and get
        their geolocation data.
        """
        for line in self._entered_text:
            try:
                ip_list = _find_ips_in_text(line)
                for ip in ip_list:
                    location = self._locate(ip)
                    new_line = _include_location_in_line(line,
                                                         ip,
                                                         location)
                    return new_line
            except NoURLOrIPFound:
                return line
        raise StopIteration()

    def _locate(self, ip):
        """Query database to get IP address location and format
        location depending of desired verbosity.

        :param ip: String with P address.
        :type ip: str
        :returns: String with location.
        :rtype: str
        """
        location_data = self._geoip_database.locate(ip)
        location_string = self._format_location_string(location_data)
        returned_string = _join_ip_to_location(ip, location_string)
        return returned_string

    def _format_location_string(self, location_data):
        """Add location fields to returned string depending of desired
        verbosity.

        :param location_data: GeoIP record.
        :type location_data: dict
        :returns: String with location.
        :rtype: str
        """
        location_string = "["
        verbosity_levels_to_show = range(self._verbosity+1)
        VERBOSITY_FIELDS = self.__class__._VERBOSITY_FIELDS
        # The more verbosity the more data you append to returned string.
        for i in verbosity_levels_to_show:
            if VERBOSITY_FIELDS[i] == "lat-long":
                lat_long = ", ".join([location_data["latitude"],
                                      location_data["longitude"]])
                location_string = " | ".join([location_string,
                                              lat_long])
            elif VERBOSITY_FIELDS[i] == "continent_name":
                # Continent_name is first level of verbosity so it is not
                # prepended by an "|"
                location_string = "".join([location_string,
                                          location_data["continent_name"]])
            else:
                location_string = " | ".join([location_string,
                                              location_data[VERBOSITY_FIELDS[i]]])
        location_string = "".join([location_string, "]"])
        return location_string


def _find_ips_in_text(text):
    """Return a set with all IP addresses found in text

    :param text: Text with IP addresses embedded.
    :type text: str
    :returns: A set with all addresses found.
    :rtype: set
    """
    ipv4_addresses = _find_ipv4_addresses(text)
    ## TODO: Implement a _find_ipv6_addresses() so in the end we can do:
    ##          found_addresses = ipv4_addresses.union(ipv6_addresses)
    found_addresses = ipv4_addresses
    return found_addresses


def _find_ipv4_addresses(text):
    """
    :param text: Text with IP addresses embedded.
    :type text: str
    :returns: A set with all addresses found.
    :rtype: set
    """
    filter = "[0-9]+(?:\.[0-9]+){3}"
    regex_filter = re.compile(filter)
    addresses = regex_filter.findall(text)
    return set(addresses)


def _include_location_in_line(line, ip, location):
    return line.replace(ip, location)



def _join_ip_to_location(ip, location_string):
    returned_string = " ".join([ip, location_string])
    return returned_string


class NoURLOrIPFound(Exception):
    pass


class InputReader:
    """Iterator to read piped input from other programs."""

    def __init__(self):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        for line in sys.stdin:
            return line
        raise StopIteration()



