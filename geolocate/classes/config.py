"""
 Configuration parser module.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import configparser
import http.client as http
import os
import urllib.parse as urlparse

import keyring


CONFIG_ROOT = os.path.expanduser("~/.geolocate")
CONFIG_FILE = "etc/geolocate.conf"
CONFIG_FILE_PATH = os.path.join(CONFIG_ROOT, CONFIG_FILE)
GEOLOCATE_VAULT = "geolocate"
DEFAULT_USER_ID = ""
DEFAULT_LICENSE_KEY = ""
# TODO: For production I have to uncomment real url.
# Only for tests I have to comment real download url. MaxMind has a rate limit
# per day. If you exceed that limit you are forbidden for 24 hours to download
# their database.
DEFAULT_DATABASE_DOWNLOAD_URL = "http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz"
# TODO: For production remove next fake url, it's only for tests.
#DEFAULT_DATABASE_DOWNLOAD_URL = "http://localhost:2014/GeoLite2-City.mmdb.gz"
# GeoLite2 databases are updated on the first Tuesday of each month, so 35 days
# of update interval should be fine.
DEFAULT_UPDATE_INTERVAL = 35
DEFAULT_LOCAL_DATABASE_FOLDER = os.path.join(CONFIG_ROOT, "local_database/")
DEFAULT_LOCAL_DATABASE_NAME = "GeoLite2-City.mmdb"
# Remember add new locators here or locate won't use them.
DEFAULT_LOCATORS_PREFERENCE = ["geoip2_webservice", "geoip2_local"]


class Configuration(object):
    # I've discovered Maxmind website blocks clients who exceeds a connection
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
                 update_interval=DEFAULT_UPDATE_INTERVAL,
                 local_database_folder=DEFAULT_LOCAL_DATABASE_FOLDER,
                 local_database_name=DEFAULT_LOCAL_DATABASE_NAME,
                 locators_preference=DEFAULT_LOCATORS_PREFERENCE):
        self._webservice = {"user_id": user_id,
                            "license_key": license_key}
        self._local_database = {"download_url": download_url,
                                "update_interval": update_interval,
                                "local_database_folder": local_database_folder,
                                "local_database_name": local_database_name}
        self._locators_preference = locators_preference

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

    @property
    def local_database_folder(self):
        return self._local_database["local_database_folder"]

    @local_database_folder.setter
    def local_database_folder(self, folder_path):
        database_folder_path = _get_folder_path(folder_path)
        _validate_folder("local_database_folder", database_folder_path)
        self._local_database["local_database_folder"] = database_folder_path

    @property
    def local_database_name(self):
        return self._local_database["local_database_name"]

    @local_database_name.setter
    def local_database_name(self, database_name):
        # At first sight every database name should be OK, but I'll leave this
        # as a property in case I have an idea about a possible check.
        self._local_database["local_database_name"] = database_name

    @property
    def local_database_path(self):
        path = os.path.join(self.local_database_folder,
                            self.local_database_name)
        return path

    @property
    def locators_preference(self):
        """
        :return: Enabled locators for this GeoIPDatabase ordered by preference.
        :rtype: list
        """
        return self._locators_preference

    @locators_preference.setter
    def locators_preference(self, new_locator_list):
        if _unknown_locators(new_locator_list):
            unknown_locators = _get_unknown_locators(new_locator_list)
            raise UnknownLocators(unknown_locators)
        else:
            self._locators_preference = new_locator_list

    # I make comparisons at tests so I need this functionality.
    # Great reference about custom classes equality at:
    #   https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.__dict__ == self.__dict__
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        else:
            return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def reset_locators_preference(self):
        """ Reset locators preference to default order.

        :return: None
        """
        self._locators_preference = DEFAULT_LOCATORS_PREFERENCE

    @property
    def disabled_locators(self):
        """ Locators registered as default one but not enabled in this
        GeoIPDatabase.

        :return: Disabled locators in this GeoIPDatabase.
        :rtype: set
        """
        default_locators_set = set(DEFAULT_LOCATORS_PREFERENCE)
        enabled_locators_set = set(self.locators_preference)
        disabled_locators_set = default_locators_set - enabled_locators_set
        return disabled_locators_set

    def get_configuration_dict(self):
        """ Get a dict with configuration parameters.

        Dict keys will be sections and values are also dict with values for
        that section. License key won't we included and must be got from
        license_key property

        :return: Configuration sections dict of dicts.
        :rtype: dict
        """
        parsed_configuration = {
            "webservice": {"user_id": self._webservice["user_id"]},
            "local_database": {key: self._local_database[key]
                               for key in self._local_database.keys()},
            "locators_preference": {
                "preference": ",".join(self._locators_preference)
            }
        }
        return parsed_configuration

def _validate_value(parameter, value):
    # TODO: Add more checks to detect invalid values when you know MaxMind's
    # conditions for user ids.
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
    :return: None
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
        raise ParameterNotValid(url, parameter, "Cannot connect to given "
                                                "URL.")


def _validate_folder(parameter, path):
    """
    :param parameter: Attribute that is being validated.
    :type parameter: str
    :param path: Path to folder being checked.
    :type path: str
    :return: None
    :raise: ParameterNotValid
    """
    if not os.path.exists(path):
        raise ParameterNotValid(path, parameter, "Folder does not exists.")


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
    status = conn.getresponse().status
    conn.close()
    return status


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
        configuration, license_key = _read_config_file()
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
    try:
        configuration_parser = configparser.ConfigParser()
        configuration_parser.read(CONFIG_FILE_PATH)
        license_key = _load_password(configuration_parser["webservice"]["user_id"])
        locators_preference = _string_to_list(configuration_parser["locators_preference"]["preference"])
        configuration = Configuration(
            user_id=configuration_parser["webservice"]["user_id"],
            license_key=license_key,
            download_url=configuration_parser["local_database"]["download_url"],
            update_interval=int(configuration_parser["local_database"]["update_interval"]),
            local_database_folder=configuration_parser["local_database"]["local_database_folder"],
            local_database_name=configuration_parser["local_database"]["local_database_name"],
            locators_preference=locators_preference
            )
        return configuration, license_key
    except (FileNotFoundError, KeyError):
        raise ConfigNotFound()
    except Exception as e:
        print("Something odd happened: ", e)


def _string_to_list(string_list):
    """ Take a string with comma separated elements a return a list of
    those elements.

    :param string_list: String with comma separated elements.
    :type string_list: str
    :return: List with elements.
    :rtype: list
    """
    string_list_no_spaces = string_list.replace(' ', '')
    element_list = list(string_list_no_spaces.split(','))
    return element_list


def _create_default_config_file():
    """ Create a default configuration file.

    :return: None
    """
    default_configuration = Configuration()
    save_configuration(default_configuration)


def save_configuration(configuration):
    """ Write Configuration object in config file.

    :param configuration: Configuration to be saved.
    :type configuration: config.Configuration
    :return: None
    """
    configuration_parameters = configuration.get_configuration_dict()
    _save_password(configuration.user_id, configuration.license_key)
    configuration_parsed = _parse_parameters(configuration_parameters)
    try:
        with open(CONFIG_FILE_PATH, "w") as config_file:
            configuration_parsed.write(config_file)
    except FileNotFoundError:  # Configuration path probably does not exist yet.
        path_to_create = os.path.dirname(CONFIG_FILE_PATH)
        os.makedirs(path_to_create)
        save_configuration(configuration)


def _parse_parameters(configuration_parameters):
    """ Insert parameter into a configparse file.

    :param configuration_parameters:
    :type configuration_parameters: dict
    :return: None
    """
    configuration_parsed = configparser.ConfigParser()
    for section in configuration_parameters.keys():
        configuration_parsed[section] = configuration_parameters[section]
    return configuration_parsed


def _save_password(username, password):
    """ Save password ciphered in system keyring.

    :param username: Username to be used with Maxmind webservice.
    :type username: str
    :param password: Password of Maxmind account.
    :type password: str
    :return: None
    """
    keyring.set_password(GEOLOCATE_VAULT, username, password)


def _load_password(username):
    """ Retrieve password from system keyring.

    :param username: Username used with Maxmind webservice.
    :type username: str
    :return: None
    """
    recovered_password = keyring.get_password(GEOLOCATE_VAULT, username)
    return recovered_password


def _delete_password(username):
    """ Delete password assigned to username and stored in system keyring.

    :param username: Username used with Maxmind webservice.
    :type username: str
    :return: None
    """
    keyring.delete_password(GEOLOCATE_VAULT, username)


def _get_folder_path(path):
    """ If path is relative, get absolute path of current working directory
    suffixed by path. If path is absolute, just return it.

    :param path: Path to get absolute form.
    :type path: str
    :return: Absolute path.
    :rtype: str
    """
    absolute_directory = None
    if path.startswith("/"):
        absolute_directory = path
    else:
        current_working_directory = os.getcwd()
        absolute_directory = "{0}/{1}".format(current_working_directory,
                                              path)
    return absolute_directory


def _unknown_locators(locator_list):
    """ Detects if any locator in provided list is not registered as a valid one.

    Enabled locators are registered in DEFAULT_LOCATORS_PREFERENCE constant.
    Locators have to be one of them to be declared valid.

    :param locator_list: String list with locator names.
    :type locator_list: list
    :return: True if any locator in list is not within default locator list, else False.
    :rtype: bool
    """
    locator_set = set(locator_list)
    default_locator_set = set(DEFAULT_LOCATORS_PREFERENCE)
    if locator_set <= default_locator_set:
        return False
    else:
        return True


def _get_unknown_locators(locator_list):
    """
    :param locator_list: String list with locator names.
    :type locator_list: list
    :return: Set with unknown locators detected.
    :rtype: set
    """
    locator_set = set(locator_list)
    default_locator_set = set(DEFAULT_LOCATORS_PREFERENCE)
    return locator_set - default_locator_set


class ConfigNotFound(Exception):
    """ Launched when config file is not where is supposed to be."""
    def __init__(self):
        message = "Configuration file is not at it's default " \
                  "location: {0}".format(CONFIG_FILE_PATH)
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


class UnknownLocators(Exception):
    """ Raised when an still not implemented location is referenced in any
    operation.
    """

    def __init__(self, unknown_locators):
        unknown_locators_text = " ".join(unknown_locators)
        self.message = " ".join(["You tried to use not implemented locators:",
                                 unknown_locators_text])
        Exception.__init__(self, self.message)


class OpenConfigurationToUpdate(object):
    """ Context manager to get a configuration file and save it automatically.
    """
    def __init__(self):
        self.configuration = load_configuration()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save_configuration(self.configuration)
        if exc_type is None:
            return True
        else:
            return False


