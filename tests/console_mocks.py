"""
 console_mocks.py

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import io
import sys


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

    @staticmethod
    def reset():
        """ Reinit output buffer.

        :return: None
        """
        sys.stdout.truncate(0)
        sys.stdout.seek(0)