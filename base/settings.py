from __future__ import annotations

import sys
import inspect
import builtins

from collections.abc import Iterable

from typing import Union
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
            if not isinstance(values, dict):
                raise SettingTypeError(dict, type(values))
            try:
                try:
                    value = values[setting]
                except KeyError:
                    raise SettingNotFoundError()
            except SettingNotFoundError as e:
                raise SettingErrorMessage(setting, original_error=e)
            if value is None:
                setattr(self, setting, value)
            elif setting_type not in self.primitive:
                try:
                    setattr(self, setting, setting_type(value))
                except SettingTypeError as e:
                    raise SettingErrorMessage(setting, original_error=e)
                except SettingCheckError as e:
                    raise SettingErrorMessage(setting, original_error=e)
                except SettingNotFoundError as e:
                    raise SettingErrorMessage(setting, original_error=e)
                except SettingErrorMessage as e:
                    raise SettingErrorMessage(setting, branch_error=e)
            else:
                try:
                    if isinstance(value, setting_type):
                        setattr(self, setting, value)
                    else:
                        raise SettingTypeError(setting_type, type(setting))
                except SettingErrorMessage as e:
                    SettingErrorMessage(setting, original_error=e)


    def __getattribute__(self, name):
        rv = object.__getattribute__(self, name)
        if issubclass(type(rv), Terminus):
            return rv.get
        elif issubclass(type(rv), Dict):
            return rv.get
        elif issubclass(type(rv), List):
            return rv.get
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
    @property
    def get(self):
        return self.value

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
        """Method that handles exceptions thrown by the :meth:`Terminus.check`
        function.

        Parameters
        ----------
        check_method
            The abstract check method implementation to be called.

        Raises
        ------
        :class:`~.SettingCheckError`
            If the check function raises any exceptions.

        """
        try:
            self.check()
        except TypeError as e:
            raise SettingCheckError(e, self.value)
        except ValueError as e:
            raise SettingCheckError(e, self.value)

    def distribute(self, value: T):
        """Method called by the decorator :meth:`Terminus.assign` that
        tries to assign the value passed to the constructor of the
        :class:`Terminus` derived class.

        Parameters
        ----------
        value : :class:`TypeVar`
            The value passed to the constructor of the :class:`Terminus`
            derived class.

        """
        if not hasattr(self, "type"):
            raise AttributeError("The child class has no self.type attribute.")
        if not isinstance(self.type, type):
            raise ValueError(f"The value of the type attribute should be a {type}")
        if not isinstance(value, self.type):
            raise SettingTypeError(self.type, type(value))
        self.value = value


class List(Settings):
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
    def get(self):
        return self[:]

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
        if not hasattr(self, "type"):
            raise AttributeError("The child class has no self.type attribute.")
        if not isinstance(self.type, type):
            raise ValueError(f"The value of the type attribute should be a {type}")

        if not isinstance(values, list):
            raise SettingTypeError(list, type(values))

        self.value = list()

        if self.type not in self.primitive:
            for idx, item in enumerate(values):
                try:
                    self.value.append(self.type(item))
                except SettingErrorMessage as e:
                    raise SettingErrorMessage(f"[{idx}]", e)
        else:
            for idx, item in enumerate(values):
                try:
                    if not isinstance(item, self.type):
                        raise SettingTypeError(self.type, type(item))
                    self.value.append(item)
                except SettingTypeError as e:
                    raise SettingErrorMessage(f"[{idx}]", original_error=e)

    def __getitem__(self, key):
        """An overload of the list get item method.

        Returns the list or sub list or entry depending on `key`. If the items
        stored in the list are :class:`~.Terminus` derived, then it will return
        a list or value which are the `value` attribute of the terminus
        instances.

        """
        rv = self.value[key]
        if issubclass(self.type, Terminus):
            if isinstance(rv, Iterable):
                return [item.get for item in rv] 
            else:
                return rv.get
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


class Dict(Settings):
    """A base class for a dict of settings classes.

    This class is used to store a number of identical :class:`~.Settings` or
    :class:`~.Terminus` derived settings.

    It can have only ONE class attribute.  If more are added, the
    MultiplicityError is raised.

    The implementation of the derived class constructor should be as follows::

        @Settings.assign
        def __init__(self, values: list):
            self.value = type
    
    Where `type` is the type of the objects that will be in the list.

    """

    @property
    def get(self):
        return self.value

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
        if not hasattr(self, "type"):
            raise AttributeError("The child class has no self.type attribute.")
        if not isinstance(self.type, type):
            raise ValueError(f"The value of the type attribute should be a {type}")

        if not isinstance(values, dict):
            raise SettingTypeError(dict, type(values))

        self.value = dict()

        if self.type not in self.primitive:
            for key, value in values.items():
                try:
                    self.value[key] = self.type(value)
                except SettingErrorMessage as e:
                    raise SettingErrorMessage(key, e)
        else:
            for key, value in values.items():
                try:
                    if not isinstance(value, self.type):
                        raise SettingTypeError(self.type, type(value))
                    self.value[key] = value
                except SettingTypeError as e:
                    raise SettingErrorMessage(key, original_error=e)
    
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
        if issubclass(self.type, Terminus):
            return {k: v.value for k, v in self.value.items()}.values()
        else:
            return self.value.values()
    
    def items(self):
        if issubclass(self.type, Terminus):
            return {k: v.value for k, v in self.value.items()}.items()
        else:
            return self.value.items()


class SettingNotFoundError(Error):
    """The exception raised when a setting cannot be found in the passed
    :obj:`dict`.

    """
    def __init__(self):
        """The constructor for the :class:`SettingNotFoundError` class.

        """
        self.msg = "Setting not found." 


class SettingCheckError(Error):
    """The exception raised when a :class:`Terminus` fails its value check.

    """
    def __init__(self, raised_exception, value: T):
        """The constructor for the :class:`SettingCheckError` class.

        Parameters
        ----------
        raised_exception 
            The exception raised by the test.
        value : T
            The value which failed the check.
        """
        self.msg = raised_exception


class SettingErrorMessage(Error):
    """The exception raised when the setting found in the passed :obj:`dict`
    is of the wrong type.

    """
    def __init__(self,
                 current_name: str,
                 branch_error: SettingErrorMessage = None,
                 original_error: Union[SettingCheckError, SettingsTypeError] = None):
        """The constructor for the :class::`SettingTypeError` class.

        Parameters
        ----------
        setting : :obj:`str`
            The name of the setting which has an incorrect type passed.

        setting_type : :obj:`type`
            The expected type of the setting.
        """
        if original_error:
            self.route = [current_name]
            self.original_error = original_error

        elif branch_error:
            self.route = [current_name] + branch_error.route
            self.original_error = branch_error.original_error
        else:
            raise ValueError("Must pass either new error or branch error as parameter.")

        super().__init__(self.build_message())
    
    def build_message(self):
        rv = str()
        join = " -> "
        for item in self.route:
            if "[" in item: 
                rv = rv[:-len(join)]
            rv += f"{item}" + join
        rv += f"{str(self.original_error.msg)}"
        return rv
        

class SettingTypeError(Error):
    """The exception raised when the setting found in the passed :obj:`dict`
    is of the wrong type, when intantiating a :class:`~.Dict` object.

    """
    def __init__(self, expected: type, actual: type):
        """The constructor for the :class::`SettingDictTypeError` class.

        Parameters
        ----------
        expected : :obj:`type`
            The expected type.
        
        actual : :obj:`type`
            The recieved type.

        """
        self.msg = f"Expecting : {expected} | Received: {actual}"
