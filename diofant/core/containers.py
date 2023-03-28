"""Module for Diofant containers

(Diofant objects that store other Diofant objects)

The containers implemented in this module are subclassed to Basic.
They are supposed to work seamlessly within the Diofant framework.
"""

from collections.abc import Mapping

from .basic import Basic
from .compatibility import as_int, iterable
from .sympify import converter, sympify


class Tuple(Basic):
    """
    Wrapper around the builtin tuple object

    The Tuple is a subclass of Basic, so that it works well in the
    Diofant framework.  The wrapped tuple is available as self.args, but
    you can also access elements or slices with [:] syntax.

    >>> Tuple(a, b, c)[1:]
    (b, c)
    >>> Tuple(a, b, c).subs({a: d})
    (d, b, c)

    """

    def __new__(cls, *args):
        args = (sympify(arg) for arg in args)
        return super().__new__(cls, *args)

    def __getitem__(self, i):
        if isinstance(i, slice):
            indices = i.indices(len(self))
            return Tuple(*[self.args[j] for j in range(*indices)])
        return self.args[i]

    def __len__(self):
        return len(self.args)

    def __contains__(self, item):
        return item in self.args

    def __iter__(self):
        return iter(self.args)

    def __add__(self, other):
        if isinstance(other, Tuple):
            return Tuple(*(self.args + other.args))
        if isinstance(other, tuple):
            return Tuple(*(self.args + other))
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Tuple):
            return Tuple(*(other.args + self.args))
        if isinstance(other, tuple):
            return Tuple(*(other + self.args))
        return NotImplemented

    def __mul__(self, other):
        try:
            n = as_int(other)
        except ValueError as exc:
            raise TypeError("Can't multiply sequence by non-integer "
                            f"of type '{type(other)!s}'") from exc
        return self.func(*(self.args*n))

    __rmul__ = __mul__

    def __eq__(self, other):
        if isinstance(other, Basic):
            return super().__eq__(other)
        return self.args == other

    def __hash__(self):
        return hash(self.args)

    def _to_mpmath(self, prec):
        return tuple(a._to_mpmath(prec) for a in self.args)

    def __lt__(self, other):
        return sympify(self.args < other.args)

    def __le__(self, other):
        return sympify(self.args <= other.args)

    # XXX: Basic defines count() as something different, so we can't
    # redefine it here. Originally this lead to cse() test failure.
    def tuple_count(self, value):
        """T.count(value) -> int -- return number of occurrences of value."""
        return self.args.count(value)

    def index(self, value, start=None, stop=None):
        """Return first index of value.

        Raises ValueError if the value is not present.

        """
        # XXX: One would expect:
        #
        # return self.args.index(value, start, stop)
        #
        # here. Any trouble with that? Yes:
        #
        # >>> [1].index(1, None, None)
        # Traceback (most recent call last):
        #   File "<stdin>", line 1, in <module>
        # TypeError: slice indices must be integers or None or have an __index__ method
        #
        # See: http://bugs.python.org/issue13340

        if start is None and stop is None:
            return self.args.index(value)
        if stop is None:
            return self.args.index(value, start)
        return self.args.index(value, start, stop)


converter[tuple] = lambda tup: Tuple(*tup)


def tuple_wrapper(method):
    """
    Decorator that converts any tuple in the function arguments into a Tuple.

    The motivation for this is to provide simple user interfaces.  The user can
    call a function with regular tuples in the argument, and the wrapper will
    convert them to Tuples before handing them to the function.

    >>> def f(*args):
    ...     return args
    >>> g = tuple_wrapper(f)

    The decorated function g sees only the Tuple argument:

    >>> g(0, (1, 2), 3)
    (0, (1, 2), 3)

    """
    def wrap_tuples(*args, **kw_args):
        newargs = []
        for arg in args:
            if type(arg) is tuple:
                newargs.append(Tuple(*arg))
            else:
                newargs.append(arg)
        return method(*newargs, **kw_args)
    return wrap_tuples


class Dict(Basic):
    """
    Wrapper around the builtin dict object

    The Dict is a subclass of Basic, so that it works well in the
    Diofant framework.  Because it is immutable, it may be included
    in sets, but its values must all be given at instantiation and
    cannot be changed afterwards.  Otherwise it behaves identically
    to the Python dict.

    >>> D = Dict({1: 'one', 2: 'two'})
    >>> for key in D:
    ...     if key == 1:
    ...         print(f'{key} {D[key]}')
    1 one

    The args are sympified so the 1 and 2 are Integers and the values
    are Symbols. Queries automatically sympify args so the following work:

    >>> 1 in D
    True
    >>> D.has('one')  # searches keys and values
    True
    >>> 'one' in D  # not in the keys
    False
    >>> D[1]
    one

    """

    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], (dict, Dict)):
            items = [Tuple(k, v) for k, v in args[0].items()]
        elif iterable(args) and all(len(arg) == 2 for arg in args):
            items = [Tuple(k, v) for k, v in args]
        else:
            raise TypeError('Pass Dict args as Dict((k1, v1), ...) or Dict({k1: v1, ...})')
        elements = frozenset(items)
        obj = Basic.__new__(cls, elements)
        obj.elements = elements
        obj._dict = dict(items)  # In case Tuple decides it wants to sympify
        return obj

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]."""
        return self._dict[sympify(key)]

    def __setitem__(self, key, value):
        raise NotImplementedError('Diofant Dicts are Immutable')

    @property
    def args(self):
        """Returns a tuple of arguments of 'self'.

        See Also
        ========

        diofant.core.basic.Basic.args

        """
        return tuple(self.elements)

    def items(self):
        """Returns a set-like object providing a view on Dict's items."""
        return self._dict.items()

    def keys(self):
        """Returns a set-like object providing a view on Dict's keys."""
        return self._dict.keys()

    def values(self):
        """Returns a set-like object providing a view on Dict's values."""
        return self._dict.values()

    def __iter__(self):
        """x.__iter__() <==> iter(x)."""
        return iter(self._dict)

    def __len__(self):
        """x.__len__() <==> len(x)."""
        return self._dict.__len__()

    def get(self, key, default=None):
        """Return the value for key if key is in the dictionary, else default."""
        return self._dict.get(sympify(key), default)

    def __contains__(self, key):
        """D.__contains__(k) -> True if D has a key k, else False."""
        return sympify(key) in self._dict

    def __lt__(self, other):
        return sympify(self.args < other.args)

    @property
    def _sorted_args(self):
        from ..utilities import default_sort_key
        return tuple(sorted(self.args, key=default_sort_key))


Mapping.register(Dict)


import operator
import itertools

class Stream(object):
    """
    Stream container

    Examples
    ========

    >>> from diofant.core.containers import Stream
    >>> from diofant import Integer, I
    >>> from diofant.abc import x
    >>> def exp_gen(q):
    ...     def gen():
    ...         i, r = Integer(0), Integer(1)
    ...         while True:
    ...             yield r
    ...             i += 1
    ...             r *= q/i
    ...     return gen()
    >>> exp_s = Stream(exp_gen(x))
    >>> exp_s1 = Stream(exp_gen(I*x))
    >>> exp_s2 = Stream(exp_gen(-I*x))
    >>> list(exp_s[0:4])
    [1, x, x**2/2, x**3/6]
    >>> sin_s = (exp_s1 - exp_s2)/(2*I)
    >>> list(sin_s[1:10:2])
    [x, -x**3/6, x**5/120, -x**7/5040, x**9/362880]
    >>> cos_s = (exp_s1 + exp_s2)/Integer(2)
    >>> list((sin_s*cos_s)[0:10])
    [0, x, 0, -2*x**3/3, 0, 2*x**5/15, 0, -4*x**7/315, 0, 2*x**9/2835]

    """

    class _StreamIterator(object):

        def __init__(self, stream):
            self._stream = stream
            self._position = -1 # not started yet

        def __next__(self):
            self._position += 1
            if len(self._stream._collection) > self._position or self._stream._fill_to(self._position):
                return self._stream._collection[self._position]

            raise StopIteration()
        next = __next__

    def __init__(self, origin=[]):
        self._collection = []
        self._last = -1 # not started yet
        self._origin = iter(origin) if origin else []

    def _fill_to(self, index):
        while self._last < index:
            try:
                n = next(self._origin)
            except StopIteration:
                return False

            self._last += 1
            self._collection.append(n)

        return True

    def __iter__(self):
        return self._StreamIterator(self)

    def __getitem__(self, index):
        from numbers import Integral
        if isinstance(index, Integral):
            if index < 0:
                raise TypeError("Invalid argument type")
            self._fill_to(index)
            return self._collection[index]
        elif isinstance(index, slice):
            if index.step == 0:
                raise ValueError("Step must not be 0")
            if not index.stop:
                return self.__class__(map(self.__getitem__, itertools.islice(index.start, index.stop, index.step or 1)))
            return self.__class__(map(self.__getitem__, range(index.start, index.stop, index.step or 1)))
        else:
            raise TypeError("Invalid argument type")

    # TODO: move this out

    def __add__(self, other):
        return self.__class__(map(operator.add, self, other))

    def __sub__(self, other):
        from . import Integer
        return self + other*Integer(-1)

    def __mul__(self, other):
        from . import Number, Symbol, Basic, Integer
        if isinstance(other, Basic):
            return self.__class__(map(lambda x: x*other, self))
        def mul():
            k = 0
            while True:
                p = Integer(0)
                for i, a in enumerate(self):
                    p += a*other[k - i]
                    if i >= k:
                        break
                yield p
                k += 1
        return self.__class__(mul())

    def __truediv__(self, other):
        from . import Basic, Integer
        if isinstance(other, Basic):
            return self*(1/other)
        def invert_unit_series(s):
            r = Integer(1)
            for t in s:
                yield r
                r = Integer(-1)*r*t
        c = 1/other[0]
        return self*invert_unit_series(other*c)*c
    __div__ = __truediv__
