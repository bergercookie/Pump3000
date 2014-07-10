# Mon May 26 18:46:09 EEST 2014, nickkouk

class MyError(Exception):
    """Base class for exceptions in this module."""
    pass

class BusyPump(MyError):
    """ Exception to be raised if the pump is busy to receive the command"""
    pass
class Window_Closed(MyError):
    """ Exception to be raised when the main window closes"""
    pass
