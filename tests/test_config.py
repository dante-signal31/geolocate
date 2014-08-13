"""
 test_config.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import os
import sys
import tempfile
import unittest
import unittest.mock
sys.path.append(os.path.abspath(".."))
import geolocate.classes.config as config

GEOLOCATE_CONFIG_FILE = os.path.abspath(config.CONFIG_FILE)

class TestConfiguration(unittest.TestCase):

    def test_user_id_validation(self):
        wrong_user_id = "john doe" # Spaces don't use to be allowed.
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
        os.chdir("./geolocate")
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
        with tempfile.TemporaryDirectory() as temporary_folder:
            os.chdir(temporary_folder)
            config_relative_path = config._get_folder_path(relative_path)
            expected_path = "{0}/{1}".format(temporary_folder, relative_path)
            self.assertEqual(config_relative_path, expected_path)

    def _test_wrong_parameter(self, parameter, value):
        configuration = config.Configuration()
        with self.assertRaises(config.ParameterNotValid) as e:
            setattr(configuration, parameter, value)

    def _test_correct_parameter(self, parameter, value):
        configuration = config.Configuration()
        try:
            setattr(configuration, parameter, value)
        except config.ParameterNotValid:
            self.fail("ParameterNotValid exception with supposedly correct "
                      "parameter")

    def test_load_configuration_create_default_config_file(self):
        with _OriginalConfigSaved():
            _remove_config()
            config._create_default_config_file()
            configuration = config.load_configuration()
            default_configuration = config.Configuration()
            self.assertEqual(configuration, default_configuration,
                             msg="Read configuration is not a default "
                                 "configuration.")

    def test_load_configuration_config_not_found(self):
        with _OriginalConfigSaved():
            _remove_config()
            default_configuration = config.Configuration()
            configuration_loaded = config.load_configuration()
            self.assertEqual(default_configuration, configuration_loaded,
                             msg="Default configuration not regenerated.")

    def test_read_config_file_config_not_found(self):
        with _OriginalConfigSaved():
            _remove_config()
            with self.assertRaises(config.ConfigNotFound,
                                   msg="Config removed but _read_config() "
                                       "didn't raise ConfigNotFound "
                                       "exception."):
                config._read_config_file()

    def test_save_configuration(self):
        with _OriginalConfigSaved():
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


class _OriginalConfigSaved(object):
    """Context manager to store original configuration in a safe place for
    tests and restore it after them.
    """
    def __init__(self, config_file_name=GEOLOCATE_CONFIG_FILE):
        self._config_file_name = config_file_name
        self._backup_config_file = tempfile.TemporaryFile("r+b")

    def __enter__(self):
        self._backup_config()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._restore_config()
        if exc_type is None:
            return True
        else:
            return False

    def _backup_config(self):
        original_config_file_content = self._get_original_config()
        self._backup_config_file.write(original_config_file_content)

    def _get_original_config(self):
        config_file = open(self._config_file_name, "rb")
        original_config_file_content = config_file.read()
        # I don't keep config_file open because some tests remove that file
        # and I know better than to keep a reference to a removed file.
        config_file.close()
        return original_config_file_content

    def _restore_config(self):
        saved_config_file_content = self._get_backup_config()
        self._write_config(saved_config_file_content)

    def _get_backup_config(self):
        self._backup_config_file.seek(0)
        saved_config_file_content = self._backup_config_file.read()
        self._backup_config_file.close()
        return saved_config_file_content

    def _write_config(self, content):
        config_file = open(self._config_file_name, "wb")
        config_file.write(content)
        config_file.close()

def _remove_config():
    os.remove(GEOLOCATE_CONFIG_FILE)
