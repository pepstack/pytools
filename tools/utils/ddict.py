# https://stackoverflow.com/questions/13520421/recursive-dotdict
# last: 2021-03-18: Vero 1

class dotdict(dict):
    """
    Attribute Dictionary.

    Enables getting/setting/deleting dictionary keys via attributes.
    Getting/deleting a non-existent key via attribute raises `AttributeError`.
    Objects are passed to `__convert` before `dict.__setitem__` is called.

    This class rebinds `__setattr__` to call `dict.__setitem__`. Attributes
    will not be set on the object, but will be added as keys to the dictionary.
    This prevents overwriting access to built-in attributes. Since we defined
    `__getattr__` but left `__getattribute__` alone, built-in attributes will
    be returned before `__getattr__` is called. Be careful::

        >>> a = dotdict()
        >>> a['key'] = 'value'
        >>> a.key
        'value'
        >>> a['keys'] = 'oops'
        >>> a.keys
        <built-in method keys of dotdict object at 0xabcdef123456>

        d = {
            "author": "zhangliang"
        }
        ad = dotdict(d)
        print d['author']
        print ad.author

    Use `'key' in a`, not `hasattr(a, 'key')`, as a consequence of the above.
    """
    def __init__(self, *args, **kwargs):
        # We trust the dict to init itself better than we can.
        dict.__init__(self, *args, **kwargs)
        # Because of that, we do duplicate work, but it's worth it.
        for k, v in self.items():
            self.__setitem__(k, v)

    def __getattr__(self, k):
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            # Maintain consistent syntactical behaviour.
            raise AttributeError(
                "'dotdict' object has no attribute '" + str(k) + "'"
            )

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, dotdict.__convert(v))

    __setattr__ = __setitem__

    def __delattr__(self, k):
        try:
            dict.__delitem__(self, k)
        except KeyError:
            raise AttributeError(
                "'dotdict' object has no attribute '" + str(k) + "'"
            )

    @staticmethod
    def __convert(o):
        """
        Recursively convert `dict` objects in `dict`, `list`, `set`, and
        `tuple` objects to `dotdict` objects.
        """
        if isinstance(o, dict):
            o = dotdict(o)
        elif isinstance(o, list):
            o = list(dotdict.__convert(v) for v in o)
        elif isinstance(o, set):
            o = set(dotdict.__convert(v) for v in o)
        elif isinstance(o, tuple):
            o = tuple(dotdict.__convert(v) for v in o)
        return o

    @staticmethod
    def __revert(v):
        if isinstance(v, tuple):
            v = list(v)
        elif isinstance(v, set):
            v = list(v)

        if isinstance(v, list):
            vl = []
            for el in v:
                vl.append(dotdict.__revert(el))
            return vl
        elif str(type(v)).find('ddict.dotdict') != -1:
            return v.to_dict()
        else:
            return v

    def to_dict(self):
        d = {}
        for k, v in self.items():
            d[k] = dotdict.__revert(v)
        return d
