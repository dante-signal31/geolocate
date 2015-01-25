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
import datetime
import geoip2.database as database
import geoip2.webservice as webservice
import subprocess

import geolocate.classes.config as config
import geolocate.classes.geowrapper as geoip

TEST_IP = "128.101.101.101"
TEST_IP_CITY = "Minneapolis"
WORKING_DIR = "./"

class TestGeoWrapper(unittest.TestCase):

    def test_geoip_database_add_locators_default_configuration(self):
        geoip_database = _create_default_geoip_database()
        locators_length = len(geoip_database._locators)
        # With default configuration only local database locator should be
        # activated.
        self.assertEqual(locators_length, 1,
                         msg="Locator list have not the expected length.")
        self.assertIsInstance(geoip_database.geoip2_local,
                              geoip.LocalDatabaseGeoLocator)

    def test_geoip_database_locate(self):
        new_locator_list = ["geoip2_local", "geoip2_webservice"]
        geoip_database = _create_default_geoip_database()
        geoip_database.locators_preference = new_locator_list
        geodata = geoip_database.locate(TEST_IP)
        self.assertEqual(geodata.city.name, TEST_IP_CITY)
        new_locator_list = ["geoip2_webservice", "geoip2_local"]
        geoip_database.locators_preference = new_locator_list
        geodata = geoip_database.locate(TEST_IP)
        self.assertEqual(geodata.city.name, TEST_IP_CITY)

    def test_local_database_geo_locator_creation(self):
        geoip_database = _create_default_geoip_database()
        connection = geoip_database.geoip2_local._db_connection
        self.assertIsInstance(connection,
                              database.Reader)

    def test_local_database_update(self):
        configuration = config.Configuration()
        with OriginalFileSaved(configuration.local_database_path):
            local_database = _create_too_old_database_locator(configuration)
            local_database._update_db()
            self.assertFalse(local_database._local_database_too_old(),
                             msg="Database not updated.")

    def test_local_database_too_old(self):
        configuration = config.Configuration()
        database_path = configuration.local_database_path
        with OriginalFileSaved(database_path):
            _make_database_file_too_old(configuration)
            too_old_date = geoip._get_database_last_modification(database_path)
            # LocalDatabaseGeolocator __init__ refreshes database.
            _ = geoip.LocalDatabaseGeoLocator(configuration)
            new_date = geoip._get_database_last_modification(database_path)
            delta = (new_date - too_old_date).days
            # If database has been updated, its new date should be newer than
            # old one (delta>0).
            self.assertGreater(delta, 0, msg="Old database not detected.")

    def test_local_database_locate(self):
        geoip_database = _create_default_geoip_database()
        geodata = geoip_database.geoip2_local.locate(TEST_IP)
        self.assertEqual(geodata.city.name, TEST_IP_CITY)

    def test_geoip_database_add_locators_non_default_configuration(self):
        geoip_database = _create_non_default_geoip_database()
        locators_length = len(geoip_database._locators)
        # With non default configuration webservice and local database locators
        # should be activated.
        self.assertEqual(locators_length, 2,
                         msg="Locator list have not the expected length.")
        self.assertIsInstance(geoip_database.geoip2_webservice,
                              geoip.WebServiceGeoLocator)
        self.assertIsInstance(geoip_database.geoip2_local,
                              geoip.LocalDatabaseGeoLocator)

    def test_web_service_geo_locator_creation(self):
        geoip_database = _create_non_default_geoip_database()
        connection = geoip_database.geoip2_webservice._db_connection
        self.assertIsInstance(connection,
                              webservice.Client)

    def test_web_service_geo_locator_failed_creation(self):
        geoip_database = _create_default_geoip_database()
        with self.assertRaises(geoip.GeoIP2WebServiceNotConfigured):
            _ = geoip_database.geoip2_webservice

    def test_local_database_geo_locator_download_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            configuration = config.Configuration()
            self._assert_folder_empty(temporary_directory)
            geoip_local_database = geoip.LocalDatabaseGeoLocator(configuration)
            geoip_local_database._download_file(temporary_directory)
            self._assert_folder_not_empty(temporary_directory)

    def test_local_database_not_found(self):
        configuration = config.Configuration()
        db_path = configuration.local_database_path
        with OriginalFileSaved(db_path):
            geolocator = geoip.LocalDatabaseGeoLocator(configuration)
            _remove_file(db_path)
            with self.assertRaises(geoip.LocalDatabaseNotFound):
                geolocator._db_connection = geoip._open_local_database(db_path)

    def test_local_database_get_modification_time_failed(self):
        configuration = config.Configuration()
        db_path = configuration.local_database_path
        with OriginalFileSaved(db_path):
            _ = geoip.LocalDatabaseGeoLocator(configuration)
            _remove_file(db_path)
            with self.assertRaises(geoip.LocalDatabaseNotFound):
                geoip._get_database_last_modification(db_path)

    def test_local_database_invalid(self):
        configuration = config.Configuration()
        database_path = configuration.local_database_path
        with OriginalFileSaved(database_path):
            os.remove(database_path)
            _create_invalid_file(database_path)
            with self.assertRaises(geoip.InvalidLocalDatabase):
                _ = geoip.LocalDatabaseGeoLocator(configuration)

    def test_get_new_database_path_name_find_file(self):
        configuration = config.Configuration()
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaises(geoip.NotValidDatabaseFileFound):
                _ = geoip._get_new_database_path_name(temporary_directory)
            _create_dummy_database_file(configuration, temporary_directory)
            database_name_path = _get_database_name_path(configuration,
                                                         temporary_directory)
            returned_database_name_path = geoip._get_new_database_path_name(temporary_directory)
            self.assertEqual(database_name_path, returned_database_name_path)

    def test_decompress_file(self):
        configuration = config.Configuration()
        with tempfile.TemporaryDirectory() as temporary_directory:
            _create_dummy_database_compressed(configuration,
                                              temporary_directory)
            geoip._decompress_file(temporary_directory)
            decompressed_file_path = _get_database_name_path(configuration,
                                                             temporary_directory)
            self.assertTrue(os.path.exists(decompressed_file_path))

    # I've didn't get this to pass although debug shows mocked function is
    # actually executed. I guess I'm not dealing right with mock library.
    # Nevertheless I leave the test here, someone may fix it.
    #
    # def test_decompress_file_failed(self):
    #     with tempfile.TemporaryDirectory() as temporary_directory:
    #         mocked_function = create_autospec(geoip._print_compressed_file_not_found_error)
    #         geoip._decompress_file(temporary_directory)
    #         self.assertTrue(mocked_function.called)

    def test_find_compressed_file(self):
        configuration = config.Configuration()
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaises(geoip.CompressedFileNotFound) as e:
                geoip._find_compressed_file(temporary_directory)
            _create_dummy_database_compressed(configuration,
                                              temporary_directory)
            dummy_path_name = _get_dummy_database_path_name(configuration,
                                                            temporary_directory)
            file_name_path = geoip._find_compressed_file(temporary_directory)
            self.assertTrue(file_name_path, dummy_path_name)

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


def _create_too_old_database_locator(configuration):
    _make_database_file_too_old(configuration)
    local_database = geoip.LocalDatabaseGeoLocator(configuration)
    return local_database


def _make_database_file_too_old(configuration):
    too_many_days = configuration.update_interval + 3
    too_old_date = datetime.date.today() - datetime.timedelta(days=too_many_days)
    _set_file_timestamp(configuration.local_database_path, too_old_date)


def _set_file_timestamp(file_path, too_old_date):
    date_string_format = "%y%m%d"
    too_old_date_string = too_old_date.strftime(date_string_format)
    touch_time_parameter = "".join([too_old_date_string, "0000"])
    subprocess.call(["touch", "-t", touch_time_parameter, file_path])


def _copy_database_file(configuration, destination_folder):
    destination_path = os.path.join(destination_folder,
                                    configuration.local_database_name)
    shutil.copyfile(configuration.local_database_path, destination_path)


def _get_database_name_path(configuration, temporary_directory):
    name_path = os.path.join(temporary_directory,
                             configuration.local_database_name)
    return name_path


def _create_dummy_database_file(configuration, temporary_directory):
    dummy_database_path_name = os.path.join(temporary_directory,
                                            configuration.local_database_name)
    subprocess.call(["touch", dummy_database_path_name])


def _create_dummy_database_compressed(configuration, temporary_directory):
    dummy_database_path_name = os.path.join(temporary_directory,
                                            configuration.local_database_name)
    subprocess.call(["touch", dummy_database_path_name])
    subprocess.call(["gzip", dummy_database_path_name])


def _get_dummy_database_path_name(configuration, temporary_directory):
    uncompressed_name_path = os.path.join(temporary_directory,
                                          configuration.local_database_name)
    compressed_name_path = ".".join([uncompressed_name_path, "gz"])
    return compressed_name_path


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


def _remove_file(file_path):
    """
    :param file_path: Path to file to be removed.
    :type file_path: str
    :return: none
    """
    os.remove(file_path)

if __name__ == '__main__':
    unittest.main()
