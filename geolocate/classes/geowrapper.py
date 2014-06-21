"""
 geolocate wrapper to Geolite2 API.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

def load_geoip_database(configuration=None):
    ## TODO: Implement this function.
    return GeoIPDatabase()


class GeoIPDatabase(object):
    ## TODO: Implement this class.
    def __init__(self):
        pass

    def locate(self, ip):
        pass


class IPNotFound(Exception):

    def __init__(self, IP):
        message = "The address {0} is not in the database.".format(IP)
        Exception.__init__(self, message)
        self.failed_IP = IP


