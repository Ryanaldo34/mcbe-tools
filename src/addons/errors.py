from typing import Callable

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