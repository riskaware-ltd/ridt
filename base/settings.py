from __future__ import annotations

import sys
import inspect
import builtins
import operator
import itertools

from pprint import pprint

from copy import deepcopy

from collections.abc import Iterable

from itertools import chain

from typing import Union
from typing import TypeVar
from typing import Type
from typing import List
from typing import Tuple

from abc import ABC
from abc import abstractmethod

from functools import wraps
from functools import reduce

from numpy import linspace
from numpy import prod
from numpy import meshgrid
from numpy import unravel_index

from .exceptions import Error

import warnings

def custom_formatwarning(msg, *args, **kwargs):
    return "Warning: " + str(msg) + '\n'

warnings.formatwarning = custom_formatwarning


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
            try:
                self.consistency_check()
            except AttributeError:
                pass
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
                except SettingRangeTypeError as e:
                    raise SettingErrorMessage(setting, original_error=e)
                except SettingRangeKeyError as e:
                    raise SettingErrorMessage(setting, original_error=e)
                except SettingStringSelectionError as e:
                    raise SettingErrorMessage(setting, original_error=e)
                except ConsistencyError as e:
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
        self.__source__ = values

    def __getattribute__(self, name):
        rv = object.__getattribute__(self, name)
        if issubclass(type(rv), Terminus):
            return rv.get
        elif issubclass(type(rv), Dict):
            return rv.get
        elif issubclass(type(rv), List):
            return rv.get
        elif issubclass(type(rv), Number):
            return rv.get
        else:
            return rv

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __hash__(self):
        return hash(str(self.__source__))
    
    def __eq__(self, other):
        if other.__hash__() == self.__hash__():
            return True
        else:
            return False


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
            raise TypeAttributeNotImplementedError(self.__class__)
        if not isinstance(self.type, type):
            raise TypeAttributeTypeError(self.__class__)
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
        return self.value

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
            raise TypeAttributeNotImplementedError(self.__class__)
        if not isinstance(self.type, type):
            raise TypeAttributeTypeError(self.__class__)

        if not isinstance(values, list):
            raise SettingTypeError(list, type(values))

        self.value = list()

        if self.type not in self.primitive:
            for idx, item in enumerate(values):
                try:
                    self.value.append(self.type(item))
                except SettingErrorMessage as e:
                    raise SettingErrorMessage(f"[{idx}]", e)
                except SettingTypeError as e:
                    raise SettingErrorMessage(f"[{idx}]", original_error=e)
                except SettingRangeTypeError as e:
                    raise SettingErrorMessage(f"[{idx}]", original_error=e)
                except SettingRangeKeyError as e:
                    raise SettingErrorMessage(f"[{idx}]", original_error=e)
                except ConsistencyError as e:
                    raise SettingErrorMessage(f"[{idx}]", original_error=e)
        else:
            for idx, item in enumerate(values):
                try:
                    if not isinstance(item, self.type):
                        raise SettingTypeError(self.type, type(item))
                    self.value.append(item)
                except SettingStringSelectionError as e:
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
            raise TypeAttributeNotImplementedError(self.__class__)
        if not isinstance(self.type, type):
            raise TypeAttributeTypeError(self.__class__)

        if not isinstance(values, dict):
            raise SettingTypeError(dict, type(values))

        self.value = dict()

        if self.type not in self.primitive:
            for key, value in values.items():
                try:
                    self.value[key] = self.type(value)
                except SettingErrorMessage as e:
                    raise SettingErrorMessage(key, e)
                except SettingRangeTypeError as e:
                    raise SettingErrorMessage(key, original_error=e)
                except SettingRangeKeyError as e:
                    raise SettingErrorMessage(key, original_error=e)
                except SettingStringSelectionError as e:
                    raise SettingErrorMessage(key, original_error=e)
                except ConsistencyError as e:
                    raise SettingErrorMessage(key, original_error=e)
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


class StringSelection(Terminus):
    
    @property
    def get(self):
        return self.value

    def distribute(self, value):
        if not hasattr(self, "options"):
            raise OptionsAttributeNotImplementedError(self.__class__)
        if not isinstance(self.options, list):
            raise OptionsAttributeTypeError(self.__class__)
        if not isinstance(value, str):
            raise SettingTypeError(str, type(value))
        elif value not in self.options:
            raise SettingStringSelectionError(self.options)
        else:
            self.value = value


class Number(Terminus):

    @property
    def is_range(self):
        return self._range
    
    @property
    def match(self):
        return self._match

    def distribute(self, value):
        if not hasattr(self, "type"):
            raise TypeAttributeNotImplementedError(self.__class__)
        if not isinstance(self.type, type):
            raise TypeAttributeTypeError(self.__class__)

        if type(value) is self.type:
            self.__value(value)
        elif type(value) is dict and "array" in value:
            self.__array(value)
        elif type(value) is dict:
            self.__range(value)
        else:
            raise SettingTypeError(
        f"{self.type} || {{'array': [{self.type}]}} || "
        f"{{'min': {self.type}, 'max': {self.type}, 'num': {int}}}",
        type(value))
    
    def __value(self, value):
        self.value = value
        self._range = False
        self._match = None
    
    def __array(self, value: dict):
        for item in value["array"]:
            if not isinstance(item, self.type):
                raise SettingTypeError(self.type, type(item))
        self.value = value["array"]
        self._range = True
        try:
            self._match = value["match"]
        except KeyError:
            self._match = None

    
    def __range(self, value: dict):
        try:
            if not isinstance(value["min"], self.type):
                raise SettingRangeTypeError("min", self.type)
        except KeyError:
            raise SettingRangeKeyError("min")
        try:
            if not isinstance(value["max"], self.type):
                raise SettingRangeTypeError("max", self.type)
        except KeyError:
            raise SettingRangeKeyError("max")
        try:
            if not isinstance(value["num"], int):
                raise SettingRangeTypeError('num', int)
        except KeyError:
            raise SettingRangeKeyError("num")
        self.value = list(linspace(value['min'],
                                   value['max'],
                                   abs(value['num'])))
        self._range = True
        try:
            self._match = value["match"]
        except KeyError:
            self._match = None

    
    def lower_bound(self, value):
        if isinstance(self.value, self.type):
            if self.value < value:
                raise ValueError(f"must be >= {value}")
        elif isinstance(self.value, list):
            for item in self.value:
                if item < value:
                    raise ValueError(f"must be >= {value}")
        elif isinstance(self.value, dict):
            if self.value["min"] < value:
                raise ValueError(f"must be >= {value}")
            if self.value["max"] < value:
                raise ValueError(f"must be >= {value}")
    
    def upper_bound(self, value):
        if isinstance(self.value, self.type):
            if self.value > value:
                raise ValueError(f"must be <= {value}")
        elif isinstance(self.value, list):
            for item in self.value:
                if item > value:
                    raise ValueError(f"must be <= {value}")
        elif isinstance(self.value, dict):
            if self.value["min"] > value:
                raise ValueError(f"must be <= {value}")
            if self.value["max"] > value:
                raise ValueError(f"must be <= {value}")


class ComputationalSpace:

    def __init__(self, setting: Type[Settings], restrict: Dict[str, str]):
        self.setting = setting
        self.restrict = restrict
        self.addresses = list()
        self.values = list()
        self.matched = dict()
        self.unmatched = list()
        self.space = list()
        self.explore(self.setting, list())
        self.build_space()

    def get_by_address(self, root: dict, address: List[str]):
        return reduce(operator.getitem, address, root)

    def set_by_address(self, root: dict, address, value):
        self.get_by_address(root, address[:-1])[address[-1]] = value

    def explore(self, root, path, restrict = None):
        if issubclass(type(root), List):
            branch = enumerate(root.value)
        elif issubclass(type(root), Dict):
            branch = root.items()
        elif issubclass(type(root), Settings):
            branch = [(k, v) for k, v in root.__dict__.items() if "__" not in k]
        else:
            branch = list()
        if restrict:
            branch = [(k, v) for k, v in branch if k == restrict]
        for key, item in branch:
            new_path = deepcopy(path)
            if issubclass(type(item), Number):
                if item.is_range:
                    new_path.append(key)
                    if item.match:
                        if item.match in self.matched:
                            self.matched[item.match]["addresses"].append(new_path)
                            self.matched[item.match]["values"].append(item.get)
                        else:
                            self.matched[item.match] = {
                                "addresses": [new_path],
                                "values": [item.get] 
                            }
                    else:
                        self.unmatched.append(new_path)
                        self.addresses.append(new_path)
                        self.values.append(item.get)
            else:
                new_path.append(key)
                for k, v in self.restrict.items():
                    new_restrict = v if key == k else None
                    break
                self.explore(item, new_path, new_restrict)
   
    def build_space(self):
        for match, items in self.matched.items():
            self.addresses += items["addresses"]
            if len({len(i) for i in items["values"]}) != 1:
                warnings.warn(f"ranges with match id '{match}' have unequal "
                              f"length. Zipped to shortest.")
            self.values.append(list(zip(*items["values"])))
        for batch in itertools.product(*self.values):
            flat_batch = list()
            for item in batch:
                if isinstance(item, Iterable):
                    for subitem in item:
                        flat_batch.append(subitem)
                else:
                    flat_batch.append(item)
            rv = deepcopy(self.setting.__source__)
            for address, value in zip(self.addresses, flat_batch):
                self.set_by_address(rv, address, float(value))
            self.space.append(type(self.setting)(rv))

    def __getitem__(self, indices):
        if isinstance(indices, tuple):
            if len(indices) > len(self.values):
                raise IndexError(f"too many indices for array {self.shape}")
            for idx, item in enumerate(indices):
                if not isinstance(item, int):
                    raise IndexError("only integers are valid when accessing arrays")
                if not 0 <= item < self.shape[idx]:
                    raise IndexError(f"index {item} is out of bounds for axis "
                                     f"{idx} with size {self.shape[idx]}")
            index = 0
            for idx, item in enumerate(indices):
                index += item * int(prod([len(v) for v in self.values[idx + 1:]]))
        elif isinstance(indices, int):
            if len(self.values) > 1:
                raise IndexError(f"too many indices for array {self.shape}")
            if not 0 <= indices < self.shape[0]:
                raise IndexError(f"index {item} is out of bounds for axis {0} "
                                 f"with size {self.shape[0]}")
            index = indices
        else:
            raise IndexError("only integers are valid when accessing arrays")

        return self.space[index]

    @property
    def shape(self):
        if len(self.values):
            return tuple((len(v) for v in self.values))
        else:
            return (1,)
        
    @property
    def zero(self) -> Union[Type[Settings], None]:
        if len(self.space) == 1:
            return self.space[0]
        else:
            return None
    
    @property
    def axes(self):
        for item, space in zip(self.addresses, self.values):
            print(self.build_path(item), space)

    def build_path(self, elements: List[str]):
        rv = ""
        for item in elements:
            rv += f"{item} -> "
        return rv[:-4]
    
    def cout_summary(self):
        from textwrap import fill
        rv = ""
        rv += f"Computational space dimensions: " + f"{self.shape}\n"\
                .replace(",", " x")\
                .replace(")", "")\
                .replace("(", "")
        axis = 0
        for idx, item in enumerate(self.unmatched):
            rv += f"\naxis: {axis}:"
            rv += "\n"
            rv += f"\t{self.build_path(item)}"
            rv += "\n"
            rv += fill(f"\tvalues:  {self.values[idx]}\n",
                       width=70,
                       subsequent_indent="\t")
            axis += 1
        rv += "\n"
        for key, value in self.matched.items():
            rv += f"\naxis: {axis}:"
            rv += "\n"
            rv += f"\tmatch_id: {key}"
            for idx, item in enumerate(value["addresses"]):
                rv += "\n"
                rv += f"\t{self.build_path(item)}"
            rv += "\n"
            rv += fill(f"\tvalues: {list(zip(*value['values']))}",
                       width=70,
                       subsequent_indent="\t\t")
            axis += 1
        return rv
    
    def index(self, setting: Type[Settings]):
        linear_index = self.linear_index(setting) 
        return unravel_index(linear_index, self.shape)

    def linear_index(self, setting: Type[Settings]):
        return self.space.index(setting)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class SettingRangeKeyError(Error):
    """The exception raised when a :class:`~.Number` instance is missing an 
    entry in a range specification.

    """
    def __init__(self, key: str):
        """The constructor for the :class:`SettingRangeKeyError` class.

        """
        self.msg = f"No '{key}' parameter provided for range"


class SettingRangeTypeError(Error):
    """The exception raised when a :class:`~.Number` instance is passed an
    incorrect type in a range specification. 

    """
    def __init__(self, key: str, expected_type: T):
        """The constructor for the :class:`SettingRangeTypeError` class.

        """
        self.msg = f"The '{key}' parameter was not {expected_type}"


class SettingStringSelectionError(Error):
    """The exception raised when a :class:`~.StringSelection` instance is
    passed an invalid value.

    """
    def __init__(self, allowed: List[str]):
        """The constructor for the :class:`SettingRangeTypeError` class.

        """
        self.msg = f"must be one of {allowed}"


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


class OptionsAttributeNotImplementedError(Error):
    """The exception raised when the `options` attribute has not been defined
    in a StringSelection derived class.

    """
    def __init__(self, derived_class):
        """The constructor for the :class::`OptionsAttributeNotImplementedError`
        class.

        Parameters
        ----------
        derived_class : :obj:`type`
            The name of the derived class that raised the exception.
        
        """
        self.msg = f"The {derived_class} class does not have a self.options"\
                   f"attribute defined in its constructor."
  

class OptionsAttributeTypeError(Error):
    """The exception raised when the value of the `options` attribute defined
    in a StringSelection derived class is not a :obj:`list`, or one of its
    elements is not a string.

    """
    def __init__(self, derived_class):
        """The constructor for the :class::`OptionsAttributeTypeError`
        class.

        Parameters
        ----------
        derived_class : :obj:`type`
            The name of the derived class that raised the exception.
        
        """
        self.msg = f"The {derived_class} class self.options attribute's value "\
                   f"is not of type {list}, or one of its elements is not of"\
                   f" type {str}"
        super().__init__(self.msg)
        

class TypeAttributeNotImplementedError(Error):
    """The exception raised when the `type` attribute has not been defined
    in a Terminus, Number, List, or Dict derived class.

    """
    def __init__(self, derived_class):
        """The constructor for the :class::`TypeAttributeNotImplementedError`
        class.

        Parameters
        ----------
        derived_class : :obj:`type`
            The name of the derived class that raised the exception.
        
        """
        self.msg = f"The {derived_class} class does not have a self.type "\
                   f"attribute defined in its constructor."
        super().__init__(self.msg)
 

class TypeAttributeTypeError(Error):
    """The exception raised when the value of the `type` attribute defined
    in a Terminus, Number, List, or Dict derived class is not a :obj:`type`.

    """
    def __init__(self, derived_class):
        """The constructor for the :class::`TypeAttributeTypeError`
        class.

        Parameters
        ----------
        derived_class : :obj:`type`
            The name of the derived class that raised the exception.
        
        """
        self.msg = f"The {derived_class} class self.type attribute's value is"\
                   f" not of type `type`."
        super().__init__(self.msg)


class ConsistencyError(Error):
    """The exception raised if a consistency check is failed.

    """

    def __init__(self, msg: str):
        """The constructor for the :class:`ConsistencyError` class

        Parameters
        ----------

        """
        self.msg = msg
        super().__init__(msg)

