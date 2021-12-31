from enum import Enum
import sys


# === Argument reading ====


class ArgType(Enum):
    FLAG = 0
    VALUE = 1
    UNLEASHED = 2


class ArgDef:

    def __init__(self, get_func, keys: list, required: bool, desc: str):
        f = get_func
        if isinstance(get_func, property):
            f = get_func.fget

        arg_type = ArgType.VALUE
        prop_type = str
        if len(keys) == 0:
            arg_type = ArgType.UNLEASHED
            prop_type = list
        elif "return" in f.__annotations__.keys():
            prop_type = f.__annotations__["return"]
            if prop_type == bool:
                arg_type = ArgType.FLAG
                if required:
                    raise ValueError(f"Program Error: Argument '{f.__name__}'"
                                     " is a flag and flags are not allowed"
                                     " to be required.")

        self._arg_type = arg_type
        self._prop_type = prop_type
        self._name = f.__name__
        self._keys = keys
        self._required = required
        self._desc = desc
        self._defined = False

    @property
    def arg_type(self) -> ArgType:
        return self._arg_type

    @property
    def prop_type(self):
        return self._prop_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def keys(self) -> list:
        return self._keys

    @property
    def required(self) -> bool:
        return self._required

    @property
    def desc(self) -> str:
        return self._desc

    @property
    def defined(self) -> bool:
        return self._defined

    @defined.setter
    def defined(self, value: bool):
        self._defined = value

    def __str__(self):
        head = f"{self.name} -> {self.prop_type.__name__}"
        tail = ""
        if self.arg_type == ArgType.FLAG:
            tail = " <FLAG>"

        return head + tail


def _default_value(arg_def: ArgDef):
    if arg_def.arg_type == ArgType.FLAG:
        return False
    elif arg_def.arg_type == ArgType.UNLEASHED:
        return []
    else:
        if arg_def.prop_type == int:
            return 0
        if arg_def.prop_type == float:
            return 0.0
        elif arg_def.prop_type == list:
            return []
        else:
            return None


def _cast_value(value: str, arg_def: ArgDef):
    prop_type = arg_def.prop_type
    if prop_type == str:
        return value
    if prop_type == list:
        return value.split(",")

    try:
        res = prop_type(value)
        return res
    except Exception as err:
        raise ValueError(f"Error: argument {arg_def.name} must be of type"
                         f" {prop_type}. {err}")


def _read_arg_into(args, arg_def, argv, idx: int) -> int:
    read = 0
    if argv[idx] in arg_def.keys:
        if arg_def.arg_type == ArgType.FLAG:
            args.__setattr__(arg_def.name, True)
            arg_def.defined = True
            read = 1
        else:
            if len(argv) > idx + 1:
                value = argv[idx + 1]
                safe_value = _cast_value(value, arg_def)
                args.__setattr__(arg_def.name, safe_value)
                arg_def.defined = True
                read = 2
            else:
                read = 1

    return read


def _validate_args(arg_definitions):
    required_undefined = [
        arg_def
        for arg_def in arg_definitions
        if arg_def.required and not arg_def.defined
    ]
    if len(required_undefined) > 0:
        names = list(map(lambda ad: ad.name, required_undefined))
        raise ValueError(f"Error: arguments {','.join(names)} are required")


class Args(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def arg(keys, required: bool = False, desc: str = ""):
    def arg_func(get_func):
        return ArgDef(get_func, keys, required, desc)

    return arg_func


def unleashed_args(desc: str = ""):
    def arg_func(get_func):
        return ArgDef(get_func, [], False, desc)

    return arg_func


def auto_help(arg_class):
    arg_definitions = get_arg_definitions(arg_class)
    for arg_def in arg_definitions:
        if arg_def.arg_type != ArgType.UNLEASHED:
            print(f"{' | '.join(arg_def.keys)}\t\t{arg_def.desc}")


def get_arg_definitions(arg_class):
    res = []

    properties = [
        method
        for method in dir(arg_class)
        if method.startswith("__") is False
    ]

    for prop in properties:
        arg_def = getattr(arg_class, prop)
        res.append(arg_def)

    return res


def get_args_obj(arg_class, argv: list = None):
    args = Args()

    # init default values
    unleashed_prop = None
    arg_definitions = get_arg_definitions(arg_class)

    for arg_def in arg_definitions:
        prop = arg_def.name

        if arg_def.arg_type == ArgType.UNLEASHED:
            unleashed_prop = prop
            args.__setattr__(prop, [])
        else:
            default_value = _default_value(arg_def)
            args.__setattr__(prop, default_value)

    # assign passed values
    if argv is None:
        argv = sys.argv

    argc = len(argv)

    idx = 1
    while idx < argc:
        move = 0
        for arg_def in arg_definitions:
            move = _read_arg_into(args, arg_def, argv, idx)
            if move > 0:
                break

        if move == 0:
            if unleashed_prop:
                args.__getattr__(unleashed_prop).append(argv[idx])
            idx += 1
        else:
            idx += move

    _validate_args(arg_definitions)

    return args
