import pytest
from unittest.mock import patch
from pathlib import Path

from validate import ValidateError

from lib.configuration.configuration import Configuration, ConfigurationInvalidKey


class TestConfiguration:
    filename: str = None

    def file_not_found(self):
        """ patch method to mock when a file doesn't exist """
        file_is_found = True
        if self == TestConfiguration.filename:
            file_is_found = False
        return file_is_found

    def test_findfile_invalid_type(self):
        with pytest.raises(TypeError):
            Configuration.__findfile__(0)

    def test_findfile_bad_filename_strtype(self):
        with pytest.raises(FileNotFoundError):
            Configuration.__findfile__('unknown')

    def test_findfile_bad_filename_pathtype(self):
        """ TODO: Might need to check for path types other than WindowsPath """
        with pytest.raises(FileNotFoundError):
            Configuration.__findfile__(Path('unknown'))

    def test_findfile_file_ok_strtype(self):
        path = Configuration.__findfile__('config.ini')
        assert path == Path('config.ini').absolute()

    def test_findfile_file_ok_pathtype(self):
        path = Configuration.__findfile__(Path('config.ini'))
        assert path == Path('config.ini').absolute()

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

    def test_validation_failure(self):
        """ Catch a validation error """
        with pytest.raises(ValidateError):
            # TODO: Probably cleaner to patch the Validation function
            c = Configuration(configspec='config_spec_bad.ini')

    def test_get_not_string(self):
        """ Make sure key is passed as a string """
        with pytest.raises(TypeError):
            c = Configuration()
            val = c.get(0)

    def test_get_parameter_not_found(self):
        """ Catch when a parameter does not exist (i.e: config_spec does not provide default value)
            We also want to make sure we get the name back as we can wrap a bunch of gets in a try block
         """
        invalid_name = 'bad_parameter_name'
        with pytest.raises(ConfigurationInvalidKey) as e:
            c = Configuration()
            val = c.get(invalid_name)
            assert val is None

        assert e.value.key == invalid_name

    def test_delimeter_is_string(self):
        """ Delimeter can only be a character string"""
        with pytest.raises(TypeError):
            c = Configuration(delimeter=0)

    def test_get_single_level(self):
        """ Check lowest level key. Check that we get the same value as when we access using ConfigObj style (dict)"""
        c = Configuration()
        val = c.get('level0_param1')
        assert val == 1234
        assert val == c['level0_param1']

    def test_get_level1(self):
        """ Check indented key (delimited). Also check that we get same value as when we access using ConfigObj
            method. This means the multiple [] of multi-dict access
        """
        c = Configuration()
        val = c.get('level1/param1')
        assert val == 5678
        assert val == c['level1']['param1']
        val = c.get('level1/param2')
        assert val == 9101112
        val = c.get('level1/param3')
        assert val == 'teststring'

    def test_get_multi_level(self):
        c = Configuration()
        val = c.get('level1/level2/param1')
        assert val == 'ABCD'












