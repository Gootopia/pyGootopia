from configobj import ConfigObj, Section
from validate import Validator, ValidateError
from loguru import logger


class ConfigurationInvalidKey(Exception):
    def __init__(self, key):
        self.key = key


class Configuration(ConfigObj):
    """ Wrapper for ConfigObj which allows key indexing with out multi-square brackets """
    def __init__(self, infile='config.ini', configspec='config_spec.ini', delimeter='/'):
        super().__init__(infile, configspec=configspec, file_error=True)
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