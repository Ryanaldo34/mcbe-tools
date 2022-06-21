from typing import Callable

class InvalidArgError(Exception):
    """Exception raise for an invalid argument passed into a function"""

    def __init__(self, arg: any, func: Callable):
        self.arg = arg
        self.func_name = func.__name__
        self.msg = f'The agument: {self.arg} is not valid for the function: {self.func_name}'
        super().__init__(self.msg)

class MissingReqFileExcep(Exception):

    """ An exception that is thrown when an entity is missing a required file that is critical to their defintion"""

    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class FileNotFoundExcep(Exception):

    """ An Exception that is raised when a file that is being opened is not found"""

    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class BadDataInputExcep(Exception):

    """ An Excepption that is raised when data recieved is considered bad"""
    
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)