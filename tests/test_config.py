"""
 test_config.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import os
import sys
import unittest
import unittest.mock
sys.path.append(os.path.abspath(".."))
import geolocate.classes.config as config

class TestConfiguration(unittest.TestCase):

    def test_user_id_validation(self):
        wrong_user_id = "john doe" # Spaces don't use to be allowed.
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
        correct_url = "www.google.com"
        self._test_correct_parameter("download_url", correct_url)

    def _test_wrong_parameter(self, parameter, value):
        arguments_to_pass = {parameter: value, }
        with self.assertRaises(config.ParameterNotValid) as e:
            configuration = config.Configuration(**arguments_to_pass)

    def _test_correct_parameter(self, parameter, value):
        arguments_to_pass = {parameter: value, }
        try:
            configuration = config.Configuration(**arguments_to_pass)
        except config.ParameterNotValid:
            self.fail("ParameterNotValid exception with supposedly correct "
                      "parameter")
