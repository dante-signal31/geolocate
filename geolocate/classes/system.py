"""
 Module to deal with base operating system.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import sys


def verify_python_version(major_version, minor_revision):
    """ Check if current python interpreter version is what we need.

    Compare current interpreter version with the one is provided as needed one.
    If not over needed one version abort execution gracefully warning user
    she is trying to use an unsupported python interpreter.

    :param major_version: Needed major version for Python interpreter.
    :type major_version: int
    :param minor_revision: Needed minor version for Python interpreter.
    :type minor_revision: int
    :return: None
    """
    if (major_version, minor_revision) > sys.version_info:
        message = "This program can only be run on Python {0}.{1} or newer, " \
                  "you are trying to use Python {2}.{3} instead.\nAborting " \
                  "execution.".format(major_version, minor_revision,
                                      sys.version_info[0], sys.version_info[1])
        sys.exit(message)