"""Limit computation tests."""

import itertools

import pytest

from diofant import (E, Ei, Float, Function, I, Integral, Lambda, Limit, O,
                     Piecewise, PoleError, Rational, Reals, RootSum, Sum,
                     Symbol, acos, acosh, acoth, acsc, arg, asin, atan,
                     besselk, binomial, cbrt, ceiling, cos, cosh, cot, diff,
                     digamma, elliptic_e, elliptic_k, erf, erfc, erfi, exp,
                     factorial, false, floor, gamma, hyper, integrate, limit,
                     log, lowergamma, nan, oo, pi, polygamma, re, root, sign,
                     simplify, sin, sinh, sqrt, subfactorial, symbols, tan,
                     tanh, true)
from diofant.abc import a, b, c, k, n, x, y, z
from diofant.calculus.limits import heuristics


__all__ = ()


def test_basic1():
    assert limit(x, x, -oo) == -oo
    assert limit(x**2, x, -oo) == oo
    assert limit(x*log(x), x, 0) == 0
    assert limit(x - x**2, x, oo) == -oo
    assert limit((1 + x)**(1 + sqrt(2)), x, 0) == 1
    assert limit((1 + x)**oo, x, 0) == oo
    assert limit((1 + x)**oo, x, 0, dir=1) == 0
    assert limit((1 + x + y)**oo, x, 0, dir=1) == (1 + y)**oo
    assert limit(y/x/log(x), x, 0) == -oo*sign(y)
    assert limit(cos(x + y)/x, x, 0) == sign(cos(y))*oo
    limit(Sum(1/x, (x, 1, y)) - log(y), y, oo)
    limit(Sum(1/x, (x, 1, y)) - 1/y, y, oo)
    assert limit(nan, x, -oo) == nan
    assert limit(O(2, x)*x, x, nan) == nan
    assert limit(O(x), x, 0) == 0
    assert limit(O(1, x), x, 0) != 1
    assert limit(sin(O(x)), x, 0) == 0
    assert limit(1/(x - 1), x, 1) == oo
    assert limit(1/(x - 1), x, 1, dir=1) == -oo
    assert limit(1/(5 - x)**3, x, 5) == -oo
    assert limit(1/(5 - x)**3, x, 5, dir=1) == oo
    assert limit(1/sin(x), x, pi) == -oo
    assert limit(1/sin(x), x, pi, dir=1) == oo
    assert limit(1/cos(x), x, pi/2) == -oo
    assert limit(1/cos(x), x, pi/2, dir=1) == oo
    assert limit(1/tan(x**3), x, cbrt(2*pi)) == oo
    assert limit(1/tan(x**3), x, cbrt(2*pi), dir=1) == -oo
    assert limit(1/cot(x)**3, x, 3*pi/2) == -oo
    assert limit(1/cot(x)**3, x, 3*pi/2, dir=1) == oo

    # approaching 0
    # from dir=-1
    assert limit(1 + 1/x, x, 0) == oo
    # from dir=1
    # Add
    assert limit(1 + 1/x, x, 0, dir=1) == -oo
    # Pow
    assert limit(x**(-2), x, 0, dir=1) == oo
    assert limit(x**(-3), x, 0, dir=1) == -oo
    assert limit(1/sqrt(x), x, 0, dir=1) == (-oo)*I
    assert limit(x**2, x, 0, dir=1) == 0
    assert limit(sqrt(x), x, 0, dir=1) == 0
    assert limit(x**-pi, x, 0, dir=1) == oo*sign((-1)**(-pi))
    assert limit((1 + cos(x))**oo, x, 0) == oo

    assert limit(x**2, x, 0, dir=Reals) == 0
    assert limit(exp(x), x, 0, dir=Reals) == 1

    pytest.raises(PoleError, lambda: limit(1/x, x, 0, dir=Reals))

    # issue diofant/diofant#74
    assert limit(sign(log(1 - 1/x)), x, oo) == -1

    # issue sympy/sympy#8166
    f = Function('f')
    assert limit(f(x), x, 4) == Limit(f(x), x, 4)

    assert limit(exp(x), x, 0, dir=exp(I*pi/3)) == 1

    assert limit(sqrt(-1 + I*x), x, 0) == +I
    assert limit(sqrt(-1 + I*x), x, 0, dir=1) == -I
    assert limit(sqrt(-1 + I*x), x, 0, dir=exp(I*pi/3)) == -I

    assert limit(log(x + sqrt(x**2 + 1)), x, I) == I*pi/2
    assert limit(log(x + sqrt(x**2 + 1)), x, I, dir=1) == I*pi/2
    assert limit(log(x + sqrt(x**2 + 1)), x, I, dir=exp(I*pi/3)) == I*pi/2


def test_basic2():
    assert limit(x**x, x, 0) == 1
    assert limit((exp(x) - 1)/x, x, 0) == 1


def test_basic3():
    assert limit(1/x, x, 0) == oo
    assert limit(1/x, x, 0, dir=1) == -oo


def test_basic4():
    assert limit(2*x + y*x, x, 0) == 0
    assert limit(2*x + y*x, x, 1) == 2 + y
    assert limit(2*x**8 + y*x**(-3), x, -2) == 512 - y/8
    assert limit(sqrt(x + 1) - sqrt(x), x, oo) == 0
    assert integrate(1/(x**3 + 1), (x, 0, oo)) == 2*pi*sqrt(3)/9

    # coverage test
    assert limit(Piecewise((x, x > 1), (0, True)), x, -1) == 0

    # issue sympy/sympy#16714
    e = ((x**(x + 1) + (x + 1)**x)/x**(x + 1))**x
    assert limit(e, x, oo) == E**E

    # issue sympy/sympy#18492
    e1 = 2*sqrt(x)*Piecewise(((4*x - 2)/abs(sqrt(4 - 4*(2*x - 1)**2)),
                              4*x - 2 >= 0),
                             ((2 - 4*x)/abs(sqrt(4 - 4*(2*x - 1)**2)), True))
    e2 = Piecewise((x**2/2, x <= Rational(1, 2)), (x/2 - Rational(1, 8), True))
    e3 = Piecewise(((x - 9)/5, x < -1), ((x - 9)/5, x > 4),
                   (sqrt(abs(x - 3)), True))
    assert limit(e1, x, 0) == 1
    assert limit(e2, x, 0) == 0
    assert limit(e2, x, oo) == oo
    assert limit(e3, x, -1) == 2
    assert limit(e3, x, oo) == oo

    e4 = Piecewise((1, 0 < x), (0, True))

    assert limit(e4, x, 0, 1) == 0
    assert limit(e4, x, 0) == 1
    pytest.raises(PoleError, lambda: limit(e4, x, 0, Reals))

    e5 = Piecewise((1, 0 < x), (2, 1 < x), (0, True))

    assert limit(e5, x, oo) == 1
    assert limit(e5, x, 1, 1) == 1
    assert limit(e5, x, 1) == 1

    e6 = Limit(Piecewise((1, x > a), (0, True)), x, 0)
    assert e6.doit() == e6


def test_basic5():
    class MyFunction(Function):
        @classmethod
        def eval(cls, arg):
            if arg is oo:
                return nan
    assert limit(MyFunction(x), x, oo) == Limit(MyFunction(x), x, oo)

    assert limit(4/x > 8, x, 0) is true  # relational test
    assert limit(MyFunction(x) > 0, x, oo) == Limit(MyFunction(x) > 0, x, oo)

    # issue diofant/diofant#1217
    assert limit(x > 0, x, 0) is true
    assert limit(x > 0, x, 0, 1) is false

    # issue sympy/sympy#11833
    a = Symbol('a', positive=True)
    f = exp(x*(-a - 1)) * sinh(x)
    assert limit(f, x, oo) == 0

    assert limit(O(x), x, x**2) == Limit(O(x), x, x**2)


def test_basic6():
    # pull sympy/sympy#22491
    assert limit(1/asin(x), x, 0) == oo
    assert limit(1/asin(x), x, 0, dir=1) == -oo
    assert limit(1/sinh(x), x, 0) == oo
    assert limit(1/sinh(x), x, 0, dir=1) == -oo
    assert limit(log(1/x) + 1/sin(x), x, 0) == oo
    assert limit(log(1/x) + 1/x, x, 0) == oo

    # issue diofant/diofant#1262
    assert limit(I*exp(I*x)*log(exp(I*x)), x, -pi) == -pi


def test_sympyissue_3885():
    assert limit(x*y + x*z, z, 2) == x*(y + 2)


def test_Limit():
    assert Limit(sin(x)/x, x, 0) != 1
    assert Limit(sin(x)/x, x, 0).doit() == 1


def test_floor():
    assert limit(floor(x), x, -2) == -2
    assert limit(floor(x), x, -2, 1) == -3
    assert limit(floor(x), x, -1) == -1
    assert limit(floor(x), x, -1, 1) == -2
    assert limit(floor(x), x, 0) == 0
    assert limit(floor(x), x, 0, 1) == -1
    assert limit(floor(x), x, 1) == 1
    assert limit(floor(x), x, 1, 1) == 0
    assert limit(floor(x), x, 2) == 2
    assert limit(floor(x), x, 2, 1) == 1
    assert limit(floor(x), x, 248) == 248
    assert limit(floor(x), x, 248, 1) == 247
    assert limit(floor(arg(1 + x)), x, 0) == 0
    assert limit(floor(arg(1 - x)), x, 0) == 0


def test_floor_requires_robust_assumptions():
    assert limit(floor(sin(x)), x, 0) == 0
    assert limit(floor(sin(x)), x, 0, 1) == -1
    assert limit(floor(cos(x)), x, 0) == 0
    assert limit(floor(cos(x)), x, 0, 1) == 0
    assert limit(floor(5 + sin(x)), x, 0) == 5
    assert limit(floor(5 + sin(x)), x, 0, 1) == 4
    assert limit(floor(5 + cos(x)), x, 0) == 5
    assert limit(floor(5 + cos(x)), x, 0, 1) == 5


def test_ceiling():
    assert limit(ceiling(x), x, -2) == -1
    assert limit(ceiling(x), x, -2, 1) == -2
    assert limit(ceiling(x), x, -1) == 0
    assert limit(ceiling(x), x, -1, 1) == -1
    assert limit(ceiling(x), x, 0) == 1
    assert limit(ceiling(x), x, 0, 1) == 0
    assert limit(ceiling(x), x, 1) == 2
    assert limit(ceiling(x), x, 1, 1) == 1
    assert limit(ceiling(x), x, 2) == 3
    assert limit(ceiling(x), x, 2, 1) == 2
    assert limit(ceiling(x), x, 248) == 249
    assert limit(ceiling(x), x, 248, 1) == 248


def test_ceiling_requires_robust_assumptions():
    assert limit(ceiling(sin(x)), x, 0) == 1
    assert limit(ceiling(sin(x)), x, 0, 1) == 0
    assert limit(ceiling(cos(x)), x, 0) == 1
    assert limit(ceiling(cos(x)), x, 0, 1) == 1
    assert limit(ceiling(5 + sin(x)), x, 0) == 6
    assert limit(ceiling(5 + sin(x)), x, 0, 1) == 5
    assert limit(ceiling(5 + cos(x)), x, 0) == 6
    assert limit(ceiling(5 + cos(x)), x, 0, 1) == 6


def test_atan():
    assert limit(atan(x)*sin(1/x), x, 0) == 0
    assert limit(atan(x) + sqrt(x + 1) - sqrt(x), x, oo) == pi/2


def test_acosh():
    assert limit(acosh(I*x), x, 0) == 2*log(1 + I) - log(2)
    assert limit(acosh(I*x), x, 0, 1) == 2*log(1 - I) - log(2)
    assert limit(acosh(-I*x), x, 0) == 2*log(1 - I) - log(2)
    assert limit(acosh(-I*x), x, 0, 1) == 2*log(1 + I) - log(2)
    pytest.raises(PoleError, lambda: limit(acosh(I*x), x, 0, Reals))
    assert limit(acosh(x - I*x), x, 0) == 2*log(1 - I) - log(2)
    assert limit(acosh(x - I*x), x, 0, 1) == 2*log(1 + I) - log(2)
    pytest.raises(PoleError, lambda: limit(acosh(x - I*x), x, 0, Reals))
    assert limit(acosh(I*x**2), x, 0, Reals) == 2*log(1 + I) - log(2)
    assert limit(acosh(x**2 - I*x**2), x, 0, Reals) == 2*log(1 - I) - log(2)


def test_acoth():
    assert limit(acoth(x), x, 0) == -I*pi/2
    assert limit(acoth(x), x, 0, 1) == I*pi/2
    pytest.raises(PoleError, lambda: limit(acoth(x), x, 0, Reals))
    assert limit(acoth(-x), x, 0) == I*pi/2
    assert limit(acoth(x**2), x, 0, Reals) == -I*pi/2
    assert limit(acoth(I*x), x, 0) == -I*pi/2
    assert limit(acoth(I*x), x, 0, 1) == I*pi/2
    pytest.raises(PoleError, lambda: limit(acoth(x - I*x), x, 0, Reals))


def test_abs():
    assert limit(abs(x), x, 0) == 0
    assert limit(abs(sin(x)), x, 0) == 0
    assert limit(abs(cos(x)), x, 0) == 1
    assert limit(abs(sin(x + 1)), x, 0) == sin(1)

    # sympy/sympy#12398
    assert limit(abs(log(x)/x**3), x, oo) == 0
    expr = abs(log(x)/x**3)
    expr2 = expr.subs({x: x + 1})
    assert limit(x*(expr/expr2 - 1), x, oo) == 3


def test_heuristic():
    x = Symbol('x', extended_real=True)
    assert heuristics(sin(1/x) + atan(x), x, 0, -1) == sin(oo)
    assert heuristics(log(2 + sqrt(atan(x))*sin(1/x)), x, 0, -1) == log(2)
    assert heuristics(tan(tan(1/x)), x, 0, -1) is None
    assert isinstance(limit(log(2 + sqrt(atan(x))*sin(1/x)),
                            x, 0, -1, heuristics=False), Limit)


def test_sympyissue_3871():
    z = Symbol('z', positive=True)
    f = -1/z*exp(-z*x)
    assert limit(f, x, oo) == 0
    assert f.limit(x, oo) == 0


def test_exponential():
    y = Symbol('y', extended_real=True)
    assert limit((1 + y/x)**x, x, oo) == exp(y)
    assert limit((1 + y/(2*x))**x, x, oo) == exp(y/2)
    assert limit((1 + y/(2*x + 1))**x, x, oo) == exp(y/2)
    assert limit(((x - 1)/(x + 1))**x, x, oo) == exp(-2)
    assert limit(1 + (1 + 1/x)**x, x, oo) == 1 + E


@pytest.mark.xfail
def test_exponential2():
    assert limit((1 + y/(x + sin(x)))**x, x, oo) == exp(y)


def test_doit():
    f = Integral(2 * x, x)
    l = Limit(f, x, oo)
    assert l.doit() == oo


def test_doit2():
    f = Integral(2 * x, x)
    l = Limit(f, x, oo)
    # limit() breaks on the contained Integral.
    assert l.doit(deep=False) == l


def test_RootSum_limits():
    r = RootSum(x**2 + 1, Lambda(x, x*log(x + y)))

    assert limit(r, y, oo) == 0


def test_sympyissue_3792():
    assert limit((1 - cos(x))/x**2, x, Rational(1, 2)) == 4 - 4*cos(Rational(1, 2))
    assert limit(sin(sin(x + 1) + 1), x, 0) == sin(1 + sin(1))
    assert limit(abs(sin(x + 1) + 1), x, 0) == 1 + sin(1)


def test_sympyissue_4090():
    assert limit(1/(x + 3), x, 2) == Rational(1, 5)
    assert limit(1/(x + pi), x, 2) == 1/(2 + pi)
    assert limit(log(x)/(x**2 + 3), x, 2) == log(2)/7
    assert limit(log(x)/(x**2 + pi), x, 2) == log(2)/(4 + pi)


def test_sympyissue_4547():
    assert limit(cot(x), x, 0) == oo
    assert limit(cot(x), x, pi/2) == 0


def test_sympyissue_5164():
    assert limit(x**0.5, x, oo) == oo**0.5 == oo
    assert limit(x**0.5, x, 16) == 4.0
    assert limit(x**0.5, x, 0) == 0
    assert limit(x**(-0.5), x, oo) == 0
    assert limit(x**(-0.5), x, 4) == 0.5


def test_sympyissue_5183():
    # using list(...) so pytest can recalculate values
    tests = list(itertools.product([x, -x],
                                   [-1, 1],
                                   [2, 3, Rational(1, 2), Rational(2, 3)],
                                   [1, -1]))
    results = (oo, oo, -oo, oo, -oo*I, oo, -oo*cbrt(-1), oo,
               0, 0, 0, 0, 0, 0, 0, 0,
               oo, oo, oo, -oo, oo, -oo*I, oo, -oo*cbrt(-1),
               0, 0, 0, 0, 0, 0, 0, 0)
    assert len(tests) == len(results)
    for args, res in zip(tests, results):
        y, s, e, d = args
        eq = y**(s*e)
        assert limit(eq, x, 0, dir=d) == res


def test_sympyissue_5184():
    assert limit(sin(x)/x, x, oo) == 0
    assert limit(atan(x), x, oo) == pi/2
    assert limit(gamma(x), x, oo) == oo
    assert limit(cos(x)/x, x, oo) == 0
    assert limit(gamma(x), x, Rational(1, 2)) == sqrt(pi)
    assert limit(x*sin(1/x), x, 0) == 0


def test_sympyissue_5229():
    assert limit((1 + x)**(1/x) - E, x, 0) == 0


def test_sympyissue_4546():
    # using list(...) so pytest can recalculate values
    tests = list(itertools.product([cot, tan],
                                   [-pi/2, 0, pi/2, pi, 3*pi/2],
                                   [1, -1]))
    results = (0, 0, -oo, oo, 0, 0, -oo, oo, 0, 0,
               oo, -oo, 0, 0, oo, -oo, 0, 0, oo, -oo)
    assert len(tests) == len(results)
    for args, res in zip(tests, results):
        f, l, d = args
        eq = f(x)
        assert limit(eq, x, l, dir=d) == res


def test_sympyissue_3934():
    assert limit((1 + x**log(3))**(1/x), x, 0) == 1
    assert limit((5**(1/x) + 3**(1/x))**x, x, 0) == 5


def test_compute_leading_term():
    assert limit(root(x, 3)**77/(root(x, 3)**77 + 1), x, oo) == 1
    assert limit(root(x, 10)**1011/(root(x, 10)**1011 + 1), x, oo) == 1


def test_sympyissue_5955():
    assert limit((x**16)/(1 + x**16), x, oo) == 1
    assert limit((x**100)/(1 + x**100), x, oo) == 1
    assert limit((x**1885)/(1 + x**1885), x, oo) == 1
    assert limit((x**100/((x + 1)**100 + exp(-x))), x, oo) == 1


def test_newissue():
    assert limit(exp(1/sin(x))/exp(cot(x)), x, 0) == 1


def test_extended_real_line():
    assert limit(x - oo, x, oo) == -oo
    assert limit(oo - x, x, -oo) == oo
    assert limit(x**2/(x - 5) - oo, x, oo) == -oo
    assert limit(1/(x + sin(x)) - oo, x, 0) == -oo
    assert limit(oo/x, x, oo) == oo
    assert limit(x - oo + 1/x, x, oo) == -oo
    assert limit(x - oo + 1/x, x, 0) == -oo


@pytest.mark.xfail
def test_order_oo():
    x = Symbol('x', positive=True, finite=True)
    assert O(x)*oo != O(1, x)
    assert limit(oo/(x**2 - 4), x, oo) == oo


def test_sympyissue_5436():
    # also issue sympy/sympy#13312 (but see diofant/diofant#425!)
    assert limit(exp(x*y), x, oo) == exp(oo*sign(y))
    assert limit(exp(-x*y), x, oo) == exp(-oo*sign(y))


def test_Limit_dir():
    pytest.raises(ValueError, lambda: Limit(x, x, 0, dir=0))
    pytest.raises(ValueError, lambda: Limit(x, x, 0, dir='0'))


def test_polynomial():
    assert limit((x + 1)**1000/((x + 1)**1000 + 1), x, oo) == 1
    assert limit((x + 1)**1000/((x + 1)**1000 + 1), x, -oo) == 1


def test_rational():
    assert limit(1/y - (1/(y + x) + x/(y + x)/y)/z, x, oo) == (z - 1)/(y*z)
    assert limit(1/y - (1/(y + x) + x/(y + x)/y)/z, x, -oo) == (z - 1)/(y*z)


def test_sympyissue_5740():
    assert limit(log(x)*z - log(2*x)*y, x, 0) == oo*sign(y - z)


def test_sympyissue_6366():
    n = Symbol('n', integer=True, positive=True)
    r = (n + 1)*x**(n + 1)/(x**(n + 1) - 1) - x/(x - 1)
    assert limit(r, x, 1).simplify() == n/2


def test_factorial():
    f = factorial(x)
    assert limit(f, x, oo) == oo
    assert limit(x/f, x, oo) == 0
    # see Stirling's approximation:
    # https://en.wikipedia.org/wiki/Stirling's_approximation
    assert limit(f/(sqrt(2*pi*x)*(x/E)**x), x, oo) == 1
    assert limit(f, x, -oo) == factorial(-oo)
    assert (limit(f, x, x**2) - factorial(x**2)).simplify() == 0
    assert (limit(f, x, -x**2) - factorial(-x**2)).simplify() == 0


def test_lowergamma_at_origin():
    assert limit(lowergamma(a, x), a, 0) == oo
    assert limit(lowergamma(a, x), a, 0, dir=1) == -oo
    assert limit(lowergamma(I*a, x), a, 0) == -oo*I
    assert limit(lowergamma(I*a, x), a, 0, dir=1) == oo*I
    assert limit(lowergamma(a, 1), a, 0) == oo
    assert limit(x*lowergamma(x, 1)/gamma(x + 1), x, 0) == 1


def test_sympyissue_6560():
    e = 5*x**3/4 - 3*x/4 + (y*(3*x**2/2 - Rational(1, 2)) +
                            35*x**4/8 - 15*x**2/4 + Rational(3, 8))/(2*(y + 1))
    assert limit(e, y, oo) == (5*x**3 + 3*x**2 - 3*x - 1)/4


def test_sympyissue_5172():
    r = Symbol('r', positive=True)
    p = Symbol('p', positive=True)
    m = Symbol('m', negative=True)
    expr = ((2*n*(n - r + 1)/(n + r*(n - r + 1)))**c +
            (r - 1)*(n*(n - r + 2)/(n + r*(n - r + 1)))**c - n)/(n**c - n)
    expr = expr.subs({c: c + 1})
    assert limit(expr.subs({c: m}), n, oo) == 1
    assert limit(expr.subs({c: p}), n, oo) == (2**(p + 1) + r -
                                               1)/(r + 1)**(p + 1)


def test_sympyissue_7088():
    assert limit(sqrt(x/(x + a)), x, oo) == 1


def test_sympyissue_6364():
    e = z/(1 - sqrt(1 + z)*sin(a)**2 - sqrt(1 - z)*cos(a)**2)
    assert (limit(e, z, 0) - 2/cos(2*a)).simplify() == 0


def test_sympyissue_4099():
    assert limit(a/x, x, 0) == oo*sign(a)
    assert limit(-a/x, x, 0) == -oo*sign(a)
    assert limit(-a*x, x, oo) == -oo*sign(a)
    assert limit(a*x, x, oo) == oo*sign(a)


def test_sympyissue_4503():
    assert limit((sqrt(1 + exp(x + y)) - sqrt(1 + exp(x)))/y,
                 y, 0) == exp(x)/(2*sqrt(exp(x) + 1))


def test_sympyissue_8730():
    assert limit(subfactorial(x), x, oo) == oo


def test_issue_55():
    assert limit((x + exp(x))/(x - 1), x, -oo) == 1
    assert limit((x*exp(x))/(exp(x) - 1), x, -oo) == 0  # issue sympy/sympy#2929

    # issue sympy/sympy#22982
    assert limit((log(E + 1/x) - 1)**(1 - sqrt(E + 1/x)), x, oo) == oo
    assert limit((log(E + 1/x))**(1 - sqrt(E + 1/x)), x, oo) == 1
    assert limit((log(E + 1/x) - 1)**-sqrt(E + 1/x), x, oo) == oo


def test_sympyissue_8061():
    assert limit(4**(acos(1/(1 + x**2))**2)/log(1 + x), x, 0) == oo


def test_sympyissue_8229():
    assert limit((root(x, 4) - 2)/root(sqrt(x) - 4, 3)**2, x, 16) == 0


def test_Limit_free_symbols():
    # issue sympy/sympy#9205
    assert Limit(x, x, a).free_symbols == {a}
    assert Limit(x, x, a, 1).free_symbols == {a}
    assert Limit(x + y, x + y, a).free_symbols == {a}
    assert Limit(-x**2 + y, x**2, a).free_symbols == {y, a}


def test_sympyissue_10610():
    assert limit(3**x*3**(-x - 1)*(x + 1)**2/x**2, x, oo) == Rational(1, 3)
    assert limit(2**x*2**(-x - 1)*(x + 1)*(y - 1)**(-x) *
                 (y - 1)**(x + 1)/(x + 2), x, oo) == y/2 - Rational(1, 2)


def test_sympyissue_9075():
    assert limit((6**(x + 1) + x + 1)/(6**x + x), x, oo) == 6


def test_sympyissue_8634():
    p = Symbol('p', positive=True)
    assert limit(x**p, x, -oo) == oo*sign((-1)**p)


def test_sympyissue_9558():
    assert limit(sin(x)**15, x, 0, 1) == 0  # should be fast


def test_issue_296():
    e = log(exp(1/x)/Float(2) + exp(-1/x)/2)*x**2
    assert e.limit(x, oo) == 0.5


def test_sympyissue_5383():
    e = (1.0 + 1.0*x)**(1.0/x)
    assert e.limit(x, 0) == E.evalf()


def test_sympyissue_6171():
    e = Piecewise((0, x < 0), (1, True))
    assert e.limit(x, 0) == 1
    assert e.limit(x, 0, 1) == 0


def test_sympyissue_11526():
    df = diff(1/(a*log((x - b)/(x - c))), x)
    res = -1/(-a*c + a*b)
    assert limit(df, x, oo) == res
    assert (limit(simplify(df), x, oo) - res).simplify() == 0

    e = log((1/x - b)/(1/x - c))
    assert e.as_leading_term(x) == x*(c - b)


def test_sympyissue_11672():
    assert limit(Rational(-1, 2)**x, x, oo) == 0
    assert limit(1/(-2)**x, x, oo) == 0


def test_sympyissue_8635():
    n = Symbol('n', integer=True, positive=True)

    k = 0
    assert limit(x**n - x**(n - k), x, oo) == 0
    k = 1
    assert limit(x**n - x**(n - k), x, oo) == oo
    k = 2
    assert limit(x**n - x**(n - k), x, oo) == oo
    k = 3
    assert limit(x**n - x**(n - k), x, oo) == oo


def test_sympyissue_8157():
    n = Symbol('n', integer=True)
    limit(cos(pi*n), n, oo)  # not raises


def test_sympyissue_5415():
    assert limit(polygamma(2 + 1/x, 3 + exp(-x)), x, oo) == polygamma(2, 3)


def test_sympyissue_2865():
    l1 = limit(O(1/x, x, oo), x, 0)
    assert l1 != 0
    assert isinstance(l1, Limit)
    l2 = limit(O(x, x, oo), x, 0)
    assert l2 != 0
    assert isinstance(l2, Limit)


def test_sympyissue_11879():
    assert limit(((x + y)**n - x**n)/y, y, 0).powsimp() == n*x**(n-1)


def test_sympyissue_12555():
    assert limit((3**x + 2*x**10)/(x**10 + E**x), x, -oo) == 2


def test_sympyissue_12769():
    r = Symbol('r', real=True)
    a, b, s0, K, F0 = symbols('a b s0 K F0', positive=True, real=True)
    fx = (F0**b*K**b*r*s0 -
          sqrt((F0**2*K**(2*b)*a**2*(b - 1) +
                F0**(2*b)*K**2*a**2*(b - 1) +
                F0**(2*b)*K**(2*b)*s0**2*(b - 1)*(b**2 - 2*b + 1) -
                2*F0**(2*b)*K**(b + 1)*a*r*s0*(b**2 - 2*b + 1) +
                2*F0**(b + 1)*K**(2*b)*a*r*s0*(b**2 - 2*b + 1) -
                2*F0**(b + 1)*K**(b + 1)*a**2*(b - 1))/((b - 1)*(b**2 - 2*b + 1))))*(b*r - b - r + 1)
    assert limit(fx, K, F0) == (F0**(2*b)*b*r**2*s0 - 2*F0**(2*b)*b*r*s0 +
                                F0**(2*b)*b*s0 - F0**(2*b)*r**2*s0 +
                                2*F0**(2*b)*r*s0 - F0**(2*b)*s0)


def test_sympyissue_13332():
    assert limit(sqrt(30)*5**(-5*x - 1)*(46656*x)**x *
                 (5*x + 2)**(5*x + Rational(5, 2)) *
                 (6*x + 2)**(-6*x - Rational(5, 2)), x, oo) == Rational(25, 36)


def test_sympyissue_13382():
    assert limit(x*(((x + 1)**2 + 1)/(x**2 + 1) - 1), x, oo) == 2


def test_sympyissue_13403():
    assert limit(x*(-1 + (x + log(x + 1) + 1)/(x + log(x))), x, oo) == 1


def test_sympyissue_13416():
    assert limit((-x**3*log(x)**3 +
                  (x - 1)*(x + 1)**2*log(x + 1)**3)/(x**2*log(x)**3),
                 x, oo) == 1


def test_sympyissue_13462():
    assert limit(x**2*(2*x*(-(1 - 1/(2*x))**y + 1) -
                 y - (-y**2/4 + y/4)/x), x, oo) == y/12 - y**2/8 + y**3/24


def test_sympyissue_13575():
    assert limit(acos(erfi(x)), x, 1).equals(pi/2 + I*log(sqrt(erf(I)**2 + 1) +
                                                          erf(I))) is True


def test_issue_558():
    r = Symbol('r', positive=True)
    expr = ((2*x*(x - r + 1)/(x + r*(x - r + 1)))**c +
            (r - 1)*(x*(x - r + 2)/(x + r*(x - r + 1)))**c - x)/(x**c - x)
    expr = expr.subs({c: c + 1})
    assert limit(expr, x, oo) == Limit(expr, x, oo)


def test_sympyissue_14393():
    assert limit((x**b - y**b)/(x**a - y**a), x, y) == b*y**b/y**a/a


def test_sympyissue_14590():
    assert limit((x**3*((x + 1)/x)**x)/((x + 1)*(x + 2)*(x + 3)), x, oo) == E


def test_sympyissue_14793():
    e = ((x + Rational(1, 2))*log(x) - x +
         log(2*pi)/2 - log(factorial(x)) + 1/(12*x))*x**3
    assert limit(e, x, oo) == Rational(1, 360)


def test_sympyissue_14811():
    assert limit(((1 + Rational(2, 3)**(x + 1))**2**x)/(2**Rational(4, 3)**(x - 1)), x, oo) == oo


def test_sympyissue_15055():
    assert limit(x**3*((-x - 1)*sin(1/x) + (x + 2)*sin(1/(x + 1)))/(-x + 1), x, oo) == 1


def test_sympyissue_15146():
    assert limit((x/2)*(-2*x**3 - 2*(x**3 - 1)*x**2*digamma(x**3 + 1) +
                        2*(x**3 - 1)*x**2*digamma(x**3 + x + 1) +
                        x + 3), x, oo) == Rational(1, 3)


def test_sympyissue_15323():
    assert limit(((1 - 1/x)**x).diff(x), x, 1) == 1


def test_sympyissue_15984():
    assert limit((-x + log(exp(x) + 1))/x, x, oo, dir=1) == 0


def test_sympyissue_16222():
    assert limit(exp(x), x, 10000000) == exp(10000000)
    assert limit(exp(x), x, 100000000) == exp(100000000)
    assert limit(exp(x), x, 1000000000) == exp(1000000000)


@pytest.mark.timeout(20)
def test_sympyissue_15282():
    assert limit((x**2000 - (x + 1)**2000)/x**1999, x, oo) == -2000


def test_sympyissue_16722():
    n, z = symbols('n z')
    assert isinstance(limit(binomial(n + z, n)*n**-z, n, oo), Limit)

    z = symbols('z', positive=True)
    assert limit(binomial(n + z, n)*n**-z, n, oo) == 1/gamma(z + 1)

    n = symbols('n', positive=True, integer=True)
    z = symbols('z', positive=True)
    assert limit(binomial(n + z, n)*n**-z, n, oo) == 1/gamma(z + 1)

    n, z = symbols('n z', positive=True, integer=True)
    assert limit(binomial(n + z, n)*n**-z, n, oo) == 1/gamma(z + 1)


def test_sympyissue_15673():
    p = symbols('p')
    alpha = symbols('α', positive=True)

    e = Limit(4*pi*p**(-alpha)*(p**3 - p**alpha)/(alpha - 3), p, 0)
    assert isinstance(e.doit(), Limit)  # but see diofant/diofant#425


def test_sympyissue_17380():
    assert limit(x*(((x + 1)**2 + 1)/(x**2 + 1) - 1), x, oo) == 2


def test_sympyissue_17431():
    assert limit(((x + 1) + 1)/(((x + 1) + 2)*factorial(x + 1)) *
                 (x + 2)*factorial(x)/(x + 1), x, oo) == 0
    assert limit((x + 2)**2*factorial(x)/((x + 1)*(x + 3)*factorial(x + 1)),
                 x, oo) == 0

    # test from sympy/sympy#17434 (see also diofant/diofant#425):
    y = symbols('y', integer=True, positive=True)
    assert isinstance(limit(x*factorial(x)/factorial(x + y), x, oo), Limit)


def test_sympyissue_17792():
    assert limit(factorial(x)/sqrt(x)*(E/x)**x, x, oo) == sqrt(2*pi)


def test_sympyissue_18118():
    assert limit(sign(x), x, 0) == +1
    assert limit(sign(x), x, 0, 1) == -1

    assert limit(sign(sin(x)), x, 0) == +1
    assert limit(sign(sin(x)), x, 0, 1) == -1


def test_sympyissue_6599():
    assert limit((x + cos(x))/x, x, oo) == 1


def test_sympyissue_18176():
    x = Symbol('x', real=True, positive=True)
    n = Symbol('n', integer=True, positive=True)
    e = x**n - x**(n - k)
    assert limit(e.subs({k: 0}), x, oo) == 0
    assert limit(e.subs({k: 1}), x, oo) == oo


def test_sympyissue_18306():
    assert limit(sin(sqrt(x))/sqrt(sin(x)), x, 0) == 1


def test_sympyissue_18378():
    assert limit(log(exp(3*x) + x)/log(exp(x) + x**100), x, oo) == 3


def test_sympyissue_18399():
    assert limit((1 - x/2)**(3*x), x, oo) == oo
    assert limit((-x)**x, x, oo) == oo


def test_sympyissue_18452():
    assert limit(abs(log(x))**x, x, 0) == 1
    assert limit(abs(log(x))**x, x, 0, 1) == 1


def test_sympyissue_18482():
    assert limit(sqrt(x**2 + 6*x) + (x**3 + x**2)/(x**2 + 1), x, -oo) == -2
    assert limit((x**3 + x**2 + sqrt(x*(x + 6))*(x**2 + 1))/(x**2 + 1),
                 x, -oo) == -2
    assert limit((2*exp(3*x)/(exp(2*x) + 1))**(1/x), x, oo) == E


def test_sympyissue_18501():
    assert limit(abs(log(x - 1)**3 - 1), x, 1) == oo


def test_sympyissue_18508():
    assert limit(sin(x)/sqrt(1 - cos(x)), x, 0) == sqrt(2)


def test_sympyissue_18707():
    p = Symbol('p', positive=True, real=True)

    assert limit(1/p**n, n, oo) == p**-oo


def test_sympyissue_18997():
    assert limit(abs(log(x)), x, 0) == oo
    assert limit(abs(log(abs(x))), x, 0) == oo


def test_sympyissue_18992():
    assert limit(x/(factorial(x)**(1/x)), x, oo) == E


def test_sympyissue_19026():
    assert limit(abs(log(x) + 1)/log(x), x, oo) == 1


def test_sympyissue_19770():
    assert limit(cos(x*y)/x, x, oo) == 0


def test_sympyissue_19766():
    assert limit(2**(-x)*sqrt(4**(x + 1) + 1), x, oo) == 2


def test_sympyissue_14874():
    assert limit(besselk(0, x), x, oo) == 0


def test_sympyissue_20365():
    assert limit(((x + 1)**(1/x) - E)/x, x, 0) == -E/2


def test_sympyissue_20704():
    assert limit(x*(abs(1/x + y) - abs(y - 1/x))/2, x, 0) == 0


def test_sympyissue_21031():
    assert limit(((1 + x)**(1/x) -
                  (1 + 2*x)**(1/(2*x)))/asin(x), x, 0) == E/2


def test_sympyissue_21038():
    assert limit(sin(pi*x)/(3*x - 12), x, 4) == pi/3


def test_sympyissue_21029():
    e = (sinh(x) + cosh(x) - 1)/x/4
    ans0 = Rational(1, 4)
    ansz = (exp(z) - 1)/z/4

    assert limit(e, x, 0) == ans0
    assert limit(e, x, z) == ansz
    assert limit(ansz, z, 0) == ans0


def test_sympyissue_20578():
    assert all(limit(abs(x)*sin(1/x), x, 0, d) == 0 for d in [-1, 1, Reals])


def test_sympyissue_19453():
    beta = Symbol('beta', real=True, positive=True)
    h = Symbol('h', real=True, positive=True)
    m = Symbol('m', real=True, positive=True)
    w = Symbol('omega', real=True, positive=True)
    g = Symbol('g', real=True, positive=True)

    q = 3*h**2*beta*g*exp(h*beta*w/2)
    p = m**2*w**2
    s = exp(h*beta*w) - 1
    z = (-q/(4*p*s) - q/(2*p*s**2) -
         q*(exp(h*beta*w) + 1)/(2*p*s**3) + exp(h*beta*w/2)/s)
    e = -diff(log(z), beta)

    assert limit(e - h*w/2, beta, oo) == 0
    assert limit(e.simplify() - h*w/2, beta, oo) == 0


def test_sympyissue_19442():
    pytest.raises(PoleError, lambda: limit(1/x, x, 0, Reals))


def test_sympyissue_21530():
    assert limit(sinh(n + 1)/sinh(n), n, oo) == E


def test_sympyissue_21550():
    r = (sqrt(5) - 1)/2
    assert limit((x - r)/(x**2 + x - 1), x, r).simplify() == sqrt(5)/5


def test_sympyissue_21606():
    assert limit(cos(x)/sign(x), x, pi) == -1
    assert limit(cos(x)/sign(x), x, pi, 1) == -1


def test_sympyissue_21756():
    e = (1 - exp(-2*I*pi*z))/(1 - exp(-2*I*pi*z/5))
    assert limit(e, z, 0) == 5


def test_sympyissue_21785():
    e = Limit(sqrt((-a**2 + x**2)/(1 - x**2)), a, 1, 1)

    assert e.doit() == (-1)**(floor(arg(-1/(x**2 - 1))/(2*pi)) + 1/2)

    assert e.subs({x: 1 + I}).doit().simplify() == +I
    assert e.subs({x: 1 - I}).doit().simplify() == -I


def test_sympyissue_22220():
    e1 = sqrt(30)*atan(sqrt(30)*tan(x/2)/6)/30
    e2 = sqrt(30)*I*(-log(sqrt(2)*tan(x/2) - 2*sqrt(15)*I/5) +
                     +log(sqrt(2)*tan(x/2) + 2*sqrt(15)*I/5))/60

    assert limit(e1, x, -pi) == -sqrt(30)*pi/60
    assert limit(e2, x, -pi) == -sqrt(30)*pi/30

    assert limit(e1, x, -pi, 1) == sqrt(30)*pi/60
    assert limit(e2, x, -pi, 1) == 0


def test_sympyissue_22334():
    k = Symbol('k', positive=True)
    assert limit((x + 1)**k/((x + 1)**(k + 1) - x**(k + 1)), x, oo) == 1/(k + 1)


def test_sympyissue_22893():
    a, b = symbols('a b', positive=True)
    e = (a*exp(-a*x) + b*exp(-b*x))*exp(b*x)
    assert isinstance(limit(e, x, oo), Limit)


def test_sympyissue_22986():
    assert limit(acosh(1 + 1/x)*sqrt(x), x, oo) == sqrt(2)


def test_sympyissue_23231():
    assert limit((2**x - 2**-x)/(2**x + 2**-x), x, -oo) == -1


def test_issue_1164():
    # also sympy/sympy#14502
    assert limit(factorial(x) - x**x, x, oo) == -oo
    l = Limit(factorial(x) - x**oo, x, oo)
    assert l.doit() == l


def test_sympyissue_23266():
    assert limit(-0.295084971874737*exp(-18.9442719099992*x) +
                 5.29508497187474*exp(-1.05572809000084*x), x, oo) == 0


def test_sympyissue_7391():
    f = Function('f')
    func = x*y*y/(x*x + y**4)
    l = Limit(func.subs({y: f(x)}), x, 0)
    assert l.doit() == l
    assert l.subs({f: Lambda(x, sqrt(x))}).doit() == Rational(1, 2)


def test_issue_1216():
    assert (x/abs(sqrt(1 - x**2))).limit(x, oo) == 1
    assert ((4*x - 2)/abs(sqrt(4 - 4*(2*x - 1)**2))).limit(x, oo) == 1


def test_issue_1213():
    # also sympy/sympy#11496
    assert limit(erfc(log(1/x)), x, oo) == 2


def test_sympyissue_23319():
    assert limit(x*tan(pi/x), x, oo) == pi


def test_issue_1230():
    assert limit(log(x + sqrt(x**2 + 1)), x, I*oo) == oo


def test_sympyissue_8433():
    d = Symbol('d', positive=True)
    e = erf(1 - x/d)
    assert limit(e, x, oo) == -1
    assert limit(e.subs({d: 2}), x, oo) == -1


def test_sympyissue_13750():
    assert limit(erf(-x), x, oo) == -1
    assert limit(erf(1 - x), x, oo) == -1
    assert limit(erf(a - x), x, oo) == -1
    assert limit(erf(sqrt(x) - x), x, oo) == -1


def test_sympyissue_23836():
    p = Piecewise((x**3, x < 3), (-x**2, x > 3), (2, True))
    assert limit(p, x, 3) == -9
    assert limit(p, x, 3, 1) == 27


def test_sympyissue_24067():
    n = symbols('n', positive=True)
    e = (5*x)**(n + 2)/x**2
    assert limit(e, x, 0) == 0
    assert limit(e.simplify(), x, 0) == 0
    e = x**(n + 2)/x**2
    assert limit(e, x, 0) == 0


def test_sympyissue_24127():
    assert limit(Piecewise((sin(x), x < 0),
                           (Rational(1, 2), True)), x, 1) == Rational(1, 2)


def test_sympyissue_24210():
    # also sympy/sympy#25885
    expr = exp(x)/((1 + 1/x)**(x**2))
    assert limit(expr, x, oo) == sqrt(E)
    assert limit(1/expr, x, oo) == 1/sqrt(E)


def test_sympyissue_24225():
    e = (log(1 + x) + log(1 + y)) / (x + y)
    assert limit(limit(e, x, 0, dir=Reals), y, 0, dir=Reals) == 1
    assert limit(limit(e, y, 0, dir=Reals), x, 0, dir=Reals) == 1


def test_sympyissue_24331():
    z = Symbol('z', complex=True)
    assert limit(log(z), z, 0) == -oo

    z = Symbol('z', infinite=True)
    assert limit(log(z), z, 0) == -oo


def test_sympyissue_24386():
    assert limit((x + y)/(exp(z) + 1) - y, z, -oo) == x


def test_issue_1155():
    assert (limit((x**(x + 1)*(log(x) + 1) + 1)/x, x, 20) ==
            Rational(2097152000000000000000000001, 20) +
            104857600000000000000000000*log(20))


def test_sympyissue_25582():
    assert limit(atan(exp(x)), x, oo) == pi/2


def test_sympyissue_25681():
    e = x/abs(sqrt(x**2 - 1))
    assert limit(e, x, 1, dir=Reals) == oo
    assert limit(e, x, -1, dir=Reals) == -oo


def test_sympyissue_25833():
    assert limit(atan(log(2**x)/log(2*x)), x, oo) == pi/2


def test_sympyissue_26250():
    e = ((1 - 3*x**2)*elliptic_e(4*x/(x**2 + 2*x + 1))**2/2 -
         (x**2 - 2*x + 1)*elliptic_e(4*x/(x**2 + 2*x + 1)) *
         elliptic_k(4*x/(x**2 + 2*x + 1))/2)/(pi**2*x**8 - 2*pi**2*x**7 -
                                              pi**2*x**6 + 4*pi**2*x**5 -
                                              pi**2*x**4 - 2*pi**2*x**3 +
                                              pi**2*x**2)
    assert limit(e, x, 0) == Rational(-1, 8)

    t = 4*x/(x + 1)
    e = ((x + 1)*elliptic_e(t) + (x - 1)*elliptic_k(t))/x**2
    assert e.limit(x, 0) == -pi/2
    assert elliptic_e(t).series() == (pi/2 - pi*x/2 + pi*x**2/8 - 3*pi*x**3/8 -
                                      15*pi*x**4/128 - 93*pi*x**5/128 + O(x**6))

    e = hyper((-Rational(1, 2), Rational(1, 2)), (1,), 4*x/(x + 1))
    assert e.series().simplify() == (1 - x + x**2/4 - 3*x**3/4 -
                                     15*x**4/64 - 93*x**5/64 + O(x**6))


def test_sympyissue_26313():
    e = Piecewise((x**2, x <= 2), (5*x - 7, x > 2))
    assert limit(e, x, 2) == 3
    assert limit(e, x, 2, dir=1) == 4


def test_sympyissue_26513():
    assert limit((x/(x + 1))**x, x, oo) == exp(-1)
    assert limit((-x/(x + 1))**x, x, oo) == Limit((-x/(x + 1))**x, x, oo)
    assert limit(abs((-x/(x + 1))**x), x, oo) == exp(-1)


def test_sympyissue_26525():
    e = (-exp(-I*pi*x)*I*(exp(I*pi*x)*pi -
                          gamma(-x + Rational(1, 2))*gamma(x + Rational(1, 2))) *
         gamma(-x - 1)/(2*sqrt(pi)*gamma(-x + Rational(1, 2))))
    assert limit(e, x, 1) == pi/8


def test_issue_1397():
    assert limit(re(asin(x)), x, oo) == pi/2


def test_issue_1403():
    assert acsc(x).rewrite(atan).limit(x, I*oo) == 0


def test_sympyissue_26916():
    assert limit(Ei(x)*exp(-x), x, +oo) == 0
    assert limit(Ei(x)*exp(-x), x, -oo) == 0


def test_sympyissue_26990():
    assert limit(x/((x - 6)*sinh(tanh(0.03*x)) + tanh(x) - 0.5),
                 x, oo) == 0.85091812823932156


def test_sympyissue_27236():
    e = Piecewise((1, x < 0), (-1, x >= 0))
    assert limit(e, x, 0, -1) == -1 == limit(e, x, 0)
    assert limit(e, x, 0, +1) == +1
    pytest.raises(PoleError, lambda: limit(e, x, 0, dir=Reals))


def test_sympyissue_27551():
    e = 1/(x*sqrt(log(x)**2))
    assert limit(e, x, 1, dir=+1) == oo
    assert limit(e, x, 1, dir=-1) == oo
