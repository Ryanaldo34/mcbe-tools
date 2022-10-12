from colorama import Fore, Back, Style
from typing import Callable
from configparser import NoSectionError, RawConfigParser
import os

config = RawConfigParser()
path = path = os.path.join(os.path.dirname(__file__), '..', 'config.cfg')
config.read(path)

TEXTURE_ERRORS: bool
GEO_ERRORS: bool
ANIM_ERROR: bool
AC_ERROR: bool
SOUND_ERROR: bool

try:
    TEXTURE_ERRORS = config.getboolean('errors', 'missing_texture')
    GEO_ERRORS = config.getboolean('errors', 'missing_geo')
    ANIM_ERROR = config.getboolean('errors', 'missing_anim')
    AC_ERROR = config.getboolean('errors', 'missing_ac')
    SOUND_ERROR = config.getboolean('errors', 'missing_sounds')
except NoSectionError:
    TEXTURE_ERRORS = True
    GEO_ERRORS = True
    ANIM_ERROR = False
    AC_ERROR = False
    SOUND_ERROR = False

class InvalidArgError(Exception):
    """Exception raise for an invalid argument passed into a function"""

    def __init__(self, arg: any, func: Callable):
        self.arg = arg
        self.func_name = func.__name__
        self.msg = f'The agument: {self.arg} is not valid for the function: {self.func_name}'
        super().__init__(self.msg)

class CustomComponentExistsError(Exception):
    """Exception raised when a custom component does not exist"""
    def __init__(self, component: str):
        msg = f'{component} does not exist or has not been registered!'
        super().__init__(msg)

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

class ComponentPropertyTypeError(Exception):
    """Exception raised when a add-on component (custom or minecraft) has a property passed with an incorrect value type"""
    def __init__(self, property, passed_type, expected_type):
        self.msg = f'The property: {property} was passed as type: {passed_type}. Expected: {expected_type}'
        super().__init__(self.msg)