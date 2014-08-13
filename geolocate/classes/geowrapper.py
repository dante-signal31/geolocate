"""
 geolocate wrapper to Geolite2 API.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import abc
import subprocess
import tempfile
import geoip2.database
import geoip2.webservice

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
        """
        :param configuration: Geolocate configuration.
        :type configuration: config.Configuration
        :return: None
        """
        super().__init__(configuration)
        self._db_connection = geoip2.webservice.Client(configuration.user_id,
                                                       configuration.license_key)

class LocalDatabaseGeoLocator(GeoLocator):

    def __init__(self, configuration):
        """
        :param configuration: Geolocate configuration.
        :type configuration: config.Configuration
        :return: None
        """
        super().__init__(configuration)
        self._update_db()
        db_path = configuration.local_database_path
        self._db_connection = geoip2.database.Reader(db_path)

    def _update_db(self):
        """ Download a fresh geolocation database if current is too old.

        :return: None
        """
        if self._local_database_too_old():
            self._download_fresh_database()

    def _local_database_too_old(self):
        """
        :return: True if database file has to be refreshed, False if not.
        :rtype: bool
        """
        ## TODO: Implement.
        pass

    def _download_fresh_database(self):
        """ Download compressed database, decompress it and place it instead
        old one.

        :return: None
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            self._download_file(temporary_directory.name)
            decompressed_file_path = _decompress_file(temporary_directory)
            self._remove_old_database()
            self._copy_new_database(decompressed_file_path)

    def _download_file(self, temporal_directory):
        """
        :param temporal_directory: Folder path to place downloaded file in.
        :type temporal_directory: str
        :return: None
        """
        downloads_folder_parameter = "--directory-prefix={0}".format(temporal_directory)
        subprocess.call(["wget", self._configuration.download_url,
                        downloads_folder_parameter])

    def _remove_old_database(self):
        """
        :return: None
        """
        ## TODO: Implement.
        pass

    def _copy_new_database(self, decompressed_file_path):
        """
        :param decompressed_file_path: Folder where new database is placed.
        :type decompressed_file_path: str
        :return: None
        """
        ## TODO: Implement.
        pass


def _decompress_file(temporal_directory):
    """ Decompress tar.gz file found in temporal_directory.

    :param temporal_directory: Folder path to compressed file.
    :type temporal_directory: str
    :return: Path to decompressed folder.
    :rtype: str
    """
    ## TODO: Implement.
    pass


class IPNotFound(Exception):

    def __init__(self, IP):
        message = "The address {0} is not in the database.".format(IP)
        Exception.__init__(self, message)
        self.failed_IP = IP


