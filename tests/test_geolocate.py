"""
 test_geolocate.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

from collections import namedtuple
from unittest.mock import patch
import unittest

import geolocate.geolocate as geolocate

Arguments = namedtuple("Arguments", "show_enabled_locators "
                                    "set_locators_preference "
                                    "show_disabled_locators "
                                    "reset_locators_preference ")


class TestGeoLocate(unittest.TestCase):

    def test_process_optional_parameters_show_enabled_locators(self):
        arguments = Arguments(True, None, False, False)
        _assert_geolocate_function_called("show_enabled_locators", arguments)

    def test_process_optional_parameters_set_locators_preference(self):
        arguments = Arguments(False, ["geoip2_local", "geoip2_webservice"],
                              False, False)
        _assert_geolocate_function_called("set_locators_preference", arguments)

    def test_process_optional_parameters_show_disabled_locators(self):
        arguments = Arguments(False, None, True, False)
        _assert_geolocate_function_called("show_disabled_locators", arguments)

    def test_process_optional_parameters_reset_locators_preference(self):
        arguments = Arguments(False, None, False, True)
        _assert_geolocate_function_called("reset_locators_preference",
                                          arguments)


def _assert_geolocate_function_called(function_name, arguments):
    with patch(geolocate, function_name) as mocked_function:
        geolocate.process_optional_parameters(arguments)
    mocked_function.assert_any_call()
