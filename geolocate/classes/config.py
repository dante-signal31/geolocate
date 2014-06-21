"""
 Configuration parser module.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import configparser

CONFIG_FILE = "etc/geolocate.conf"
DEFAULT_USER_ID = ""
DEFAULT_LICENSE_KEY = ""
DEFAULT_DATABASE_DOWNLOAD_URL = "http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz"
# GeoLite2 databases are updated on the first Tuesday of each month, so 35 days
# of update interval should be fine.
DEFAULT_UPDATE_INTERVAL = 35


class Configuration(object):
    """ Class to encapsulate configuration needed to connect to Geolite2
    webservices or downloaded local database. This class also validates
    parameters read from config files to overcome user typos.
    """
    def __init__(self, user_id = DEFAULT_USER_ID,
                       license_key = DEFAULT_LICENSE_KEY,
                       download_url = DEFAULT_DATABASE_DOWNLOAD_URL,
                       update_interval = DEFAULT_UPDATE_INTERVAL):
        self._webservice = {"user_id": "",
                            "license_key": ""}
        self._local_database = {"download_url": "",
                                "update_interval": ""}
        self.user_id = user_id
        self.license_key = license_key
        self.download_url = download_url
        self.update_interval = update_interval

    @property
    def user_id(self):
        return self._webservice["user_id"]

    @user_id.setter
    def user_id(self, user_id):
        _validate_value("user_id", user_id)
        self._webservice["user_id"] = user_id

    @property
    def license_key(self):
        return self.license_key_

    @license_key.setter
    def license_key(self, license_key):
        _validate_value("license_key", license_key)
        self._webservice["license_key"] = license_key

    @property
    def download_url(self):
        return self._local_database["download_url"]

    @download_url.setter
    def download_url(self, url):
        _validate_url(url)
        self._local_database["download_url"] = url

    @property
    def update_interval(self):
        return self._local_database["update_interval"]

    @update_interval.setter
    def update_interval(self, update_interval_in_days):
        _validate_integer(update_interval_in_days)
        self._local_database["update_interval"] = update_interval_in_days


def _validate_value(parameter, value):
    ## TODO: Add more checks to detect invalid values.
    if value == "":
        return
    elif _text_has_spaces(value):
            raise ParameterNotValid(value, parameter,
                                    " ". join([parameter, "cannot have spaces."]))


def _validate_url(url):
    pass


def _validate_integer(value):
    pass


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
        _create_config_file()
        configuration = load_configuration()
    return configuration


def _read_config_file():
    """ Load all configuration parameters set in config file.

    :return: Configuration instance populated with configuration file data.
    :rtype: config.Configuration
    :raise: config.ConfigNotFound
    """
    pass


def _create_config_file():
    """ Create a default configuration file.

    :return: None
    """
    pass


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










