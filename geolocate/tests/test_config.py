"""
 test_config.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import keyring
import os
import tempfile
import unittest
import unittest.mock

import geolocate.classes.config as config
import geolocate.tests.testing_tools as testing_tools


WORKING_DIR = "./geolocate/"
GEOLOCATE_CONFIG_FILE = config.CONFIG_FILE_PATH
TEST_CREDENTIALS = {"username": "john_doe",
                    "password": "superpassword1"}


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
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR):
            wrong_path = "database"
            self._test_wrong_parameter("local_database_folder", wrong_path)
            correct_path = "local_database"
            self._test_correct_parameter("local_database_folder", correct_path)

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
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            _remove_config()
            config._create_default_config_file()
            configuration = config.load_configuration()
            default_configuration = config.Configuration()
            self.assertEqual(configuration, default_configuration,
                             msg="Read configuration is not a default "
                                 "configuration.")

    def test_load_configuration_config_not_found(self):
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            _remove_config()
            default_configuration = config.Configuration()
            configuration_loaded = config.load_configuration()
            self.assertEqual(default_configuration, configuration_loaded,
                             msg="Default configuration not regenerated.")

    def test_read_config_file_config_not_found(self):
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            _remove_config()
            with self.assertRaises(config.ConfigNotFound,
                                   msg="Config removed but _read_config() "
                                       "didn't raise ConfigNotFound "
                                       "exception."):
                config._read_config_file()

    def test_save_configuration(self):
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR),\
                testing_tools.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            _remove_config()
            configuration_to_save = config.Configuration(user_id=TEST_CREDENTIALS["username"],
                                                         license_key=TEST_CREDENTIALS["password"])
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
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(GEOLOCATE_CONFIG_FILE):
            config._create_default_config_file()
            with config.OpenConfigurationToUpdate() as f:
                new_configuration = correct_configuration
                f.configuration = new_configuration
            saved_configuration = config.load_configuration()
            self.assertEqual(saved_configuration, correct_configuration)

    def test_save_and_load_password(self):
        username = TEST_CREDENTIALS["username"]
        password = TEST_CREDENTIALS["password"]
        config._save_password(username, password)
        recovered_password = config._load_password(username)
        keyring.delete_password(config.GEOLOCATE_VAULT, username)
        self.assertEqual(password, recovered_password)

    def test_delete_password(self):
        username = TEST_CREDENTIALS["username"]
        password = TEST_CREDENTIALS["password"]
        keyring.set_password(config.GEOLOCATE_VAULT, username, password)
        config._delete_password(username)
        recovered_password = keyring.get_password(config.GEOLOCATE_VAULT,
                                                  username)
        self.assertIs(recovered_password, None)


def _remove_config():
    if os.path.isfile(GEOLOCATE_CONFIG_FILE):
        os.remove(GEOLOCATE_CONFIG_FILE)
