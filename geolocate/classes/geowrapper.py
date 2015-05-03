"""
 geolocate wrapper to Geolite2 API.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import abc
import datetime
import gzip
import os
import shutil
# import subprocess
import tempfile
import geoip2.database as database
import geoip2.webservice as webservice
import maxminddb
import wget


import geolocate.classes.config as config
import geolocate.classes.exceptions as exceptions

DEFAULT_DATABASE_FILE_EXTENSION = "mmdb"
GEOIP2_WEBSERVICE_TAG = "geoip2_webservice"
GEOIP2_LOCAL_TAG = "geoip2_local"


def load_geoip_database(configuration=None):
    return GeoIPDatabase(configuration)


class GeoIPDatabase(object):
    """ Location engines may have multiple query methods. This class
    encapsulates them all in _locators list.
    """
    def __init__(self, configuration):
        """
        :param configuration: Geolocate configuration.
        :type configuration: config.Configuration
        """
        self._configuration = configuration
        self._locators = {}
        self._add_locators()
        self._locators_preference = configuration.locators_preference

    def _add_locators(self):
        """ Add query methods for this location engine.

        :return: None
        """
        self._add_webservice_locator()
        self._add_local_database_locator()

    def _web_service_access_configured(self):
        """
        :return: True if access credential to web service are configured, False if not.
        :rtype: bool
        """
        default_user_id = config.DEFAULT_USER_ID
        default_license_key = config.DEFAULT_LICENSE_KEY
        if self._configuration.user_id != default_user_id and \
           self._configuration.license_key != default_license_key:
            return True
        else:
            return False

    def _add_webservice_locator(self):
        """
        :return: None
        """
        if self._web_service_access_configured():
            webservice_locator = WebServiceGeoLocator(self._configuration)
            self._locators[GEOIP2_WEBSERVICE_TAG] = webservice_locator

    def _add_local_database_locator(self):
        """
        :return: None
        """
        local_db_locator = LocalDatabaseGeoLocator(self._configuration)
        self._locators[GEOIP2_LOCAL_TAG] = local_db_locator

    @property
    def geoip2_webservice(self):
        """
        :return: GeoIPLocateor to query GeoIP webservice.
        :rtype: WebServiceGeoLocator
        :raises: GeoIP2WebServiceNotConfigured
        """
        try:
            return self._locators[GEOIP2_WEBSERVICE_TAG]
        except KeyError:
            raise GeoIP2WebServiceNotConfigured()

    @property
    def geoip2_local(self):
        return self._locators[GEOIP2_LOCAL_TAG]

    def locate(self, ip):
        """ Query enabled locators in preference order until getting any
        geodata.

        :param ip: IP address to look for.
        :type ip: IP address string.
        :return: Location data for that address.
        :rtype: geoip2.models.City
        """
        for locator_id in self._locators_preference:
            # TODO: Try to disable webservice to see if this is really working.
            try:
                locator = self._locators[locator_id]
                geodata = locator.locate(ip)
            except:
                continue
            else:
                break
        else:
            raise exceptions.IPNotFound(ip)
        return geodata


class GeoLocator(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, configuration):
        self._configuration = configuration
        self._db_connection = None

    def locate(self, ip):
        """ Get geolocation data from database.

        :param ip: IP address we are asking about.
        :type ip: str
        :raises: geoip2.errors.AddressNotFoundError
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
        self._db_connection = webservice.Client(configuration.user_id,
                                                configuration.license_key)


class LocalDatabaseGeoLocator(GeoLocator):
    def __init__(self, configuration):
        """
        :param configuration: Geolocate configuration.
        :type configuration: config.Configuration
        :return: none
        :raise: LocalDatabaseNotFound
        :raise: InvalidLocalDatabase
        """
        super().__init__(configuration)
        self._update_db()
        db_path = configuration.local_database_path
        self._db_connection = _open_local_database(db_path)

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
        database_path = self._configuration.local_database_path
        update_interval = self._configuration.update_interval
        try:
            last_modification = _get_database_last_modification(database_path)
        except LocalDatabaseNotFound:
            return True  # This should force a database download.
        else:
            today_date = datetime.date.today()
            allowed_age = datetime.timedelta(days=update_interval)
            return _must_be_updated(today_date, last_modification, allowed_age)

    def _download_fresh_database(self):
        """ Download compressed database, decompress it and place it instead
        old one.

        :return: None
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            print("Downloading fresh geolocation database...")
            self._download_file(temporary_directory)
            try:
                _decompress_file(temporary_directory)
            except CompressedFileNotFound as e:
                _print_compressed_file_not_found_error(e)
            else:
                self._write_new_database(temporary_directory)

    def _download_file(self, temporal_directory):
        """
        :param temporal_directory: Folder path to place downloaded file in.
        :type temporal_directory: str
        :return: None
        """
        wget.download(url=self._configuration.download_url,
                      out=temporal_directory)

    def _remove_old_database(self):
        """
        :return: None
        """
        database_path = self._configuration.local_database_path
        os.remove(database_path)

    def _write_new_database(self, temporary_directory):
        """
        :param temporary_directory: Folder path to place downloaded file in.
        :type temporal_directory: str
        :return: None
        """
        try:
            self._remove_old_database()
        except FileNotFoundError:
            print("\nOld local database not found. May be this is the "
                  "first time you run geolocate?.")
        self._copy_new_database(temporary_directory)

    def _copy_new_database(self, decompressed_file_path):
        """
        :param decompressed_file_path: Folder where new database is placed.
        :type decompressed_file_path: str
        :return: None
        """
        database_path = self._configuration.local_database_path
        new_database_path = _get_new_database_path_name(decompressed_file_path)
        shutil.copyfile(new_database_path, database_path)


def _decompress_file(temporary_directory):
    """ Decompress tar.gz file found in temporary_directory.

    :param temporary_directory: Folder path to compressed file.
    :type temporary_directory: str
    :return: Path to decompressed folder.
    :rtype: str
    """
    try:
        compressed_file_name_path = _find_compressed_file(temporary_directory)
        uncompressed_file_name_path = _get_uncompressed_file_name_path(compressed_file_name_path)
    except CompressedFileNotFound as e:
        _print_compressed_file_not_found_error(e)
    else:
        with gzip.open(compressed_file_name_path, "rb") as input_file, \
                open(uncompressed_file_name_path, "wb") as output_file:
            uncompressed_content = input_file.read()
            output_file.write(uncompressed_content)
        return compressed_file_name_path


def _find_compressed_file(temporary_directory):
    """ Find .gz file name downloaded to temporary directory.

    :param temporary_directory: Folder to search compressed file in.
    :type temporary_directory: str
    :return: Absolute path name of found file.
    :rtype: str
    :raise: CompressedFileNotFound
    """
    for file_name in os.listdir(temporary_directory):
        if file_name.endswith(".gz"):
            file_name_path = os.path.join(temporary_directory, file_name)
            return file_name_path
    else:
        raise CompressedFileNotFound(temporary_directory)

def _get_uncompressed_file_name_path(compressed_file_name_path):
    """ Get file name compressed in .gz file.

    :param compressed_file_name_path: Compressed file name absolute path.
    :type compressed_file_name_path: str
    :return: File name compressed into .gz file.
    :rtype: str
    """
    uncompressed_file_name_path = os.path.splitext(compressed_file_name_path)[0]
    return uncompressed_file_name_path

def _open_local_database(local_database_path):
    try:
        database_connection = database.Reader(local_database_path)
    except FileNotFoundError:
        raise LocalDatabaseNotFound(local_database_path)
    except maxminddb.InvalidDatabaseError:
        raise InvalidLocalDatabase(local_database_path)
    else:
        return database_connection


def _get_database_last_modification(database_path):
    """
    :param database_path: Path to database file to be evaluated.
    :type database_path: str
    :return: Date of file's last modification.
    :rtype: datetime.date
    """
    try:
        last_modification = os.stat(database_path).st_mtime
    except FileNotFoundError:
        raise LocalDatabaseNotFound(database_path)
    else:
        date_last_modification = datetime.date.fromtimestamp(last_modification)
        return date_last_modification


def _must_be_updated(today_date, last_modification, allowed_age):
    """
    :param today_date: Today's date.
    :type today_date: datetime.date
    :param last_modification: Date of file's last modification.
    :type last_modification: datetime.date
    :param allowed_age: Maximum age allowed between today and last modification.
    :type allowed_age: datetime.timedelta
    :return: True if last modification is older than allowed age; else False.
    :rtype: bool
    """
    if today_date - last_modification > allowed_age:
        return True
    else:
        return False


def _get_new_database_path_name(decompressed_file_path):
    """
    :param decompressed_file_path: Temporary folder path where new database is.
    :type decompressed_file_path: str
    :return: Temporary folder with database filename and extension appended.
    :rtype: str
    """
    decompressed_files = os.listdir(decompressed_file_path)
    for file in decompressed_files:
        if file.endswith(DEFAULT_DATABASE_FILE_EXTENSION):
            new_database_path_name = os.path.join(decompressed_file_path, file)
            return new_database_path_name
    else:
        raise NotValidDatabaseFileFound(decompressed_file_path)


def _print_compressed_file_not_found_error(e):
    """
    :param e: Exception caught.
    :type e: CompressedFileNotFound
    :return: none
    """
    print("Problem decompressing updated database.")
    path = e.compressed_database_path
    message = "No .gz file found at {0}".format(path)
    print(message)


class GeoIP2WebServiceNotConfigured(Exception):
    """ GeoIP2 WebService access is still not configured."""

    def __init__(self):
        message = "You tried a query to GeoIP2 webservice, but no valid " \
                  "credentials were found in configuration."
        Exception.__init__(self, message)


class LocalDatabaseNotFound(OSError):
    """ Local database file is missing."""

    def __init__(self, local_database_path):
        self.local_database_path = local_database_path
        message = "Local database file is missing"
        OSError.__init__(self, message)


class InvalidLocalDatabase(Exception):
    """ Local database exists but is corrupted. """

    def __init__(self, local_database_path):
        self.local_database_path = local_database_path
        message = "Local database is invalid."
        Exception.__init__(self, message)


class NotValidDatabaseFileFound(OSError):
    """ Raised when a new database pack is downloaded on local, but after
    decompression no valid database file is found in decompressed folder.
    """

    def __init__(self, decompressed_database_path):
        self.decompressed_database_path = decompressed_database_path
        message = "No valid database found in downloaded file."
        OSError.__init__(self, message)


class CompressedFileNotFound(OSError):
    """ Raised when no .gz compressed file is found in temporary folder where
    downloaded data is placed.
    """

    def __init__(self, compressed_database_path):
        self.compressed_database_path = compressed_database_path
        message = "No compressed file found in downloaded data."
        OSError.__init__(self, message)