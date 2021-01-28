import random
import re
import string

_ITERABLE_SINGLE_VALUES = dict, str, bytes


def arglist_to_dict(arglist):
    """Convert a list of arguments like ['arg1=val1', 'arg2=val2', ...] to a
    dict
    """
    return dict(x.split('=', 1) for x in arglist)


def regex(x):
    if isinstance(x, str):
        return re.compile(x)
    return x


def unique(list_, key=lambda x: x):
    """efficient function to uniquify a list preserving item order"""
    seen = set()
    result = []
    for item in list_:
        seenkey = key(item)
        if seenkey in seen:
            continue
        seen.add(seenkey)
        result.append(item)
    return result


def arg_to_iter(arg):
    """Convert an argument to an iterable. The argument can be a None, single
    value, or an iterable.

    Exception: if arg is a dict, [arg] will be returned
    """
    if arg is None:
        return []
    elif not isinstance(arg, _ITERABLE_SINGLE_VALUES) and hasattr(
            arg, '__iter__'):
        return arg
    else:
        return [arg]


def gen_random_str(length):
    return "".join(
        random.sample(string.ascii_lowercase + string.digits, length))


class LazyProperty:
    """
    延迟加载实例属性,只会在第一次调用时才会初始化
    """
    def __init__(self, method):
        self.method = method
        self.method_name = method.__name__
        print(f'function overridden:{self.method}')
        print(f'function name:{self.method_name}')

    def __get__(self, obj, cls):
        if not obj:
            return None
        value = self.method(obj)
        print(f'value:{value}')
        setattr(obj, self.method_name, value)
        return value
