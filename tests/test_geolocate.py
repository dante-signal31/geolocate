"""
 test_geolocate.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

from collections import namedtuple
import io
import sys
import os.path
from unittest.mock import patch
import unittest

import geolocate.geolocate as geolocate
import geolocate.classes.config as config
import tests.test_geowrapper as test_geowrappers


ERRONEOUS_ARGUMENT = "erroneous_argument"

Arguments = namedtuple("Arguments", "show_enabled_locators "
                                    "set_locators_preference "
                                    "show_disabled_locators "
                                    "reset_locators_preference ")

ErroneousArguments = namedtuple("ErroneousArguments",
                                " ".join(["show_enabled_locators "
                                          "set_locators_preference "
                                          "show_disabled_locators "
                                          "reset_locators_preference ",
                                          ERRONEOUS_ARGUMENT]))

CONFIGURATION_PATH = os.path.abspath(config.CONFIG_FILE)

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
        arguments = Arguments(True, None, False, False)
        result = _assert_geolocate_function_called("show_enabled_locators",
                                                   arguments)
        self.assertTrue(result)

    def test_process_optional_parameters_set_locators_preference(self):
        arguments = Arguments(False, ["geoip2_local", "geoip2_webservice"],
                              False, False)
        result = _assert_geolocate_function_called("set_locators_preference",
                                                   arguments)
        self.assertTrue(result)

    def test_process_optional_parameters_show_disabled_locators(self):
        arguments = Arguments(False, None, True, False)
        result = _assert_geolocate_function_called("show_disabled_locators",
                                                   arguments)
        self.assertTrue(result)

    def test_process_optional_parameters_reset_locators_preference(self):
        arguments = Arguments(False, None, False, True)
        result = _assert_geolocate_function_called("reset_locators_preference",
                                                   arguments)
        self.assertTrue(result)

    def tests_process_optional_parameters_erroneos_argument(self):
        arguments = ErroneousArguments(False, None, False, False, True)
        with self.assertRaises(geolocate.NoFunctionAssignedToArgument) as e:
            geolocate._execute_function(ERRONEOUS_ARGUMENT, arguments)
        self.assertEqual(e.exception.argument, ERRONEOUS_ARGUMENT)


    def test_get_user_attributes(self):
        correct_arguments_set = {"show_enabled_locators",
                                 "set_locators_preference",
                                 "show_disabled_locators",
                                 "reset_locators_preference"}
        test_arguments_object = MockedArguments(True, True, True, True)
        valid_arguments = geolocate._get_user_arguments(test_arguments_object)
        self.assertEqual(valid_arguments, correct_arguments_set)


    def test_show_enabled_locators(self):
        correct_string = "Enabled locators:\n" \
                         "geoip2_webservice\n" \
                         "geoip2_local\n"
        with test_geowrappers.OriginalFileSaved(CONFIGURATION_PATH):
            geolocate.reset_locators_preference()
            with MockedConsoleOutput() as console:
                geolocate.show_enabled_locators()
                returned_output = console.output()
                self.assertEqual(returned_output, correct_string)

    def test_show_disabled_locators(self):
        correct_string = "Disabled locators:\n" \
                         "geoip2_webservice\n"
        enabled_locators = ["geoip2_local",]
        with test_geowrappers.OriginalFileSaved(CONFIGURATION_PATH):
            geolocate.set_locators_preference(enabled_locators)
            with MockedConsoleOutput() as console:
                geolocate.show_disabled_locators()
                returned_output = console.output()
                self.assertEqual(returned_output, correct_string)

    def test_set_locators_preference(self):
        correct_string = "Enabled locators:\n" \
                         "geoip2_local\n" \
                         "geoip2_webservice\n"
        new_locators_preference = ["geoip2_local", "geoip2_webservice"]
        with test_geowrappers.OriginalFileSaved(CONFIGURATION_PATH):
            geolocate.set_locators_preference(new_locators_preference)
            with MockedConsoleOutput() as console:
                geolocate.show_enabled_locators()
                returned_output = console.output()
                self.assertEqual(returned_output, correct_string)

    def test_reset_locators_preference(self):
        changed_string = "Enabled locators:\n" \
                         "geoip2_local\n" \
                         "geoip2_webservice\n"
        correct_string = "Enabled locators:\n" \
                         "geoip2_webservice\n" \
                         "geoip2_local\n"
        new_locators_preference = ["geoip2_local", "geoip2_webservice"]
        with test_geowrappers.OriginalFileSaved(CONFIGURATION_PATH):
            geolocate.set_locators_preference(new_locators_preference)
            with MockedConsoleOutput() as console:
                geolocate.show_enabled_locators()
                returned_output = console.output()
                self.assertEqual(returned_output, changed_string)
                console.reset()
                geolocate.reset_locators_preference()
                geolocate.show_enabled_locators()
                returned_output = console.output()
                self.assertEqual(returned_output, correct_string)


# def _reset_locators():
#     with config.OpenConfigurationToUpdate() as f:
#         f.configuration.reset_locators_preference()
#
#
# def _set_locators_preference(new_preference_list):
#     """
#     :param new_preference_list: Locator list ordered by preference.
#     :type new_preference_list: list
#     :return: None
#     """
#     with config.OpenConfigurationToUpdate() as f:
#         f.configuration.locators_preference = new_preference_list


def _assert_geolocate_function_called(function_name, arguments):
    target_to_patch = ".".join(["geolocate.geolocate", function_name])
    with patch(target_to_patch) as mocked_function:
        geolocate.process_optional_parameters(arguments)
    return mocked_function.called


class MockedConsoleOutput(object):
    """ Context manager to catch console output. """
    def __init__(self):
        self._saved_stdout = sys.stdout
        self._mocked_stdout = io.StringIO()

    def __enter__(self):
        sys.stdout = self._mocked_stdout
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._saved_stdout
        if exc_type is None:
            return True
        else:
            return False

    def output(self):
        """
        :return: Console output.
        :rtype: str
        """
        return self._mocked_stdout.getvalue()

    def reset(self):
        """ Reinit output buffer.

        :return: None
        """
        sys.stdout.truncate(0)
        sys.stdout.seek(0)