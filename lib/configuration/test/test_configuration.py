import pytest
from unittest.mock import patch
from pathlib import Path

from validate import ValidateError

from lib.configuration.configuration import Configuration, ConfigurationError, ConfigurationErrorReason


class TestConfiguration:
    # list of files that are assumed to exist during testing. Set as required during specific tests
    test_files_exist_list: list = []
    file_numlevels_above: int = 0

    class TestFunctions:
        @staticmethod
        def mock_file_exist_on_higher_level():
            """ patch method to simulate a file exists in a folder one or more levels above """
            # If we start < 0 => we don't ever want to find the file
            if TestConfiguration.file_numlevels_above < 0:
                return False

            TestConfiguration.file_numlevels_above -= 1
            if TestConfiguration.file_numlevels_above < 0:
                return True
            else:
                return False

        @staticmethod
        def mock_files_exist(path):
            """ patch method to mock that a specific file or files exist or not """
            if TestConfiguration.test_files_exist_list.__contains__(path):
                return True
            else:
                return False

    def test_dir_up_non_pathtype(self):
        """ Catch when we pass something other than str or WindowsPath types """
        with pytest.raises(TypeError):
            up = Configuration.__walk_dir_up__(0)

    def test_walk_dir_up_badpath(self):
        """ Catch if the initial path is bad, so we'll assume that going up one level will also be bad """
        with pytest.raises(OSError):
            curr_dir = Path("c://badpath")
            new_dir = Configuration.__walk_dir_up__(curr_dir)

    def test_walk_dir_up_at_top(self):
        """ Catch that we can't go any higher if we are at the root of a path structure """
        with pytest.raises(NotADirectoryError):
            curr_dir = Path("c:")
            new_dir = Configuration.__walk_dir_up__(curr_dir)

    @patch('pathlib.Path.exists', return_value=True)
    def test_walk_dir_up_ok(self, patch1):
        """ Happy path test to make sure we get the next directory when we pass a path. """
        # This is a garbage path, so we patch .exists() so it passes
        curr_dir = Path("c:/dir1/dir2/dir3")
        new_dir = Configuration.__walk_dir_up__(curr_dir)
        assert new_dir == Path('c:/dir1/dir2')

    @patch('pathlib.Path.exists', return_value=True)
    def test_walk_dir_up_filepath_ok(self, patch1):
        """ Happy path to make sure we get the new full path (including file name) """
        # This is a garbage path, so we patch .exists() so it passes
        curr_dir = Path("c:/dir1/dir2/dir3/config.ini")
        new_dir = Configuration.__walk_dir_up__(curr_dir)
        assert new_dir == Path('c:/dir1/dir2/config.ini')

    def test_findfile_invalid_type(self):
        with pytest.raises(ConfigurationError):
            Configuration.__findfile__(0)

    @patch('pathlib.Path.exists', return_value=False)
    def test_findfile_bad_filename_strtype(self, patch1):
        with pytest.raises(ConfigurationError) as e:
            # 'unknown' is probably a bad file, but we patch anyway.
            Configuration.__findfile__('unknown')
        assert e.value.reason == ConfigurationErrorReason.SearchFailed

    @patch('pathlib.Path.exists', return_value=False)
    def test_findfile_bad_filename_pathtype(self, patch1):
        """ TODO: Might need to check for path types other than WindowsPath """
        with pytest.raises(ConfigurationError) as e:
            Configuration.__findfile__(Path('unknown'))
        assert e.value.reason == ConfigurationErrorReason.SearchFailed

    def test_findfile_file_ok_strtype(self):
        path = Configuration.__findfile__('config.ini')
        assert path == Path('config.ini').absolute()

    def test_findfile_file_ok_pathtype(self):
        path = Configuration.__findfile__(Path('config.ini'))
        assert path == Path('config.ini').absolute()

    @patch('pathlib.Path.exists', wraps=TestFunctions.mock_file_exist_on_higher_level)
    def test_findfile_found_on_local_level(self, patch1):
        """ Verify file is found with default (local) search (i.e: search_level=0) """
        higher_path = Path('config.ini').absolute().parent / 'config.ini'
        TestConfiguration.file_numlevels_above = 0
        found_path = Configuration.__findfile__('config.ini')
        assert found_path == higher_path

    @patch('pathlib.Path.exists', wraps=TestFunctions.mock_file_exist_on_higher_level)
    def test_findfile_found_on_higher_level(self, patch1):
        """ Verify we find the config files at a higher level when not found at local level """
        higher_path = Path('config.ini').absolute().parent.parent / 'config.ini'
        TestConfiguration.file_numlevels_above = 1
        found_path = Configuration.__findfile__('config.ini', max_levels=1)
        assert found_path == higher_path

    # We are patching .isfile() and not Path.exists() because that is what is used in ConfigObj
    @patch('os.path.isfile', wraps=TestFunctions.mock_files_exist)
    def test_config_not_present(self, patch1):
        """ Make sure we flag when default config.ini isn't found """
        with pytest.raises(ConfigurationError) as e:
            TestConfiguration.test_files_exist_list = []
            c = Configuration()
        assert e.value.reason == ConfigurationErrorReason.ConfigurationNotFound

    @patch('os.path.isfile', wraps=TestFunctions.mock_files_exist)
    def test_config_exists_but_no_spec(self, patch1):
        """ Make sure config_spec.ini is also there """
        with pytest.raises(ConfigurationError) as e:
            TestConfiguration.test_files_exist_list = ['config.ini']
            c = Configuration()
        assert e.value.reason == ConfigurationErrorReason.SpecificationNotFound

    def test_config_validation_failure(self):
        """ Catch a validation error. This uses the a test spec file to make sure it works """
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
        with pytest.raises(ConfigurationError) as e:
            c = Configuration()
            val = c.get(invalid_name)
            assert val is None

        assert e.value.reason == ConfigurationErrorReason.InvalidParameter
        # Make sure we include the parameter name in the details
        assert e.value.details.__contains__(invalid_name)

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












