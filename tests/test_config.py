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
        with self.assertRaises(config.ParameterNotValid) as e:
            configuration = config.Configuration(user_id=wrong_user_id)
        correct_user_id = "john_doe"
        try:
            configuration = config.Configuration(user_id=correct_user_id)
        except config.ParameterNotValid:
            self.fail("ParameterNotValid exception with supposedly correct "
                      "parameter")

    def test_license_key_validation(self):
        wrong_license_key = "1234 56ab"
        with self.assertRaises(config.ParameterNotValid) as e:
            configuration = config.Configuration(license_key=wrong_license_key)
        correct_license_id = "123456ab"
        try:
            configuration = config.Configuration(license_key=correct_license_id)
        except config.ParameterNotValid:
            self.fail("ParameterNotValid exception with supposedly correct "
                      "parameter")

    def test_download_url_validation(self):
        wrong_url = "www-google.com"
        with self.assertRaises(config.ParameterNotValid) as e:
            configuration = config.Configuration(download_url=wrong_url)
