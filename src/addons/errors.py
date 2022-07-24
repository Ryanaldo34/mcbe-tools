from typing import Callable
from configparser import RawConfigParser

config = RawConfigParser()
config.read('config.cfg')

TEXTURE_ERRORS = config.getboolean('errors', 'missing_texture')
GEO_ERRORS = config.getboolean('errors', 'missing_geo')
ANIM_ERROR = config.getboolean('errors', 'missing_anim')
AC_ERROR = config.getboolean('errors', 'missing_ac')
SOUND_ERROR = config.getboolean('errors', 'missing_sounds')

class InvalidArgError(Exception):
    """Exception raise for an invalid argument passed into a function"""

    def __init__(self, arg: any, func: Callable):
        self.arg = arg
        self.func_name = func.__name__
        self.msg = f'The agument: {self.arg} is not valid for the function: {self.func_name}'
        super().__init__(self.msg)

class MissingTextureError(Exception):
    """Exception raised when an entity is missing a texture file"""
    def __init__(self, msg=''):
        super().__init__(msg)

class MissingGeometryError(Exception):
    """Exception raised when an entity is missing a geometry defintion"""
    def __init__(self, msg=''):
        super().__init__(msg)

class MissingAnimationError(Exception):
    """Exception raised when an entity is missing an animation file"""
    def __init__(self, msg=''):
        super().__init__(msg)

class MissingAnimationControllerFile(Exception):
    """Exception raised when an entity is missing an animation controller file"""
    def __init__(self, msg=''):
        super().__init__(msg)

class MissingSoundError(Exception):
    """Exception raised when an entity is missing sound definitions"""
    def __init__(self, msg=''):
        super().__init__(msg)

class BadDataInputExcep(Exception):
    """ An Excepption that is raised when data recieved is considered bad"""
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)