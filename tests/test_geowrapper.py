"""
 test_geowrapper.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import ntpath
import os
import shutil
import tempfile
import unittest
import geoip2.database as database
import geoip2.webservice as webservice

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
                              database.Reader)

    def test_local_database_update(self):
        self.assertTrue(False)

    def test_local_database_too_old(self):
        self.assertTrue(False)

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
                              webservice.Client)

    def test_local_database_geo_locator_download_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            configuration = config.Configuration()
            self._assert_folder_empty(temporary_directory)
            geoip_local_database = geoip.LocalDatabaseGeoLocator(configuration)
            geoip_local_database._download_file(temporary_directory)
            self._assert_folder_not_empty(temporary_directory)

    def test_local_database_not_found(self):
        configuration = config.Configuration()
        database_path = configuration.local_database_path
        with OriginalFileSaved(database_path):
            os.remove(database_path)
            with self.assertRaises(geoip.LocalDatabaseNotFound):
                _ = geoip.LocalDatabaseGeoLocator(configuration)

    def test_local_database_invalid(self):
        configuration = config.Configuration()
        database_path = configuration.local_database_path
        with OriginalFileSaved(database_path):
            os.remove(database_path)
            _create_invalid_file(database_path)
            with self.assertRaises(geoip.InvalidLocalDatabase):
                _ = geoip.LocalDatabaseGeoLocator(configuration)

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


class OriginalFileSaved(object):
    """Context manager to store original files in a safe place for
    tests and restore it after them.
    """

    def __init__(self, original_file_path):
        """
        :param original_file_path: File name including path.
        :type original_file_path: str
        """
        self._original_file_path = original_file_path
        self._original_file_name = _get_file_name(original_file_path)
        self._backup_directory = _create_temporary_directory()
        self._backup_file_path = os.path.join(self._backup_directory.name,
                                              self._original_file_name)

    def __enter__(self):
        self._backup_file()
        return self

    def _backup_file(self):
        shutil.copyfile(self._original_file_path, self._backup_file_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._restore_file()
        self._remove_backup_directory()
        if exc_type is None:
            return True
        else:
            return False

    def _restore_file(self):
        shutil.copyfile(self._backup_file_path, self._original_file_path)

    def _remove_backup_directory(self):
        self._backup_directory.cleanup()


def _get_file_name(file_path):
    """
    :param file_path: File name including path.
    :type file_path: str
    :return: File name.
    :rtype: str
    """
    file_name = ntpath.basename(file_path)
    return file_name


def _create_temporary_directory():
    """
    :return: Temporary directory just created.
    :rtype: TemporaryDirectory.
    """
    temporary_directory = tempfile.TemporaryDirectory()
    return temporary_directory


def _create_invalid_file(file_path):
    with open(file_path, "w") as file:
        file.write("invalid_content")


if __name__ == '__main__':
    unittest.main()
