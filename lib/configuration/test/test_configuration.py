import pytest
from unittest.mock import patch
from pathlib import Path

from validate import ValidateError

from lib.configuration.configuration import Configuration, ConfigurationError, ConfigurationErrorReason


class TestConfiguration:
    # files in the above list are assumed to exist this many levels above (relative to local). 0 = local, 1="../", etc.
    file_num_levels_above: int = 0
    # exact paths to check for existence
    test_full_path_exist_list: list = []

    class TestFunctions:
        @staticmethod
        def get_higher_path(path: Path, levels=1):
            if path.suffix == '':
                raise TypeError  # no suffix will be considered a bogus file (i.e: a path only). Mistake

            path = path.absolute()
            name = path.name
            path = path.parent
            while levels > 0:
                path = path.parent
                levels -= 1
            path = path.joinpath(name)
            return path

        @staticmethod
        def mock_files_exist(path):
            """ patch method to mock that a specific file or files exist or not """
            file_exists = False
            # Attempting to match specific path.
            if TestConfiguration.test_full_path_exist_list.__contains__(path):
                file_exists = True

            return file_exists

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

    # We are patching .isfile() and not Path.exists() because that is what is used in ConfigObj
    @patch('os.path.isfile', wraps=TestFunctions.mock_files_exist)
    def test_config_exists_at_local_but_no_spec(self, patch1):
        """ Make sure config_spec.ini is also there """
        # with pytest.raises(ConfigurationError) as e:
        #     TestConfiguration.test_filename_exist_list = ['config.ini']
        #     c = Configuration()
        # assert e.value.reason == ConfigurationErrorReason.SpecificationNotFound

    @patch('os.path.isfile', wraps=TestFunctions.mock_files_exist)
    def test_config_and_spec_found_local_happy(self, patch1):
        """ Happy path to verify both files exist locally and we can pull a parameter from it """
        TestConfiguration.test_full_path_exist_list = [(str(Path('config.ini').absolute()))]
        TestConfiguration.test_full_path_exist_list.append(str(Path('config_spec.ini').absolute()))
        c = Configuration()
        val = c.get('level0_param1')
        assert val == 1234

    @patch('os.path.isfile', wraps=TestFunctions.mock_files_exist)
    def test_config_and_spec_found_higher_level(self, patch1):
        """ Verify we can find files one level up """
        with pytest.raises(ValueError) as e:
            config_path = Path('config.ini')
            config_path = TestConfiguration.TestFunctions.get_higher_path(config_path)
            spec_path = Path('config_spec.ini')
            spec_path = TestConfiguration.TestFunctions.get_higher_path(spec_path)

            TestConfiguration.test_full_path_exist_list = [(str(config_path))]
            TestConfiguration.test_full_path_exist_list.append(str(spec_path))
            c = Configuration(search_levels=1)
        # We don't actually have config files at the higher level, so Validator will fail. We just need to catch
        # this as it meant that ConfigObj "found" our file paths and moved on to validating the files
        assert e.value.args[0] == 'No configspec supplied.'

    @patch('os.path.isfile', wraps=TestFunctions.mock_files_exist)
    def test_config_not_found_at_higher_level(self, patch1):
        """ Verify we search all the way up the path to the anchor and can't find the config file """
        with pytest.raises(ConfigurationError) as e:
            TestConfiguration.test_full_path_exist_list = []
            c = Configuration(search_levels=-1)
        assert e.value.reason == ConfigurationErrorReason.ConfigurationNotFound

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












