"""Ground types for various mathematical domains in Diofant. """

__all__ = ()

import builtins
import fractions

import mpmath.libmp as mlib

from ..core.compatibility import HAS_GMPY
from ..core.numbers import Float as DiofantReal  # noqa: F401
from ..core.numbers import Integer as DiofantInteger  # noqa: F401
from ..core.numbers import Rational as DiofantRational  # noqa: F401
from ..core.numbers import igcd as python_gcd  # noqa: F401
from ..core.numbers import igcdex as python_gcdex  # noqa: F401
from ..core.numbers import ilcm as python_lcm  # noqa: F401


PythonInteger = builtins.int
PythonReal = builtins.float
PythonComplex = builtins.complex
PythonRational = fractions.Fraction


if HAS_GMPY == 'gmpy':
    from gmpy2 import (  # noqa: N812
        mpz as GMPYInteger,
        mpq as GMPYRational,
        fac as gmpy_factorial,
        numer as gmpy_numer,
        denom as gmpy_denom,
        gcdext as gmpy_gcdex,
        gcd as gmpy_gcd,
        lcm as gmpy_lcm,
        isqrt as gmpy_sqrt,
        qdiv as gmpy_qdiv)
elif HAS_GMPY == 'gmpy_ctypes':
    from gmpy_ctypes import (mpz as GMPYInteger,  # noqa: N812
                             mpq as GMPYRational,
                             gcd as gmpy_gcd,
                             lcm as gmpy_lcm,
                             gcdext as gmpy_gcdex)

    def gmpy_factorial(x):
        from gmpy_ctypes import fac
        return fac(int(x))

    def gmpy_numer(x):
        return x.numerator

    def gmpy_denom(x):
        return x.denominator

    def gmpy_sqrt(x):
        return GMPYInteger(int(x**GMPYRational(1, 2)))

    def gmpy_qdiv(x, y):
        return GMPYRational(x, y)
else:
    class GMPYInteger:
        def __init__(self, obj):
            pass

    class GMPYRational:
        def __init__(self, obj):
            pass

    gmpy_factorial = None
    gmpy_numer = None
    gmpy_denom = None
    gmpy_gcdex = None
    gmpy_gcd = None
    gmpy_lcm = None
    gmpy_sqrt = None
    gmpy_qdiv = None


def python_sqrt(n):
    return int(mlib.isqrt(n))


def python_factorial(n):
    return int(mlib.ifac(n))
