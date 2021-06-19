# configuration.py
from enum import Enum
from pathlib import Path, WindowsPath
from configobj import ConfigObj, Section
from validate import Validator, ValidateError
from loguru import logger


class ConfigurationInvalidKey(Exception):
    def __init__(self, key):
        self.key = key


class ConfigurationReason(Enum):
    ConfigurationNotFound = 0,
    SpecificationNotFound = 1,


class ConfigurationError(Exception):
    """ Information about Configuration Failures"""
    def __init__(self, reason='Unknown', details='None'):
        self.reason = reason
        self.details = details


class Configuration(ConfigObj):
    """ Wrapper for ConfigObj which allows key indexing without multi-square brackets """
    def __init__(self, infile='config.ini', configspec='config_spec.ini', delimeter='/'):
        try:
            super().__init__(infile, configspec=configspec, file_error=True)
        except IOError as e:
            err = ConfigurationError(details=e.args[0])
            if e.args[0].__contains__(infile):
                err.reason = ConfigurationReason.ConfigurationNotFound
            elif e.args[0].__contains__(configspec):
                err.reason = ConfigurationReason.SpecificationNotFound
            raise err

        logger.log('DEBUG', f'Configuration: {infile}, Spec: {configspec}')
        validator = Validator()
        results = self.validate(validator)

        if results is not True:
            raise ValidateError

        if type(delimeter) is str:
            self.param_delimeter = delimeter
        else:
            logger.log('DEBUG', f'Configuration: Non-string delimeter ({delimeter})')
            raise TypeError

    @staticmethod
    def __walk_dir_up__(currdir:WindowsPath):
        """ method to go up one level in a directory path """
        if type(currdir) is not WindowsPath:
            raise TypeError

        # part length of 1 means we can't go any higher since we are at the root
        if currdir.parts.__len__() == 1:
            raise NotADirectoryError

        if currdir.exists() is not True:
            raise OSError

        higher_path_parts = [x for x in currdir.parts if x != currdir.stem]
        higher_path_obj = Path()
        for p in higher_path_parts:
            higher_path_obj = higher_path_obj / p
        return higher_path_obj

    @staticmethod
    def __getpath__(path):
        """ return a path object when given either a path object or just a string """
        if type(path) is str:
            return Path(path)
        elif type(path) is WindowsPath:
            return path
        else:
            raise TypeError

    @staticmethod
    def __findfile__(file):
        """ find a file in current path or when walking the path upwards """
        path = Configuration.__getpath__(file)

        if path.exists() is not True:
            raise FileNotFoundError

        return path.absolute()

    def get(self, key):
        """ return parameter using multi level indexing similar to file paths:
            Example: level1/level2/level3/parameter_name
        """
        if type(key) is not str:
            logger.log('DEBUG', f'Configuration: Non-String ({key}) passed as parameter name')
            raise TypeError

        levels = key.split(self.param_delimeter)
        parse_obj = self
        param_val = None

        # Walk the levels until only a string is found. This is the actual parameter to get
        for level in levels:
            try:
                val = parse_obj[level]
                if type(val) is Section:
                    parse_obj = val
                else:
                    param_val = val
            except Exception as e:
                logger.log('DEBUG', f'EXCEPTION: Unknown {e}')

        if param_val is None:
            logger.log('DEBUG', f'Configuration: Parameter ({key}) not found and has no default value')
            bad_param_exception = ConfigurationInvalidKey(key)
            raise bad_param_exception
        else:
            logger.log('DEBUG', f'Configuration: {key}={param_val} ({type(param_val)})')
            return param_val


if __name__ == '__main__':
    pass