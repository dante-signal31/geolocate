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

    def test_get_properties(self):
        configuration = config.Configuration()
        self.assertEqual(configuration.user_id, config.DEFAULT_USER_ID)
        self.assertEqual(configuration.license_key,
                         config.DEFAULT_LICENSE_KEY)
        self.assertEqual(configuration.download_url,
                         config.DEFAULT_DATABASE_DOWNLOAD_URL)
        self.assertEqual(configuration.update_interval,
                         config.DEFAULT_UPDATE_INTERVAL)

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

    def test_load_configuration_ConfigNotFound(self):
        with _OriginalConfigSaved:
            _remove_original_config()
            configuration = config.load_configuration()
            default_configuration = config.Configuration()
            self.assertEqual(configuration, default_configuration,
                             msg="Read configuration is not a default "
                                 "configuration.")


class _OriginalConfigSaved(object):
    """Context manager to store original configuration in a safe place for
    tests and restore it after them.
    """
    def __init__(self, config_file_name=config.CONFIG_FILE):
        self._config_file = open(config_file_name)
        self._backup_config_file = tempfile.TemporaryFile()

    def __enter__(self):
        _backup_config()

    def __exit__(self, exc_type, exc_val, exc_tb):
        _restore_config()
        self._config_file.close()
        self._backup_config_file.close()

    def _backup_config(self):
        self._config_file.seek(0)
        original_config_file_content = self._config_file.read()
        self._backup_config_file.write(original_config_file_content)

    def _restore_config(self):
        self._config_file.seek(0)
        self._backup_config_file.seek(0)
        saved_config_file_content = self._backup_config_file.read()
        self._config_file.write(saved_config_file_content)



