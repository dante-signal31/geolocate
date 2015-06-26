"""
 Geolocate launcher.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import sys

def verify_python_version(major_version, minor_revision):
    if (major_version, minor_revision) > sys.version_info:
        message = "This program can only be run on Python {0}.{1} or newer, " \
                  "you are trying to use Python {2}.{3} instead.\nAborting " \
                  "execution.".format(major_version, minor_revision,
                                      sys.version_info[0], sys.version_info[1])
        sys.exit(message)

verify_python_version(3, 0)

from geolocate.glocate import main

main()
