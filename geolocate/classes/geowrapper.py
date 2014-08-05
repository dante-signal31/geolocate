"""
 geolocate wrapper to Geolite2 API.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import abc

import geolocate.classes.config as config

def load_geoip_database(configuration=None):
    ## TODO: Implement this function.
    return GeoIPDatabase(configuration)


class GeoIPDatabase(object):

    def __init__(self, configuration):
        self._configuration = configuration
        self._locators = []
        self._add_locators()

    def _add_locators(self):
        self._add_webservice_locator()
        self._add_local_database_locator()

    def _add_webservice_locator(self):
        if self._configuration.user_id != config.DEFAULT_USER_ID and \
                self._configuration.license_key != config.DEFAULT_LICENSE_KEY:
            webservice_locator = WebServiceGeoLocator(self._configuration)
            self._locators.append(webservice_locator)

    def _add_local_database_locator(self):
        local_db_locator = LocalDatabaseGeoLocator(self._configuration)
        self._locators.append(local_db_locator)


class GeoLocator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, configuration):
        self._configuration = configuration
        self._db_connection = None

    def locate(self, ip):
        """ Get geolocation data from database.
        :param ip: IP address we are asking about.
        :type ip: str
        :return: Geolocation data.
        :rtype: geoip2.models.City
        """
        geolocation_data = self._db_connection.city(ip)
        return geolocation_data


class WebServiceGeoLocator(GeoLocator):

    def __init__(self, configuration):
        pass

class LocalDatabaseGeoLocator(GeoLocator):

    def __init__(self, configuration):
        pass


class IPNotFound(Exception):

    def __init__(self, IP):
        message = "The address {0} is not in the database.".format(IP)
        Exception.__init__(self, message)
        self.failed_IP = IP


