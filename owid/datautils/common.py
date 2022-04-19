"""Common objects shared by other modules.

"""

from typing import Union, Any


class ExceptionFromDocstring(Exception):
    """Exception that returns its own docstring, if no message is explicitly given."""

    def __init__(self, exception_message: Union[str, None] = None, *args: Any):
        super().__init__(exception_message or self.__doc__, *args)
