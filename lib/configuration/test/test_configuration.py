import pytest
from unittest.mock import patch
from lib.configuration.configuration import Configuration


class TestConfiguration:
    filename: str = None

    def file_not_found(self):
        """ patch method to mock when a file doesn't exist """
        file_is_found = True
        if self == TestConfiguration.filename:
            file_is_found = False
        return file_is_found

    @patch('os.path.isfile', wraps=file_not_found)
    def test_config_not_present(self, patched):
        """ Make sure we flag when default config.ini isn't found
            Need to simulate the os isfile function since config.ini is available for other tests
        """
        with pytest.raises(IOError):
            TestConfiguration.filename = 'config.ini'
            c = Configuration()

    @patch('os.path.isfile', wraps=file_not_found)
    def test_configspec_not_present(self, patched):
        """ Make sure we flag when default configspec.ini isn't found
            Need to simulate the os isfile function since config.ini is available for other tests
        """
        with pytest.raises(IOError):
            TestConfiguration.filename = 'config_spec.ini'
            c = Configuration()

    def test_get_not_string(self):
        """ Make sure key is passed as a string """
        with pytest.raises(TypeError):
            c = Configuration()
            val = c.get(0)



