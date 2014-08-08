"""
 test_geowrapper.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import os
import tempfile
import sys
import unittest
import geoip2.database
import geoip2.webservice
sys.path.append(os.path.abspath(".."))
import geolocate.classes.config as config
import geolocate.classes.geowrapper as geoip


class TestGeoWrapper(unittest.TestCase):

    def test_geoip_database_add_locators_default_configuration(self):
        geoip_database = _create_default_geoip_database()
        locators_length = len(geoip_database._locators)
        # With default configuration only local database locator should be
        # activated.
        self.assertEqual(locators_length, 1,
                         msg="Locator list have not the expected length.")
        self.assertIsInstance(geoip_database._locators[0],
                              geoip.LocalDatabaseGeoLocator)

    def test_local_database_geo_locator_creation(self):
        geoip_database = _create_default_geoip_database()
        connection = geoip_database._locators[0]._db_connection
        self.assertIsInstance(connection,
                              geoip2.database.Reader)

    def test_geoip_database_add_locators_non_default_configuration(self):
        geoip_database = _create_non_default_geoip_database()
        locators_length = len(geoip_database._locators)
        # With non default configuration webservice and local database locators
        # should be activated.
        self.assertEqual(locators_length, 2,
                         msg="Locator list have not the expected length.")
        self.assertIsInstance(geoip_database._locators[0],
                              geoip.WebServiceGeoLocator)
        self.assertIsInstance(geoip_database._locators[1],
                              geoip.LocalDatabaseGeoLocator)

    def test_web_service_geo_locator_creation(self):
        geoip_database = _create_non_default_geoip_database()
        connection = geoip_database._locators[0]._db_connection
        self.assertIsInstance(connection,
                              geoip2.webservice.Client)

    def test_local_database_geo_locator_download_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            configuration = config.Configuration()
            self._assert_folder_empty(temporary_directory)
            geoip_local_database = geoip.LocalDatabaseGeoLocator(configuration)
            geoip_local_database._download_file(temporary_directory)
            self._assert_folder_not_empty(temporary_directory)

    def _assert_folder_empty(self, folder_path):
        files_list = os.listdir(folder_path)
        self.assertEqual([], files_list,
                           msg="Temporary folder initially not empty.")

    def _assert_folder_not_empty(self, folder_path):
        files_list = os.listdir(folder_path)
        self.assertNotEqual([], files_list,
                           msg="Nothing downloaded.")


def _create_default_geoip_database():
    configuration = config.Configuration()
    geoip_database = geoip.load_geoip_database(configuration)
    return geoip_database

def _create_non_default_geoip_database():
    configuration = config.Configuration(user_id="user2014",
                                         license_key="XXXXX")
    geoip_database = geoip.load_geoip_database(configuration)
    return geoip_database





if __name__ == '__main__':
    unittest.main()
