import sys
import inspect
import builtins

from collections.abc import Iterable

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
        :class:`~.SettingNotFoundError`
            If one of the derived class' attributes cannot be found in
            `values`.

        :class:`~.SettingTypeError`
            If one of the type of one of the settings found in `values`
            is not of the required type, as defined in the derived class'
            constructor.
        
        :class:`~.AssignError`
            If a check error is caught when assigning a setting to a
            :class:`~.Terminus` instance.

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
                try:
                    setattr(self, setting, setting_type(value))
                except SettingListTypeError as e:
                    raise SettingTypeError(setting, e.setting_type)
                except SettingDictTypeError as e:
                    raise SettingTypeError(setting, e.setting_type)
                except CheckError as e:
                    raise AssignError(setting, e)
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


class CheckError(Error):
    """The exception raised when a :class:`Terminus` fails its value check.

    """
    def __init__(self, raised_exception, value: T):
        """The constructor for the :class:`CheckError` class.

        Parameters
        ----------
        raised_exception 
            The exception raised by the test.
        value : T
            The value which failed the check.
        """
        self.exception = raised_exception
        self.value = value
        msg = "A value passed to the initialiser of a Terminus class instance"\
              " has failed its check."
        super().__init__(msg)


class AssignError(Error):
    """The exception raised when a :class:`Settings` class catches a
    :class:`~.CheckError` exception when assigning a value.

    """
    def __init__(self, setting: str, check_error: CheckError):
        """The constructor for the :class:`AssignError` class.

        Parameters
        ----------
        setting: :obj:`str`
            The setting for which the exception is being raised.

        check_error: :class:`CheckError`
            The check error instance raised by the :class:`~.Terminus`
            instance.

        """
        print(check_error.exception)
        msg = f"When assigning the '{setting}' setting, the passed value "\
              f"'{check_error.value}' failed the value check with the "\
              f"following error: {check_error.exception}" 
        super().__init__(msg)


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
            self.action(self.check)
        return wrapper

    @abstractmethod
    def check(self):
        """An abstract method that defines the value checks to be performed on
        the settings stored in this class.

        Raises
        ------
        :obj:`TypeError`
            If the passed value is of the wrong type.
        
        :obj:`ValueError`
            If the passed value is outside acceptable bounds.

        """
        pass

    def action(self, check_method):
        """Method that handles the return value of the :meth:`Terminus.check`
        function.

        Parameters
        ----------
        check_method
            The abstract check method implementation to be called.

        Raises
        ------
        :class:`~.CheckError`
            If the check function raises any exceptions.

        """
        try:
            self.check()
        except TypeError as e:
            raise CheckError(e, self.value)
        except ValueError as e:
            raise CheckError(e, self.value)

    def distribute(self, value: T):
        """Method called by the decorator :meth:`Terminus.assign` that
        tries to assign the value passed to the constructor of the
        :class:`Terminus` derived class.

        Parameters
        ----------
        value : :class:`TypeVar`
            The value passed to the constructor of the :class:`Terminus`
            derived class.

        Raises
        ------
        :class:`~.SettingTypeError`
            If `value` is not of the required type, as defined in the derived
            class' constructor.

        """
        self.value = value

    @property
    def value(self):
        """`value` property that accesses the single class attribute,
        regardless of that attribute's name.

        """
        return list(self.__dict__.values())[0]


class List:
    """A base class for a list of settings classes.

    This class is used to store a number of identical :class:`~.Settings` or
    :class:`~.Terminus` derived settings.

    It can have only ONE class attribute.  If more are added, the
    MultiplicityError is raised.

    The implementation of the derived class constructor should be as follows::

        @TerminusSet.assign
        def __init__(self, values: list):
            self.value = type
    
    Where `type` is the type of the objects that will be in the list.

    """

    @property
    def primitive(self):
        """:obj:`list`(:obj:`type`) : a list of built in types.

        """
        return [getattr(builtins, d) for d in dir(builtins) if
                isinstance(getattr(builtins, d), type)]

    def __setattr__(self, name: str, value: T):
        """The setter method for :class:`TerminusSet` instances.

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
        """A decorator that applies the :meth:`List.distribute` to
        parameter of the constructor of the derived class.

        """
        @wraps(method)
        def wrapper(self, *args):
            method(self, *args)
            self.distribute(*args)
        return wrapper

    def distribute(self, values: list):
        """Method called by the decorator :meth:`List.assign` that
        tries to assign the values passed to the constructor of the
        :class:`List` derived class.

        Parameters
        ----------
        values : :obj:`list`
            The values passed to the constructor of the :class:`List`
            derived class.

        Returns
        -------
        None

        Raises
        ------
        :class:`~.SettingTypeError`
            If `values` is not a :obj:`list`.
        
        :class:`~.SettingsListTypeError`
            If any of the items in `values` are not of the required type,
            as specified in the derived class.

        """
        if not isinstance(values, list):
            raise SettingTypeError(values, list)

        setting_type = self.value
        self.value = list()

        if setting_type not in self.primitive:
            for item in values:
                self.value.append(setting_type(item))
        else:
            for item in values:
                if not isinstance(item, setting_type):
                    raise SettingListTypeError(setting_type)
                self.value.append(item)

    @property
    def value(self):
        """`value` property that accesses the single class attribute,
        regardless of that attribute's name.

        """
        return list(self.__dict__.values())[0]
    
    def __getitem__(self, key):
        """An overload of the list get item method.

        Returns the list or sub list or entry depending on `key`. If the items
        stored in the list are :class:`~.Terminus` derived, then it will return
        a list or value which are the `value` attribute of the terminus
        instances.

        """
        rv = self.value[key]
        if Terminus in self.value[0].__class__.__bases__:
            if isinstance(rv, Iterable):
                return [item.value for item in rv] 
            else:
                return rv.value
        else:
            return rv
    
    def __len__(self):
        """Mapping __len__ to attibute `value` __len__.
        
        Returns
        -------
        :obj:`int`
            The length of the stored list.

        """
        return len(self.value)


class Dict:
    """A base class for a dict of settings classes.

    This class is used to store a number of identical :class:`~.Settings` or
    :class:`~.Terminus` derived settings.

    It can have only ONE class attribute.  If more are added, the
    MultiplicityError is raised.

    The implementation of the derived class constructor should be as follows::

        @TerminusSet.assign
        def __init__(self, values: list):
            self.value = type
    
    Where `type` is the type of the objects that will be in the list.

    """

    @property
    def primitive(self):
        """:obj:`list`(:obj:`type`) : a list of built in types.

        """
        return [getattr(builtins, d) for d in dir(builtins) if
                isinstance(getattr(builtins, d), type)]

    def __setattr__(self, name: str, value: T):
        """The setter method for :class:`TerminusSet` instances.

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
        """A decorator that applies the :meth:`Dict.distribute` to
        parameter of the constructor of the derived class.

        """
        @wraps(method)
        def wrapper(self, *args):
            method(self, *args)
            self.distribute(*args)
        return wrapper

    def distribute(self, values: dict):
        """Method called by the decorator :meth:`Dict.assign` that
        tries to assign the values passed to the constructor of the
        :class:`Dict` derived class.

        Parameters
        ----------
        values : :obj:`dict`
            The values passed to the constructor of the :class:`Dict`
            derived class.

        Returns
        -------
        None

        Raises
        ------
        :class:`~.SettingTypeError`
            If `values` is not a :obj:`dict`.
        
        :class:`~.SettingsDictTypeError`
            If any of the values in `values` are not of the required type,
            as specified in the derived class.

        """
        if not isinstance(values, dict):
            raise SettingTypeError(values, dict)

        setting_type = self.value
        self.value = dict()

        if setting_type not in self.primitive:
            for key, value in values.items():
                self.value[key] = setting_type(value)
        else:
            for key, value in values.items():
                if not isinstance(value, setting_type):
                    raise SettingDictTypeError(setting_type)
                self.value[key] = value

    @property
    def value(self):
        """`value` property that accesses the single class attribute,
        regardless of that attribute's name.

        """
        return list(self.__dict__.values())[0]
    
    def __getitem__(self, key):
        """An overload of the :obj:`dict` __getitem__ method.

        Returns the value for the given key. If the value is :class:`~.Terminus`
        derived, then it will return `value` attribute of the terminus instance.

        """
        rv = self.value[key]
        if Terminus in rv.__class__.__bases__:
            return rv.value
        else:
            return rv
    
    def __len__(self):
        """Mapping __len__ to attibute `value` __len__.
        
        Returns
        -------
        :obj:`int`
            The length of the stored list.

        """
        return len(self.value)
    
    def keys(self):
        return self.value.keys()
    
    def values(self):
        if Terminus in list(self.value.values())[0].__class__.__bases__:
            return {k: v.value for k, v in self.value.items()}.values()
        else:
            return self.value.values()
    
    def items(self):
        if Terminus in list(self.value.values())[0].__class__.__bases__:
            return {k: v.value for k, v in self.value.items()}.items()
        else:
            return self.value.items()


class MultiplicityError(Error):
    """The exception raised when more than one attribute are assigned to a
    :class:`Terminus` instance.

    """

    def __init__(self):
        """The constructor for the :class:`MultiplicityError` class.
        """
        msg = f"More than one setting value defined in a {Terminus} instance."
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


class SettingListTypeError(Error):
    """The exception raised when the setting found in the passed :obj:`list`
    is of the wrong type, when intantiating a :class:`~.List` object.

    """
    def __init__(self, setting_type: type):
        """The constructor for the :class::`SettingListTypeError` class.

        Parameters
        ----------
        setting_type : :obj:`type`
            The expected type of the setting.

        """
        self.setting_type = setting_type
        super().__init__()


class SettingDictTypeError(Error):
    """The exception raised when the setting found in the passed :obj:`dict`
    is of the wrong type, when intantiating a :class:`~.Dict` object.

    """
    def __init__(self, setting_type: type):
        """The constructor for the :class::`SettingDictTypeError` class.

        Parameters
        ----------
        setting_type : :obj:`type`
            The expected type of the setting.

        """
        self.setting_type = setting_type
        super().__init__()
