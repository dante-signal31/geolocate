"""
 testing_tools.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""

import ntpath
import os
import shutil
import tempfile


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
        if os.path.isfile(self._original_file_path):
            shutil.copyfile(self._original_file_path, self._backup_file_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._restore_file()
        self._remove_backup_directory()
        if exc_type is None:
            return True
        else:
            return False

    def _restore_file(self):
        if os.path.isfile(self._backup_file_path):
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


class WorkingDirectoryChanged(object):
    """ Sometimes unit test executes at a different path level than usual
    execution code. This context manager restores normal working directory
    after context manager exit.
    """
    def __init__(self, new_working_dir):
        """
        :param new_working_dir: New working path.
        :return: str
        """
        self._old_working_dir = os.getcwd()
        self._new_working_dir = new_working_dir

    def __enter__(self):
        os.chdir(self._new_working_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._old_working_dir)
        if exc_type is None:
            return True
        else:
            return False
