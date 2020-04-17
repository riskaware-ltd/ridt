import sys
import inspect
import builtins

from typing import TypeVar
from abc import ABC
from abc import abstractmethod
from functools import wraps

from base.exceptions import Error

T = TypeVar("T")


class Settings:
    """A base class for building python objects out of :obj:`dict` object.

    This class is designed as a recursive method of building python objects
    from json files.

    If the parsed json file does not match the defined settings class
    in attribute names and type, it will catch it an terminate with an error
    message.

    Example
    -------

    The following is a simple use case::

        class UserSettings(Settings):

            @Settings.assign
            def __init__(self, values: dict):
                self.setting_1 = int
                self.setting_2 = SubSetting

        class SubSetting(Settings):

            @Settings.assign
            def __init__(self, values: dict):
                self.subsetting_1 = str

    The `values` parameter should be, for example::

        values = {
            "setting_1": 1,
            "setting_2": {
                subsetting_1: "this_is_a_string"
            }
        }

    This results in::

        settings = UserSettings(values)

        print(settings.setting_1)
            # 1

        print(settings.setting_2.subsetting_1)
            # this_is_a_string

    """

    @staticmethod
    def assign(method):
        """A decorator that applies the
        :meth:`~.Settings.distribute` to parameter of the
        constructor of the derived class.

        """
        @wraps(method)
        def wrapper(self, *args):
            method(self, *args)
            self.distribute(*args)
        return wrapper

    @property
    def primitive(self):
        """:obj:`list`(:obj:`type`) : a list of built in types.

        """
        return [getattr(builtins, d) for d in dir(builtins) if
                isinstance(getattr(builtins, d), type)]

    def distribute(self, values: dict):
        """The method which loops over the attribute/type pairs in the derived
        class' constructor and tries to find and assign values to them from the
        `values` parameter.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary that contains the values to be assigned to the
            derived class' attributes.

        Returns
        -------
        None

        Raises
        ------
        SettingNotFoundError
            If one of the derived class' attributes cannot be found in
            `values`.

        SettingTypeError
            If one of the type of one of the settings found in `values`
            is not of the required type, as defined in the derived class'
            constructor.

        Note
        ----
        If the setting found in the `values` is None, then this function will
        assign None as the setting value by default, independent of the expected
        value.

        """
        for setting, setting_type in self.__dict__.items():
            try:
                value = values[setting]
            except KeyError:
                raise SettingNotFoundError(setting, self.__class__.__name__)
            if value is None:
                setattr(self, setting, value)
            elif setting_type not in self.primitive:
                setattr(self, setting, setting_type(value))
            else:
                if isinstance(value, setting_type):
                    setattr(self, setting, value)
                else:
                    raise SettingTypeError(setting, setting_type)

    def __getattribute__(self, name):
        rv = object.__getattribute__(self, name)
        if Terminus in rv.__class__.__bases__:
            return list(rv.__dict__.values())[0]
        else:
            return rv

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Terminus(ABC):
    """A base class for a terminating setting.

    This class is used to store a single settting in a :class:`~.Settings`
    derived class.

    It can have only ONE class attribute.  If more are added, the
    MultiplicityError is raised.

    If the expected type of a :class:`~.Settings` derived class attribute
    inherits from :class:`Termninus`, then when __getattribute__ is called to
    access the :class:`Terminus` instance, it will return the single
    :class:`Terminus` instance attribute instead.

    This structure allows for value checks to be applied to individual settings,
    on instantiation of :class:`~.Settings` derived classes.

    As with the :class:`~.Settings` derived classes, the decorator
    :meth:`Terminus.assign` should be applied to :class:`Terminus` derived class
    constructors. If this is done, the abstract method :meth:`Terminus.check` is
    automatically called after the derived class' constructor.

    """

    def __setattr__(self, name: str, value: T):
        """The setter method for :class:`Terminus` instances.

        Parameters
        ----------
        name : :obj:`str`
            The name of the attribute to be set.

        value: T
            The value to be assigned to the attribute.

        Raises
        ------
        MultiplicityError
            If the passed name is not the same as the existing attribute name.

        """
        if len(self.__dict__) > 1:
            raise MultiplicityError()
        else:
            self.__dict__[name] = value

    @staticmethod
    def assign(method):
        """A decorator that applies the :meth:`Terminus.distribute` to
        parameter of the constructor of the derived class. It will also then
        call the :meth:`Terminus.check` function.

        """
        @wraps(method)
        def wrapper(self, *args):
            method(self, *args)
            self.distribute(*args)
            self.action(self.check())
        return wrapper

    @abstractmethod
    def check(self):
        """An abstract method that defines the value checks to be performed on
        the settings stored in this class.

        Returns
        -------
        bool
            The success or failure of the check.

        """
        pass

    def action(self, result: bool):
        """Method that handles the return value of the :meth:`Terminus.check`
        function.

        Parameters
        ----------
        result : :obj:`bool`
            The return value of the :meth:`Terminus.check` method.

        Raises
        ------
        CheckError
            If the result is False.

        """
        if not result:
            raise CheckError(self.__class__.__name__, self.value)

    def distribute(self, value: T):
        """Method called by the decorator :meth:`Terminus.assign` that
        tries to assign the value passed to the constructor of the
        :class:`Terminus` derived class to the attribute/type pair in the
        derived class' constructor

        Parameters
        ----------
        value : :class:`TypeVar`
            The value passed to the constructor of the :class:`Terminus`
            derived class.

        Raises
        ------
        SettingTypeError
            If `value` is not of the required type, as defined in the derived
            class' constructor.

        """

        if isinstance(value, self.value):
            self.value = value
        else:
            SettingTypeError(self.__class__.__name__, self.value)

    @property
    def value(self):
        """`value` property that accesses the single class attribute,
        regardless of that attribute's name.

        """
        return list(self.__dict__.values())[0]


class MultiplicityError(Error):
    """The exception raised when more than one attribute are assigned to a
    :class:`Terminus` instance.

    """

    def __init__(self):
        """The constructor for the :class:`MultiplicityError` class.
        """
        msg = f"More than one setting value defined in a {Terminus} instance."
        super().__init__(msg)


class CheckError(Error):
    """The exception raised when a :class:`Terminus` fails its value check.

    """
    def __init__(self, derived_class: Terminus, value: T):
        """The constructor for the :class:`CheckError` class.

        Parameters
        ----------
        derived_class : :class:`Terminus`
            The :class:`Terminus` derived class which failed the test.
        value : T
            The value which failed the check.
        """
        msg = f"A {derived_class} class has failed its check. Value: {value}"
        super().__init__(msg)


class SettingNotFoundError(Error):
    """The exception raised when a setting cannot be found in the passed
    :obj:`dict`.

    """
    def __init__(self, setting: str, settings_class: type):
        """The constructor for the :class:`SettingNotFoundError` class.

        Parameters
        ----------
        setting : :obj:`str`
            The name of the setting that cannot be found.

        settings_class : :obj:`type`
            The :class:`~.Settings` dertived class to
            which the missing setting belongs.
        """
        msg = f"The setting '{setting}' was not found " \
              f"for the {settings_class} object. Please check the relevant " \
              f"config file."
        super().__init__(msg)


class SettingTypeError(Error):
    """The exception raised when the setting found in the passed :obj:`dict`
    is of the wrong type.

    """
    def __init__(self, setting: str, setting_type: type):
        """The constructor for the :class::`SettingTypeError` class.

        Parameters
        ----------
        setting : :obj:`str`
            The name of the setting which has an incorrect type passed.

        setting_type : :obj:`type`
            The expected type of the setting.
        """
        msg = f"The found setting {setting} was not of type {setting_type}."
        super().__init__(msg)
