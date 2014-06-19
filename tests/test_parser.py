"""
 test_logparser.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import io
import os
import sys
import unittest
import unittest.mock
sys.path.append(os.path.abspath(".."))
import geolocate.classes.parser as parser
import geolocate.classes.geowrapper as geoip


TEST_STRING = """TRACEROUTE OUTPUT
traceroute to www.google.com (173.194.45.51), 30 hops max, 60 byte packets
 1  192.168.1.1 (192.168.1.1)  2.923 ms  4.180 ms  4.092 ms
 2  90.Red-80-58-67.staticIP.rima-tde.net (80.58.67.90)  7.713 ms  7.657 ms  7.601 ms
 3  57.Red-80-58-76.staticIP.rima-tde.net (80.58.76.57)  11.990 ms  11.948 ms  13.062 ms
 4  145.Red-80-58-86.staticIP.rima-tde.net (80.58.86.145)  9.630 ms  14.929 ms  14.872 ms
 5  AE3-GRCMADJV1.red.telefonica-wholesale.net (5.53.1.77)  9.431 ms  9.337 ms  11.313 ms
 6  5.53.1.82 (5.53.1.82)  12.499 ms  13.972 ms  15.852 ms
 7  209.85.252.150 (209.85.252.150)  15.817 ms  15.798 ms 209.85.251.242 (209.85.251.242)  15.779 ms
 8  209.85.240.189 (209.85.240.189)  55.590 ms  55.581 ms  55.550 ms
 9  209.85.245.82 (209.85.245.82)  37.949 ms  37.937 ms 209.85.245.71 (209.85.245.71)  50.830 ms
10  66.249.94.79 (66.249.94.79)  40.635 ms  37.871 ms  40.588 ms
11  par03s12-in-f19.1e100.net (173.194.45.51)  37.817 ms  40.528 ms  37.954 ms
"""
TEST_STRING_IP_ADDRESSES = ("173.194.45.51",
                            "192.168.1.1",
                            "80.58.67.90",
                            "80.58.76.57",
                            "80.58.86.145",
                            "5.53.1.77",
                            "5.53.1.82",
                            "209.85.252.150",
                            "209.85.251.242",
                            "209.85.240.189",
                            "209.85.245.82",
                            "209.85.245.71",
                            "66.249.94.79",
                            "173.194.45.51")

TEST_IP = "173.194.45.51"

TEST_IP_FIELDS = {
            TEST_IP : {"continent_name": "North America",
                       "country_name": "United States",
                       "city_name": "Mountain View",
                       "lat-long": "37.419200000000004, -122.0574"}
            }

TEST_IP_LOCATION_STRINGS = {
            TEST_IP : {0: "173.194.45.51 [North America]",
                       1: "173.194.45.51 [North America | United States]",
                       2: "173.194.45.51 [North America | United States | "
                          "Mountain View]",
                       3: "173.194.45.51 [North America | United States | "
                          "Mountain View | 37.419200000000004, -122.0574]"}
            }

TEST_IP_GEOLOCATION_STRINGS = {
            TEST_IP : {0: "[North America]",
                       1: "[North America | United States]",
                       2: "[North America | United States | "
                          "Mountain View]",
                       3: "[North America | United States | "
                          "Mountain View | 37.419200000000004, -122.0574]"}
            }

MOCKED_LOCATE_RESPONSE = {"continent_name": "North America",
                          "country_name": "United States",
                          "city_name": "Mountain View",
                          "latitude": "37.419200000000004",
                          "longitude": "-122.0574"}

IP_NOT_FOUND_MESSAGE = "IP not found"

MOCKED_RESULTS_VERBOSITY_0 = {"173.194.45.51": 'North America',
                              "192.168.1.1": IP_NOT_FOUND_MESSAGE,
                              "80.58.67.90": 'Europe',
                              "80.58.76.57": 'Europe',
                              "80.58.86.145": 'Europe',
                              "5.53.1.77": 'Europe',
                              "5.53.1.82": 'Europe',
                              "209.85.252.150": 'North America',
                              "209.85.251.242": 'North America',
                              "209.85.240.189": 'North America',
                              "209.85.245.82": 'North America',
                              "209.85.245.71": 'North America',
                              "66.249.94.79": 'North America',
                              "173.194.45.51": 'North America'}

CORRECT_RESULT_TEXT = """TRACEROUTE OUTPUT
traceroute to www.google.com (173.194.45.51 [North America]), 30 hops max, 60 byte packets
 1  192.168.1.1 [IP not found] (192.168.1.1 [IP not found])  2.923 ms  4.180 ms  4.092 ms
 2  90.Red-80-58-67.staticIP.rima-tde.net (80.58.67.90 [Europe])  7.713 ms  7.657 ms  7.601 ms
 3  57.Red-80-58-76.staticIP.rima-tde.net (80.58.76.57 [Europe])  11.990 ms  11.948 ms  13.062 ms
 4  145.Red-80-58-86.staticIP.rima-tde.net (80.58.86.145 [Europe])  9.630 ms  14.929 ms  14.872 ms
 5  AE3-GRCMADJV1.red.telefonica-wholesale.net (5.53.1.77 [Europe])  9.431 ms  9.337 ms  11.313 ms
 6  5.53.1.82 [Europe] (5.53.1.82 [Europe])  12.499 ms  13.972 ms  15.852 ms
 7  209.85.252.150 [North America] (209.85.252.150 [North America])  15.817 ms  15.798 ms 209.85.251.242 [North America] (209.85.251.242 [North America])  15.779 ms
 8  209.85.240.189 [North America] (209.85.240.189 [North America])  55.590 ms  55.581 ms  55.550 ms
 9  209.85.245.82 [North America] (209.85.245.82 [North America])  37.949 ms  37.937 ms 209.85.245.71 [North America] (209.85.245.71 [North America])  50.830 ms
10  66.249.94.79 [North America] (66.249.94.79 [North America])  40.635 ms  37.871 ms  40.588 ms
11  par03s12-in-f19.1e100.net (173.194.45.51 [North America])  37.817 ms  40.528 ms  37.954 ms
"""

class TestParser(unittest.TestCase):

    @staticmethod
    def setUpClass():
        TestInputReader._inject_to_stdin = TestInputReader._replace_stdin()

    @staticmethod
    def tearDownClass():
        TestInputReader._restore_stdin()

    def test_GeolocateInputParser_next(self):
        """Check class is able to analyze input line by line and return
        lines with geodata strings included.
        """
        ## TODO: Remove mocks when geoip is implemented.
        TestInputReader._inject_to_stdin(TEST_STRING)
        geoip_database = unittest.mock.MagicMock(name="GeoIPDatabase",
                                                 spec=geoip.GeoIPDatabase)
        input_parser = parser.GeolocateInputParser(0, geoip_database)
        input_parser._geoip_database.locate = unittest.mock.MagicMock(
                                                    name="locate",
                                                    side_effect=self.__class__._mocked_locate_results)
        lines = []
        for line in input_parser:
            lines.append(line)
        result_text = _rejoin_lines(lines)
        self.assertEqual(result_text,
                         CORRECT_RESULT_TEXT,
                         msg="Rebuilt text and test string doesn't match.\n"
                             "Rebuilt text:\n {0}\n"
                             "Test string:\n {1}".format(result_text,
                                                         CORRECT_RESULT_TEXT))

    @staticmethod
    def _mocked_locate_results(ip_address):
        if MOCKED_RESULTS_VERBOSITY_0[ip_address] == IP_NOT_FOUND_MESSAGE:
            raise geoip.IPNotFound(ip_address)
        else:
            mocked_location = {"continent_name":
                                   MOCKED_RESULTS_VERBOSITY_0[ip_address]}
            return mocked_location

    def test_GeolocateInputParser_locate(self):
        """Check locate() returns an string correctly formatted for every
        verbosity level.
        """
        ## TODO: Remove mocked_locate_response when _geoip_database.locate is
        ## implemented.
        verbosity_levels = parser.GeolocateInputParser.VERBOSITY_LEVELS
        ip_to_find = TEST_IP
        geoip_database = geoip.load_geoip_database()
        for verbosity in verbosity_levels:
            input_parser = parser.GeolocateInputParser(verbosity, geoip_database)
            ## TODO: Remove Mock when _geoip_database.locate is implemented.
            input_parser._geoip_database.locate = unittest.mock.MagicMock(
                                                    return_value=MOCKED_LOCATE_RESPONSE)
            location_string = input_parser._locate(ip_to_find)
            self.assertEqual(location_string,
                             TEST_IP_LOCATION_STRINGS[TEST_IP][verbosity])

    def test_GeolocateInputParser_format_location_string(self):
        """Check format_location_string() returns an string correctly formatted
        for every verbosity level.
        """
        verbosity_levels = parser.GeolocateInputParser.VERBOSITY_LEVELS
        for verbosity in verbosity_levels:
            input_parser = parser.GeolocateInputParser(verbosity, None)
            location_string = input_parser._format_location_string(
                                                        MOCKED_LOCATE_RESPONSE)
            self.assertEqual(location_string,
                             TEST_IP_GEOLOCATION_STRINGS[TEST_IP][verbosity])

    def test_find_ips_in_text(self):
        """Check all embedded IP addresses are found."""
        returned_IP_addresses = set()
        test_text_lines = TEST_STRING.splitlines()
        test_ip_addresses = set(TEST_STRING_IP_ADDRESSES)
        for line in test_text_lines:
            line_IP_addresses = parser._find_ips_in_text(line)
            returned_IP_addresses.update(line_IP_addresses)
        self.assertEqual(returned_IP_addresses, test_ip_addresses)

    def test_include_location_in_line(self):
        """Check IP addresses are properly replaced with geodata string."""
        line = ("traceroute to www.google.com (173.194.45.51), 30 hops max, "
                "60 byte packets")
        ip = "173.194.45.51"
        location = "173.194.45.51 [North America | United States]"
        correct_line = ("traceroute to www.google.com (173.194.45.51 "
                        "[North America | United States]), 30 hops max, "
                        "60 byte packets")
        returned_line = parser._include_location_in_line(line, ip, location)
        self.assertEqual(returned_line,
                         correct_line,
                         msg="Rebuilt text and test string doesn't match.\n"
                             "Rebuilt text:\n {0}\n"
                             "Test string:\n {1}".format(returned_line,
                                                         correct_line))


class TestInputReader(unittest.TestCase):

    _inject_to_stdin = None
    _old_stdin = None

    @classmethod
    def setUpClass(cls):
        cls._inject_to_stdin = cls._replace_stdin()

    @classmethod
    def _replace_stdin(cls):
        cls._old_stdin = sys.stdin
        def _inject_string(string):
            sys.stdin = io.StringIO(string)
        return _inject_string

    @classmethod
    def tearDownClass(cls):
        cls._restore_stdin()

    @classmethod
    def _restore_stdin(cls):
        sys.stdin = cls._old_stdin

    def test_InputReader(self):
        """Inject text in stdin and compare what is read from there to check
        it is the same.
        """
        self.__class__._inject_to_stdin(TEST_STRING)
        input_reader = parser.InputReader()
        lines = _read_stdin(input_reader)
        rebuilt_text = _rejoin_lines(lines)
        self.assertEqual(rebuilt_text,
                         TEST_STRING,
                         msg="Rebuilt text and test string doesn't match.\n"
                             "Rebuilt text:\n {0}\n"
                             "Test string:\n {1}".format(rebuilt_text,
                                                         TEST_STRING))


def _read_stdin(input_reader):
    lines_read = (line for line in input_reader)
    return lines_read


def _rejoin_lines(lines):
    rebuilt_text = "".join(lines)
    return rebuilt_text
