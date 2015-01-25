"""
 test_config.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import os
import tempfile
import unittest
import unittest.mock

import test_geowrapper
import geolocate.classes.config as config

GEOLOCATE_CONFIG_FILE = os.path.abspath(config.CONFIG_FILE)
WORKING_DIR = "./"


class TestConfiguration(unittest.TestCase):

    def test_user_id_validation(self):
        wrong_user_id = "john doe"  # Spaces don't use to be allowed.
        self._test_wrong_parameter("user_id", wrong_user_id)
        wrong_user_id = ""
        self._test_wrong_parameter("user_id", wrong_user_id)
        correct_user_id = "john_doe"
        self._test_correct_parameter("user_id", correct_user_id)

    def test_license_key_validation(self):
        wrong_license_key = "1234 56ab"
        self._test_wrong_parameter("license_key", wrong_license_key)
        correct_license_key = "123456ab"
        self._test_correct_parameter("license_key", correct_license_key)

    def test_download_url_validation(self):
        wrong_url = "www-google.com"
        self._test_wrong_parameter("download_url", wrong_url)
        wrong_url = "http://old-releases.ubuntu.com/releases/99.04.0/"
        self._test_wrong_parameter("download_url", wrong_url)
        correct_url = "http://www.google.com"
        self._test_correct_parameter("download_url", correct_url)

    def test_update_interval_validation(self):
        wrong_update_interval = -30
        self._test_wrong_parameter("update_interval", wrong_update_interval)
        correct_update_interval = 40
        self._test_correct_parameter("update_interval", correct_update_interval)

    def test_database_folder_validation(self):
        # Current working dir is at setup.py folder level, so we have to go
        # deeper into geolocate as we would be at production.
        with WorkingDirectoryChanged(WORKING_DIR):
            wrong_path = "database"
            self._test_wrong_parameter("local_database_folder", wrong_path)
            correct_path = "local_database"
            self._test_correct_parameter("local_database_folder", correct_path)

    def test_get_config_path(self):
        absolute_path = "/usr/local/"
        config_absolute_path = config._get_folder_path(absolute_path)
        expected_path = absolute_path
        self.assertEqual(config_absolute_path, expected_path)
        relative_path = "test/"
        with tempfile.TemporaryDirectory() as temporary_folder, \
                WorkingDirectoryChanged(temporary_folder):
            config_relative_path = config._get_folder_path(relative_path)
            expected_path = "{0}/{1}".format(temporary_folder, relative_path)
            self.assertEqual(config_relative_path, expected_path)

    def _test_wrong_parameter(self, parameter, value):
        configuration = config.Configuration()
        with self.assertRaises(config.ParameterNotValid):
            setattr(configuration, parameter, value)

    def _test_correct_parameter(self, parameter, value):
        configuration = config.Configuration()
        try:
            setattr(configuration, parameter, value)
        except config.ParameterNotValid:
            self.fail("ParameterNotValid exception with supposedly correct "
                      "parameter")

    def test_load_configuration_create_default_config_file(self):
        with test_geowrapper.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            _remove_config()
            config._create_default_config_file()
            configuration = config.load_configuration()
            default_configuration = config.Configuration()
            self.assertEqual(configuration, default_configuration,
                             msg="Read configuration is not a default "
                                 "configuration.")

    def test_load_configuration_config_not_found(self):
        with test_geowrapper.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            _remove_config()
            default_configuration = config.Configuration()
            configuration_loaded = config.load_configuration()
            self.assertEqual(default_configuration, configuration_loaded,
                             msg="Default configuration not regenerated.")

    def test_read_config_file_config_not_found(self):
        with test_geowrapper.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            _remove_config()
            with self.assertRaises(config.ConfigNotFound,
                                   msg="Config removed but _read_config() "
                                       "didn't raise ConfigNotFound "
                                       "exception."):
                config._read_config_file()

    def test_save_configuration(self):
        with test_geowrapper.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            _remove_config()
            configuration_to_save = config.Configuration(user_id="user1984")
            config.save_configuration(configuration_to_save)
            configuration_loaded = config.load_configuration()
            self.assertEqual(configuration_to_save, configuration_loaded,
                             msg="Configuration loaded is not the same as "
                                 "configuration saved.")

    def test_configuration_equality(self):
        configuration1 = config.Configuration(user_id="userXXX")
        configuration2 = config.Configuration(user_id="no_name")
        self.assertNotEqual(configuration1, configuration2)
        configuration2.user_id = configuration1.user_id
        self.assertEqual(configuration1, configuration2)

    def test_get_properties(self):
        configuration = config.Configuration()
        self.assertEqual(configuration.user_id, config.DEFAULT_USER_ID)
        self.assertEqual(configuration.license_key,
                         config.DEFAULT_LICENSE_KEY)
        self.assertEqual(configuration.download_url,
                         config.DEFAULT_DATABASE_DOWNLOAD_URL)
        self.assertEqual(configuration.update_interval,
                         config.DEFAULT_UPDATE_INTERVAL)

    def test_config_get_disabled_locators_preference(self):
        new_locator_list = ["geoip2_local", ]
        disabled_locator_list = ["geoip2_webservice"]
        configuration = config.Configuration()
        configuration.locators_preference = new_locator_list
        detected_disabled_locator_list = list(configuration.disabled_locators)
        self.assertEqual(disabled_locator_list, detected_disabled_locator_list)

    def test_config_reset_locators_preference(self):
        new_locator_list = ["geoip2_local", "geoip2_webservice"]
        configuration = config.Configuration()
        configuration.locators_preference = new_locator_list
        configuration.reset_locators_preference()
        reseted_locator_preference = list(configuration.locators_preference)
        self.assertEqual(config.DEFAULT_LOCATORS_PREFERENCE,
                         reseted_locator_preference)

    def test_config_set_locators_preference_error(self):
        bad_locator_list = ["dummy", "geoip2_webservice", "geoip2_local"]
        configuration = config.Configuration()
        with self.assertRaises(config.UnknownLocators):
            configuration.locators_preference = bad_locator_list

    def test_config_set_locators_preference(self):
        new_locator_list = ["geoip2_local", "geoip2_webservice"]
        configuration = config.Configuration()
        configuration.locators_preference = new_locator_list
        self.assertEqual(new_locator_list, configuration.locators_preference)

    def test_config_OpenConfigurationToUpdate(self):
        correct_configuration = config.Configuration(user_id="test",
                                                     license_key="key")
        with test_geowrapper.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            with config.OpenConfigurationToUpdate() as f:
                new_configuration = correct_configuration
                f.configuration = new_configuration
            saved_configuration = config.load_configuration()
            self.assertEqual(saved_configuration, correct_configuration)


def _remove_config():
    os.remove(GEOLOCATE_CONFIG_FILE)


class WorkingDirectoryChanged(object):
    """ Sometimes unit test executes at a different path level than usual
    execution code. This context manager restores normal working directory
    after context manager exit.
    """
    def __init__(self, new_working_dir):
        """
        :param new_working_dir: New working path.
        :return: str
        """
        self._old_working_dir = os.getcwd()
        self._new_working_dir = new_working_dir

    def __enter__(self):
        os.chdir(self._new_working_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._old_working_dir)
        if exc_type is None:
            return True
        else:
            return False