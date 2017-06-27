"""
 test_geolocate.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

from collections import namedtuple
from unittest.mock import patch
import unittest

import geolocate.classes.arguments as args
import geolocate.classes.config as config
import geolocate.tests.console_mocks as console_mocks
import geolocate.tests.testing_tools as testing_tools


ERRONEOUS_ARGUMENT = "erroneous_argument"

Arguments = namedtuple("Arguments", "show_enabled_locators "
                                    "set_locators_preference "
                                    "show_disabled_locators "
                                    "reset_locators_preference "
                                    "set_user "
                                    "set_password")

ErroneousArguments = namedtuple("ErroneousArguments",
                                " ".join(["show_enabled_locators "
                                          "set_locators_preference "
                                          "show_disabled_locators "
                                          "reset_locators_preference ",
                                          ERRONEOUS_ARGUMENT]))

WORKING_DIR = "./geolocate/"
CONFIGURATION_PATH = config.CONFIG_FILE


class MockedArguments(object):
    """ Used to detect private attributes.

    I couldn't use namedtuple because it doesn't admit attributes prefixed
    by "_".
    """

    def __init__(self, arg1, arg2, arg3, arg4):
        self._priv1 = False
        self.__priv2 = False
        self.show_enabled_locators = arg1
        self.set_locators_preference = arg2
        self.show_disabled_locators = arg3
        self.reset_locators_preference = arg4


class TestGeoLocate(unittest.TestCase):

    def test_process_optional_parameters_show_enabled_locators(self):
        arguments = Arguments(True, None, False, False, None, None)
        result = _assert_geolocate_function_called("show_enabled_locators",
                                                   arguments)
        self.assertTrue(result)

    def test_process_optional_parameters_set_locators_preference(self):
        arguments = Arguments(False, ["geoip2_local", "geoip2_webservice"],
                              False, False, None, None)
        result = _assert_geolocate_function_called("set_locators_preference",
                                                   arguments)
        self.assertTrue(result)

    def test_process_optional_parameters_show_disabled_locators(self):
        arguments = Arguments(False, None, True, False, None, None)
        result = _assert_geolocate_function_called("show_disabled_locators",
                                                   arguments)
        self.assertTrue(result)

    def test_process_optional_parameters_reset_locators_preference(self):
        arguments = Arguments(False, None, False, True, None, None)
        result = _assert_geolocate_function_called("reset_locators_preference",
                                                   arguments)
        self.assertTrue(result)

    def tests_process_optional_parameters_erroneos_argument(self):
        arguments = ErroneousArguments(False, None, False, False, True)
        with self.assertRaises(args.NoFunctionAssignedToArgument) as e:
            args._execute_function(ERRONEOUS_ARGUMENT, arguments)
        self.assertEqual(e.exception.argument, ERRONEOUS_ARGUMENT)

    def test_get_user_attributes(self):
        correct_arguments_set = {"show_enabled_locators",
                                 "set_locators_preference",
                                 "show_disabled_locators",
                                 "reset_locators_preference"}
        test_arguments_object = MockedArguments(True, True, True, True)
        valid_arguments = args._get_user_arguments(test_arguments_object)
        self.assertEqual(valid_arguments, correct_arguments_set)

    def test_show_enabled_locators(self):
        correct_string = "Enabled locators:\n" \
                         "geoip2_webservice\n" \
                         "geoip2_local\n"
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(CONFIGURATION_PATH):
            args.reset_locators_preference()
            with console_mocks.MockedConsoleOutput() as console:
                args.show_enabled_locators()
                self._assertConsoleOutputEqual(correct_string, console)

    def test_show_disabled_locators(self):
        correct_string = "Disabled locators:\n" \
                         "geoip2_webservice\n"
        enabled_locators = ["geoip2_local", ]
        mocked_arguments = Arguments(False, enabled_locators, False, False,
                                     None, None)
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(CONFIGURATION_PATH):
            args.set_locators_preference(mocked_arguments)
            with console_mocks.MockedConsoleOutput() as console:
                args.show_disabled_locators()
                self._assertConsoleOutputEqual(correct_string, console)

    def test_set_locators_preference(self):
        correct_string = "Enabled locators:\n" \
                         "geoip2_local\n" \
                         "geoip2_webservice\n"
        new_locators_preference = ["geoip2_local", "geoip2_webservice"]
        mocked_arguments = Arguments(False, new_locators_preference, False,
                                     False, None, None)
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(CONFIGURATION_PATH):
            args.set_locators_preference(mocked_arguments)
            with console_mocks.MockedConsoleOutput() as console:
                args.show_enabled_locators()
                self._assertConsoleOutputEqual(correct_string, console)

    def test_reset_locators_preference(self):
        changed_string = "Enabled locators:\n" \
                         "geoip2_local\n" \
                         "geoip2_webservice\n"
        correct_string = "Enabled locators:\n" \
                         "geoip2_webservice\n" \
                         "geoip2_local\n"
        new_locators_preference = ["geoip2_local", "geoip2_webservice"]
        mocked_arguments = Arguments(False, new_locators_preference, False,
                                     False, None, None)
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(CONFIGURATION_PATH):
            args.set_locators_preference(mocked_arguments)
            with console_mocks.MockedConsoleOutput() as console:
                args.show_enabled_locators()
                returned_output = console.output()
                self.assertEqual(returned_output, changed_string)
                console.reset()
                args.reset_locators_preference()
                args.show_enabled_locators()
                self._assertConsoleOutputEqual(correct_string, console)

    def test_set_user(self):
        user = "user_2015"
        returned_string = "User:\n" \
                          "{0}\n".format(user)
        mocked_arguments = Arguments(False, None, False,
                                     False, user, None)
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(CONFIGURATION_PATH):
            args.set_user(mocked_arguments)
            with console_mocks.MockedConsoleOutput() as console:
                args.show_user()
                self._assertConsoleOutputEqual(returned_string, console)

    def test_set_password(self):
        password = "mocked_password"
        returned_string = "Password:\n" \
                          "{0}\n".format(password)
        mocked_arguments = Arguments(False, None, False, False, None,
                                     password)
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(CONFIGURATION_PATH):
            args.set_password(mocked_arguments)
            with console_mocks.MockedConsoleOutput() as console:
                args.show_password()
                self._assertConsoleOutputEqual(returned_string, console)

    def test_show_user(self):
        user = "user_2015"
        returned_string = "User:\n" \
                          "{0}\n".format(user)
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(CONFIGURATION_PATH):
            new_configuration = config.Configuration()
            new_configuration.user_id = user
            config.save_configuration(new_configuration)
            with console_mocks.MockedConsoleOutput() as console:
                args.show_user()
                self._assertConsoleOutputEqual(returned_string, console)

    def test_show_password(self):
        password = "mocked_password"
        returned_string = "Password:\n" \
                          "{0}\n".format(password)
        with testing_tools.WorkingDirectoryChanged(WORKING_DIR), \
                testing_tools.OriginalFileSaved(CONFIGURATION_PATH):
            new_configuration = config.Configuration()
            new_configuration.license_key = password
            config.save_configuration(new_configuration)
            with console_mocks.MockedConsoleOutput() as console:
                args.show_password()
                self._assertConsoleOutputEqual(returned_string, console)

    def _assertConsoleOutputEqual(self, string_to_match, console):
        returned_output = console.output()
        self.assertEqual(returned_output, string_to_match)


def _assert_geolocate_function_called(function_name, arguments):
    target_to_patch = ".".join(["geolocate.classes.arguments", function_name])
    with patch(target_to_patch) as mocked_function:
        args.process_optional_parameters(arguments)
    return mocked_function.called
