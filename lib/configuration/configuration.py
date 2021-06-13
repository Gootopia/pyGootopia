import os
from configobj import ConfigObj


class Configuration(ConfigObj):
    def __init__(self, infile='config.ini', configspec='config_spec.ini'):
        super().__init__(infile, configspec=configspec, file_error=True)

    def get(self, key):
        """ return parameter using multi level format """
        if type(key) is not str:
            raise TypeError

        try:
            val = self[key]
        except KeyError:
            val = None
        finally:
            return val


if __name__ == '__main__':
    pass