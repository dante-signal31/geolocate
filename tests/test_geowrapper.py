"""
 test_geowrapper.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import os
import sys
import unittest
sys.path.append(os.path.abspath(".."))
import geolocate.classes.config as config
import geolocate.classes.geowrapper as geoip


class MyTestCase(unittest.TestCase):

    def test_geoip_database_add_locators_default_configuration(self):
        configuration = config.Configuration()
        geoip_database = geoip.load_geoip_database(configuration)
        locators_length = len(geoip_database._locators)
        # With default configuration only local database locator should be
        # activated.
        self.assertEqual(locators_length, 1,
                         msg="Locator list have not the expected length.")
        self.assertIsInstance(geoip_database._locators[0],
                              geoip.LocalDatabaseGeoLocator)

    def test_geoip_database_add_locators_non_default_configuration(self):
        configuration = config.Configuration(user_id="user2014",
                                             license_key="XXXXX")
        geoip_database = geoip.load_geoip_database(configuration)
        locators_length = len(geoip_database._locators)
        # With non default configuration webservice and local database locators
        # should be activated.
        self.assertEqual(locators_length, 2,
                         msg="Locator list have not the expected length.")
        self.assertIsInstance(geoip_database._locators[0],
                              geoip.WebServiceGeoLocator)
        self.assertIsInstance(geoip_database._locators[1],
                              geoip.LocalDatabaseGeoLocator)


if __name__ == '__main__':
    unittest.main()
