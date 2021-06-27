from enum import Enum
from pathlib import Path, WindowsPath

import validate
from configobj import ConfigObj, Section
from validate import Validator, ValidateError
from loguru import logger


class ConfigurationErrorReason(Enum):
    ConfigurationNotFound = 0,  # Can't find 'config.ini'
    SpecificationNotFound = 1,  # Can't find 'config_spec.ini"
    InvalidFileNameType = 2,    # File wasn't string or Path type
    SearchFailed = 3,           # File couldn't be found at local or higher level (within search limits)
    InvalidParameter = 4,       # Couldn't find parameter in the configuration file and it had no default


class ConfigurationError(Exception):
    """ Information about Configuration Failures"""
    def __init__(self, reason='Unknown', details='None'):
        self.reason = reason
        self.details = details


class Configuration(ConfigObj):
    """ Wrapper for ConfigObj which allows key indexing without multi-square brackets """
    def __init__(self, infile='config.ini', configspec='config_spec.ini', search_levels=0, delimeter='/'):
        if type(delimeter) is str:
            self.param_delimeter = delimeter
        else:
            self.__logger_config(f'Configuration: Non-string delimeter ({delimeter})')
            raise TypeError

        path_config = Path(infile).absolute()
        path_spec = Path(configspec).absolute()
        config_files_found = True
        file_exception = None

        # If we pass -1 to search levels, we are going to search all the way up to the path anchor to find the files
        if search_levels < 0:
            search_levels = 10000  # Just make this some abnormally large number of file levels

        while search_levels >= 0:
            search_levels -= 1
            try:
                super().__init__(str(path_config), configspec=str(path_spec), file_error=True)
            except IOError as e:
                try:
                    path_config = self.__walk_dir_up__(path_config)
                    path_spec = self.__walk_dir_up__(path_spec)
                except NotADirectoryError:
                    config_files_found = False
                    file_exception = e
                    break
            finally:
                pass

        if config_files_found is False:
            err = ConfigurationError(details=file_exception.args[0])
            if file_exception.args[0].__contains__(infile):
                err.reason = ConfigurationErrorReason.ConfigurationNotFound
            elif file_exception.args[0].__contains__(configspec):
                err.reason = ConfigurationErrorReason.SpecificationNotFound
            raise err

        self.__logger_config(f'Configuration: {infile}, Spec: {configspec}')
        validator = Validator()
        results = self.validate(validator)

        if results is not True:
            self.__logger_config(f'{infile} validation failure, {results}')
            raise ValidateError

    @staticmethod
    def __logger_config(msg, level='DEBUG'):
        """ Consistent message format for logging"""
        logger.log(level, f'Configuration:{msg}')

    @staticmethod
    def __walk_dir_up__(dir_path: Path):
        """ method to go up one level in a directory path """
        if isinstance(dir_path, Path) is False:
            raise TypeError

        # blank name means we are at the top level
        if dir_path.name == '':
            raise NotADirectoryError

        new_dir = dir_path.parent

        # if there's a suffix, it's a file, so we need to append the file name to create a full path
        if dir_path.suffix != '':
            # Since the filename is rightmost item, we need parent of parent or we'll return the current folder
            new_dir = new_dir.parent / dir_path.name

        if dir_path.parts.__len__() == 2 and dir_path.parts[0] == dir_path.anchor:
            raise NotADirectoryError

        return new_dir

    @staticmethod
    def __getpath__(path):
        """ return a path object when given either a path object or just a string """
        path_obj = None

        try:
            path_obj = Path(path)
        except TypeError:
            err = ConfigurationError(ConfigurationErrorReason.InvalidFileNameType,
                                     details='Filename must be of type string or Path')
            raise err
        except Exception as e:
            Configuration.__logger_config(f'Unknown exception: {e}')

        path_obj = path_obj.absolute()
        return path_obj

    def get(self, key):
        """ return parameter using multi level indexing similar to file paths:
            Example: level1/level2/level3/parameter_name
        """
        if type(key) is not str:
            self.__logger_config(f'Configuration: Non-String ({key}) passed as parameter name')
            raise TypeError

        levels = key.split(self.param_delimeter)
        parse_obj = self
        param_val = None

        # Walk the levels until only a string is found. This is the actual parameter
        for level in levels:
            try:
                val = parse_obj[level]
                if type(val) is Section:
                    parse_obj = val
                else:
                    param_val = val
            except Exception as e:
                self.__logger_config(f'Unknown exception: {e}')

        if param_val is None:
            self.__logger_config(f'Parameter ({key}) not found and has no default value')
            bad_param_exception = ConfigurationError(reason=ConfigurationErrorReason.InvalidParameter,
                                                     details=f'Parameter ({key}) not found and has no default value')
            raise bad_param_exception
        else:
            self.__logger_config(f'{key}={param_val} ({type(param_val)})')
            return param_val


if __name__ == '__main__':
    pass