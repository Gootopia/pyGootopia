import pytest
from unittest.mock import patch
from pathlib import Path

from validate import ValidateError

from lib.configuration.configuration import Configuration, ConfigurationError, ConfigurationReason


class TestConfiguration:
    # list of files that are assumed to exist during testing. Set as required during specific tests
    test_files_exist_list: list = []

    class TestFunctions:
        def mock_files_exist(self):
            """ patch method to mock that a specific file or files exist or not """
            if TestConfiguration.test_files_exist_list.__contains__(self):
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
    def test_walk_dir_up_ok(self, patched):
        """ Happy path test to see that we get higher path. """
        # This is a garbage path, so we patch .exists() so it passes
        curr_dir = Path("c:/dir1/dir2/dir3")
        new_dir = Configuration.__walk_dir_up__(curr_dir)
        assert new_dir == Path('c:/dir1/dir2')

    def test_findfile_invalid_type(self):
        with pytest.raises(TypeError):
            Configuration.__findfile__(0)

    @patch('pathlib.Path.exists', return_value=False)
    def test_findfile_bad_filename_strtype(self, patched):
        with pytest.raises(FileNotFoundError):
            # 'unknown' is probably a bad file, but we patch anyway.
            Configuration.__findfile__('unknown')

    @patch('pathlib.Path.exists', return_value=False)
    def test_findfile_bad_filename_pathtype(self, patched):
        """ TODO: Might need to check for path types other than WindowsPath """
        with pytest.raises(FileNotFoundError):
            Configuration.__findfile__(Path('unknown'))

    def test_findfile_file_ok_strtype(self):
        path = Configuration.__findfile__('config.ini')
        assert path == Path('config.ini').absolute()

    def test_findfile_file_ok_pathtype(self):
        path = Configuration.__findfile__(Path('config.ini'))
        assert path == Path('config.ini').absolute()

    # We are patching .isfile() and not Path.exists() because that is what is used in ConfigObj
    @patch('os.path.isfile', wraps=TestFunctions.mock_files_exist)
    def test_config_not_present(self, patched):
        """ Make sure we flag when default config.ini isn't found """
        with pytest.raises(ConfigurationError) as e:
            TestConfiguration.test_files_exist_list = []
            c = Configuration()
        assert e.value.reason == ConfigurationReason.ConfigurationNotFound

    @patch('os.path.isfile', wraps=TestFunctions.mock_files_exist)
    def test_config_exists_but_no_spec(self, patched):
        """ Make sure config_spec.ini is also there """
        with pytest.raises(ConfigurationError) as e:
            TestConfiguration.test_files_exist_list = ['config.ini']
            c = Configuration()
        assert e.value.reason == ConfigurationReason.SpecificationNotFound

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












