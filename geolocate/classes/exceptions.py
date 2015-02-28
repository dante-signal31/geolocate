"""
 Custom exceptions for geolocate.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

# TODO: Find the way to take this code back to geowrapper module.
# This class shouldn't be here. Initially it was defined at geowrapper module.
# Problem is that when class is there, test_GeolocateInputParser_next (at
# test_parser.TestParser) fails because IPNotFound is not caught in parser's
# GeoLocateInputParser __next__(). I don't know why but if I take off IPNotFound
# definition from geowrapper module and put it in another module, like this one,
# the code runs as intended and tests success.
class IPNotFound(Exception):
    """ Searched IP is not in geolocation database."""

    def __init__(self, ip_address):
        self.failed_IP = ip_address
        self.message = "The address {0} is not in the database.".format(ip_address)
        Exception.__init__(self, self.message)