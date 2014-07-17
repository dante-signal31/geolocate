"""
 Configuration parser module.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import http.client as http
import os
import pickle
import urllib.parse as urlparse

CONFIG_FILE = "geolocate/etc/geolocate.conf"
CONFIG_FILE_NAME = os.path.abspath(CONFIG_FILE)
DEFAULT_USER_ID = ""
DEFAULT_LICENSE_KEY = ""
## TODO: For production I have to uncomment real url.
# Only for tests I have to comment real download url. MaxMind has a rate limit
# per day. If you exceed that limit you are forbidden for 24 hours to download
# their database.
# DEFAULT_DATABASE_DOWNLOAD_URL = "http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz"
## TODO: For production remove next fake url, it's only for tests.
DEFAULT_DATABASE_DOWNLOAD_URL = "http://old-releases.ubuntu.com/releases/10.04.0/ubuntu-10.04.4-desktop-i386.iso"
# GeoLite2 databases are updated on the first Tuesday of each month, so 35 days
# of update interval should be fine.
DEFAULT_UPDATE_INTERVAL = 35


class Configuration(object):
    # I've discovered Maxmind website blocks clients who exceeds a conenection
    # threshold. If we make a connection each time we run geolocate, in order
    # to check that configured URL is OK, we can end in Maxmind blacklist. So,
    # we have to minimize connections. Check only when configuration is updated
    # is a way, but then we have to control how users update config. Best way
    # is limit users to change configuration only through executable's
    # parameters. If we let them change manually configuration file we should
    # check it each time we run the program. We'd better close configuration
    # file through serialization and check URL only when user makes program
    # change configuration.
    """ Class to encapsulate configuration needed to connect to Geolite2
    webservices or downloaded local database. This class also validates
    parameters read from config files to overcome user typos.
    """
    def __init__(self, user_id=DEFAULT_USER_ID,
                       license_key=DEFAULT_LICENSE_KEY,
                       download_url=DEFAULT_DATABASE_DOWNLOAD_URL,
                       update_interval=DEFAULT_UPDATE_INTERVAL):
        self._webservice = {"user_id": user_id,
                            "license_key": license_key}
        self._local_database = {"download_url": download_url,
                                "update_interval": update_interval}

    @property
    def user_id(self):
        return self._webservice["user_id"]

    @user_id.setter
    def user_id(self, user_id):
        _validate_value("user_id", user_id)
        self._webservice["user_id"] = user_id

    @property
    def license_key(self):
        return self._webservice["license_key"]

    @license_key.setter
    def license_key(self, license_key):
        _validate_value("license_key", license_key)
        self._webservice["license_key"] = license_key

    @property
    def download_url(self):
        return self._local_database["download_url"]

    @download_url.setter
    def download_url(self, url):
        _validate_url("download_url", url)
        self._local_database["download_url"] = url

    @property
    def update_interval(self):
        return self._local_database["update_interval"]

    @update_interval.setter
    def update_interval(self, update_interval_in_days):
        interval_integer = _validate_integer("update_interval",
                                             update_interval_in_days)
        self._local_database["update_interval"] = interval_integer

    def __eq__(self, other):
        for _property, value in vars(self).items():
            if getattr(other, _property) != value:
                return False
        return True

def _validate_value(parameter, value):
    ## TODO: Add more checks to detect invalid values when you know MaxMind's
    ## conditions for user ids.
    if _text_has_spaces(value) or value == "":
        raise ParameterNotValid(value, parameter,
                                " ". join([parameter, "cannot have spaces."]))


def _validate_url(parameter, url):
    """
    Check if a URL exists without downloading the whole file.
    We only check the URL header.

    :param parameter: Attribute that is being validated.
    :type parameter: str
    :param url: HTTP url to check its existence.
    :type url: str
    :return: True if url exists, else False.
    :rtype: bool
    :raise: ParameterNotValid
    """
    # see also http://stackoverflow.com/questions/2924422
    good_codes = [http.OK, http.FOUND, http.MOVED_PERMANENTLY]
    try:
        if _get_server_status_code(url) in good_codes:
            return  # Validation succeeded.
        else:
            raise Exception  # Let outer except raise one only exception.
    except:
        raise ParameterNotValid(parameter, url, "Cannot connect to given "
                                                "URL.")


def _get_server_status_code(url):
    """
    Download just the header of a URL and return the server's status code.

    :param url: HTTP url to check its existence.
    :type url: str
    :return: One of the connection status from http.client.
    :rtype: int
    :raise: Any of the exceptions from http.client built-in module.
    """
    # http://stackoverflow.com/questions/1140661
    host, path = urlparse.urlparse(url)[1:3]    # elems [1] and [2]
    conn = http.HTTPConnection(host)
    conn.request('HEAD', path)
    return conn.getresponse().status


def _validate_integer(parameter, value):
    """
    :param parameter: Attribute that is being validated.
    :type parameter: str
    :param value: Value integer o string.
    :type value: int or str
    :return: Value converted to an integer.
    :rtype: int
    """
    try:
        integer_value = int(value)
        if integer_value <= 0:
            raise ValueError
    except ValueError:
        raise ParameterNotValid(value, parameter, "Cannot convert to int.")
    return integer_value


def _text_has_spaces(text):
    """
    :param text:
    :type text: str
    :return: True if text has any space or false otherwise.
    :rtype: bool
    """
    words = text.split(" ")
    if len(words) > 1:
        return True
    else:
        return False


def load_configuration():
    """ Read configuration file and populate with its data a
    config.Configuration instance.

    :return: Configuration instance populated with configuration file data.
    :rtype: config.Configuration
    """
    try:
        configuration = _read_config_file()
    except ConfigNotFound:
        _create_default_config_file()
        configuration = load_configuration()
    return configuration


def _read_config_file():
    """ Load all configuration parameters set in config file.

    :return: Configuration instance populated with configuration file data.
    :rtype: config.Configuration
    :raise: config.ConfigNotFound
    """
    ## TODO: Implement config file existence check and ConfigNotFound exception
    ## raising if not found.
    with open(CONFIG_FILE_NAME, "rb") as config_file:
        configuration = pickle.load(config_file)
    return configuration


def _create_default_config_file():
    """ Create a default configuration file.

    :return: None
    """
    default_configuration = Configuration()
    with open(CONFIG_FILE_NAME, "wb") as config_file:
        pickle.dump(default_configuration, config_file, pickle.HIGHEST_PROTOCOL)


class ConfigNotFound(Exception):
    """ Launched when config file is not where is supposed to be."""
    def __init__(self):
        message = "Configuration file is not at it's default " \
                  "location: {0}".format(CONFIG_FILE)
        Exception.__init__(self, message)


class ParameterNotValid(Exception):
    """ Launched when user_id validation fails."""
    def __init__(self, provided_value, parameter, message):
        self.provided_value = provided_value
        self.parameter = parameter
        parameter_message = "There is a problem with parameter {0}, you " \
                            "gave {1} as value.\n " \
                            "Problem is: \n".format(parameter, provided_value)
        final_message = "".join([parameter_message, message])
        Exception.__init__(self, final_message)










