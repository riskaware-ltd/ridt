from datetime import datetime


class Error(Exception):
    """The base class from which all other Error classes inherit.

    """
    pass

class RIDTOSError(Error):
    """The exception raised when RIDT attempts to modify a file but is unable.

    """
    def __init__(self, error):
        """The constructor for the :class:`RIDTOSError` class

        Parameters
        ----------
        obj
            The object which is not a :class:`~datetime.datetime` object.

        """
        msg = f"The following error was encoutered: \n{error}"
        super().__init__(msg)


class NullError(Error):
    """The exception class raised when an operation is attempted on a null
    object.

    """

    def __init__(self, msg):

        super().__init__(msg)


class DateTimeTypeError(Error):
    """The exception raised if a value is not a :class:`~datetime.datetime`
    object, when it was expected to be.

    """

    def __init__(self, obj):
        """The constructor for the :class:`DateTimeTypeError` class

        Parameters
        ----------
        obj
            The object which is not a :class:`~datetime.datetime` object.

        """
        msg = f"The passed value {obj} was not {datetime}"
        super().__init__(msg)


class DictTypeError(Error):
    """The exception raised if a value is not a :obj:`dict`, when it was
    expected to be.

    """

    def __init__(self, obj):
        """The constructor for the :class:`DictTypeError` class

        Parameters
        ----------
        obj
            The object which is not a :obj:`dict`.

        """
        msg = f"The passed value {obj} was not {dict}"
        super().__init__(msg)


class FloatTypeError(Error):
    """The exception raised if a value is not a :obj:`float`, when it was
    expected to be.

    """

    def __init__(self, obj):
        """The constructor for the :class:`FloatTypeError` class

        Parameters
        ----------
        obj
            The object which is not a :obj:`float`.

        """
        msg = f"The passed value {obj} was not {float}"
        super().__init__(msg)


class ListTypeError(Error):
    """The exception raised if a value is not a :obj:`list`, when it was
    expected to be.

    """

    def __init__(self, obj):
        """The constructor for the :class:`ListTypeError` class

        Parameters
        ----------
        obj
            The object which is not a :obj:`list`.

        """
        msg = f"The passed value {obj} was not {list}"
        super().__init__(msg)


class StringTypeError(Error):
    """The exception raised if a value is not a :obj:`str`, when it was
    expected to be.

    """

    def __init__(self, obj):
        """The constructor for the :class:`StringTypeError` class

        Parameters
        ----------
        obj
            The object which is not a :obj:`str`.

        """
        msg = f"The passed value {obj} was not {str}"
        super().__init__(msg)


class IntTypeError(Error):
    """The exception raised if a value is not a :obj:`int`, when it was
    expected to be.

    """

    def __init__(self, obj):
        """The constructor for the :class:`IntTypeError` class

        Parameters
        ----------
        obj
            The object which is not a :obj:`int`.

        """
        msg = f"The passed value {obj} was not {int}"
        super().__init__(msg)


class UUIDNotFoundError(Error):
    """The exception raised if a uuid is not cannot be found in a particular
    register.

    """

    def __init__(self, uuid: str):
        """The constructor for the :class:`UUIDNotFoundError` class

        Parameters
        ----------
        obj
            The uuid which cannot be found.

        """
        msg = f"The uuid {uuid} could not be found."
        super().__init__(msg)


class DimensionError(Error):
    """The exception raised if a value is not of the desired dimension.
    """

    def __init__(self, obj, dim_required: int):
        """The constructor for the :class:`DimensionError` class

        Parameters
        ----------
        obj
            The object which is not a :obj:`int`.

        """
        msg = f"The dimension of {obj} is not {dim_required}"
        super().__init__(msg)
