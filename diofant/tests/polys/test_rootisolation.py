"""Tests for real and complex root isolation and refinement algorithms. """

import pytest

from diofant.core import I
from diofant.domains import EX, QQ, ZZ
from diofant.functions import sqrt
from diofant.polys.polyerrors import DomainError, RefinementFailed
from diofant.polys.rings import ring
from diofant.polys.rootisolation import (RealInterval,
                                         dup_inner_refine_real_root,
                                         dup_step_refine_real_root)


__all__ = ()


def test_dup_sturm():
    R, x = ring("x", QQ)

    assert R.dup_sturm(5) == [1]
    assert R.dup_sturm(x) == [x, 1]

    f = x**3 - 2*x**2 + 3*x - 5
    assert R.dup_sturm(f) == [f, 3*x**2 - 4*x + 3, -10*x/9 + QQ(13, 3), -QQ(3303, 100)]


def test_dup_sign_variations():
    R, x = ring('x', ZZ)

    assert R.dup_sign_variations(0) == 0
    assert R.dup_sign_variations(x) == 0
    assert R.dup_sign_variations(x**2 + 2) == 0
    assert R.dup_sign_variations(x**3 + 3*x) == 0
    assert R.dup_sign_variations(x**4 + 4*x**2 + 5) == 0

    assert R.dup_sign_variations(2 - x**2) == 1
    assert R.dup_sign_variations(3*x - x**3) == 1
    assert R.dup_sign_variations(-x**4 + 4*x**2 + 5) == 1

    assert R.dup_sign_variations(-x**2 - 4*x - 5) == 0
    assert R.dup_sign_variations(+x**2 - 4*x - 5) == 1
    assert R.dup_sign_variations(+x**2 + 4*x - 5) == 1
    assert R.dup_sign_variations(+x**2 - 4*x + 5) == 2
    assert R.dup_sign_variations(-x**2 + 4*x - 5) == 2
    assert R.dup_sign_variations(-x**2 + 4*x + 5) == 1
    assert R.dup_sign_variations(-x**2 - 4*x + 5) == 1
    assert R.dup_sign_variations(+x**2 + 4*x + 5) == 0

    assert R.dup_sign_variations(-x**4 - 4*x**2 - 5) == 0
    assert R.dup_sign_variations(+x**4 - 4*x**2 - 5) == 1
    assert R.dup_sign_variations(+x**4 + 4*x**2 - 5) == 1
    assert R.dup_sign_variations(+x**4 - 4*x**2 + 5) == 2
    assert R.dup_sign_variations(-x**4 + 4*x**2 - 5) == 2
    assert R.dup_sign_variations(-x**4 + 4*x**2 + 5) == 1
    assert R.dup_sign_variations(-x**4 - 4*x**2 + 5) == 1
    assert R.dup_sign_variations(+x**4 + 4*x**2 + 5) == 0


def test_dup_root_upper_bound():
    R, x = ring("x", ZZ)

    assert R.dup_root_upper_bound(+x - 1) == 4
    assert R.dup_root_upper_bound(-x - 1) is None

    R, x = ring("x", QQ)

    assert R.dup_root_upper_bound(+x - 1) == 4
    assert R.dup_root_upper_bound(-x - 1) is None

    assert R.dup_root_upper_bound(+x/2 - 1) is None
    assert R.dup_root_upper_bound(-x/2 - 1) is None


def test_dup_step_refine_real_root():
    assert dup_step_refine_real_root([1, 1], (-2, 0, 1, 1),
                                     ZZ) == ([1, 2], (0, -2, 1, 2))


def test_dup_inner_refine_real_root():
    f = [-1, 0, 2]
    r = (1, QQ(3, 2))
    assert dup_inner_refine_real_root(f, (1, 2, 1, 1), QQ, steps=1) == r


def test_dup_refine_real_root():
    R, x = ring("x", ZZ)
    f = x**2 - 2

    assert R.dup_refine_real_root(f, QQ(1), QQ(1), steps=1) == (1, 1)
    assert R.dup_refine_real_root(f, QQ(1), QQ(1), steps=9) == (1, 1)

    pytest.raises(ValueError, lambda: R.dup_refine_real_root(f, QQ(-2), QQ(2)))

    s, t = QQ(1, 1), QQ(2, 1)

    assert R.dup_refine_real_root(f, s, t, steps=0) == (1, 2)
    assert R.dup_refine_real_root(f, s, t, steps=1) == (1, QQ(3, 2))
    assert R.dup_refine_real_root(f, s, t, steps=2) == (QQ(4, 3), QQ(3, 2))
    assert R.dup_refine_real_root(f, s, t, steps=3) == (QQ(7, 5), QQ(3, 2))
    assert R.dup_refine_real_root(f, s, t, steps=4) == (QQ(7, 5), QQ(10, 7))

    s, t = QQ(1, 1), QQ(3, 2)

    assert R.dup_refine_real_root(f, s, t, steps=0) == (1, QQ(3, 2))
    assert R.dup_refine_real_root(f, s, t, steps=1) == (QQ(4, 3), QQ(3, 2))
    assert R.dup_refine_real_root(f, s, t, steps=2) == (QQ(7, 5), QQ(3, 2))
    assert R.dup_refine_real_root(f, s, t, steps=3) == (QQ(7, 5), QQ(10, 7))
    assert R.dup_refine_real_root(f, s, t, steps=4) == (QQ(7, 5), QQ(17, 12))

    s, t = QQ(1, 1), QQ(5, 3)

    assert R.dup_refine_real_root(f, s, t, steps=0) == (1, QQ(5, 3))
    assert R.dup_refine_real_root(f, s, t, steps=1) == (1, QQ(3, 2))
    assert R.dup_refine_real_root(f, s, t, steps=2) == (QQ(7, 5), QQ(3, 2))
    assert R.dup_refine_real_root(f, s, t, steps=3) == (QQ(7, 5), QQ(13, 9))
    assert R.dup_refine_real_root(f, s, t, steps=4) == (QQ(7, 5), QQ(27, 19))

    s, t = QQ(-1, 1), QQ(-2, 1)

    assert R.dup_refine_real_root(f, s, t, steps=0) == (-QQ(2, 1), -QQ(1, 1))
    assert R.dup_refine_real_root(f, s, t, steps=1) == (-QQ(3, 2), -QQ(1, 1))
    assert R.dup_refine_real_root(f, s, t, steps=2) == (-QQ(3, 2), -QQ(4, 3))
    assert R.dup_refine_real_root(f, s, t, steps=3) == (-QQ(3, 2), -QQ(7, 5))
    assert R.dup_refine_real_root(f, s, t, steps=4) == (-QQ(10, 7), -QQ(7, 5))

    pytest.raises(RefinementFailed, lambda: R.dup_refine_real_root(f, QQ(0), QQ(1)))

    s, t, u, v, w = QQ(1), QQ(2), QQ(24, 17), QQ(17, 12), QQ(7, 5)

    assert R.dup_refine_real_root(f, s, t, eps=QQ(1, 100)) == (u, v)
    assert R.dup_refine_real_root(f, s, t, steps=6) == (u, v)

    assert R.dup_refine_real_root(f, s, t, eps=QQ(1, 100), steps=5) == (w, v)
    assert R.dup_refine_real_root(f, s, t, eps=QQ(1, 100), steps=6) == (u, v)
    assert R.dup_refine_real_root(f, s, t, eps=QQ(1, 100), steps=7) == (u, v)

    s, t, u, v = QQ(-2), QQ(-1), QQ(-3, 2), QQ(-4, 3)

    assert R.dup_refine_real_root(f, s, t, disjoint=QQ(-5)) == (s, t)
    assert R.dup_refine_real_root(f, s, t, disjoint=-v) == (s, t)
    assert R.dup_refine_real_root(f, s, t, disjoint=v) == (u, v)

    s, t, u, v = QQ(1), QQ(2), QQ(4, 3), QQ(3, 2)

    assert R.dup_refine_real_root(f, s, t, disjoint=QQ(5)) == (s, t)
    assert R.dup_refine_real_root(f, s, t, disjoint=-u) == (s, t)
    assert R.dup_refine_real_root(f, s, t, disjoint=u) == (u, v)

    R, x = ring("x", QQ)
    f = x**2 - QQ(1, 4)
    assert R.dup_refine_real_root(f, QQ(0), QQ(1),
                                  steps=1) == (QQ(1, 2), QQ(1, 2))

    D = ZZ.poly_ring("y")
    y, = D.gens
    R, x = ring("x", D)
    f = x**2 + y*x - 1
    pytest.raises(DomainError, lambda: R.dup_refine_real_root(f, ZZ(0), ZZ(1)))


def test_dup_isolate_real_roots_sqf():
    R, x = ring("x", ZZ)

    assert R.dup_isolate_real_roots_sqf(0) == []
    assert R.dup_isolate_real_roots_sqf(5) == []

    assert R.dup_isolate_real_roots_sqf(x**2 + x) == [(-1, -1), (0, 0)]
    assert R.dup_isolate_real_roots_sqf(x**2 + x, inf=QQ(+1)) == []
    assert R.dup_isolate_real_roots_sqf(x**2 + x, sup=QQ(-1)) == [(-1, -1)]
    assert R.dup_isolate_real_roots_sqf(x**2 + x, sup=QQ(-2)) == []

    assert R.dup_isolate_real_roots_sqf(x**2 - x) == [( 0,  0), (1, 1)]

    assert R.dup_isolate_real_roots_sqf(x**4 + x + 1) == []

    i = [(-2, -1), (1, 2)]

    assert R.dup_isolate_real_roots_sqf(x**2 - 2) == i
    assert R.dup_isolate_real_roots_sqf(-x**2 + 2) == i

    assert R.dup_isolate_real_roots_sqf(x - 1) == \
        [(1, 1)]
    assert R.dup_isolate_real_roots_sqf(x**2 - 3*x + 2) == \
        [(1, 1), (2, 2)]
    assert R.dup_isolate_real_roots_sqf(x**3 - 6*x**2 + 11*x - 6) == \
        [(1, 1), (2, 2), (3, 3)]
    assert R.dup_isolate_real_roots_sqf(x**4 - 10*x**3 + 35*x**2 - 50*x + 24) == \
        [(1, 1), (2, 2), (3, 3), (4, 4)]
    assert R.dup_isolate_real_roots_sqf(x**5 - 15*x**4 + 85*x**3 - 225*x**2 + 274*x - 120) == \
        [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]

    assert R.dup_isolate_real_roots_sqf(x - 10) == \
        [(10, 10)]
    assert R.dup_isolate_real_roots_sqf(x**2 - 30*x + 200) == \
        [(10, 10), (20, 20)]
    assert R.dup_isolate_real_roots_sqf(x**3 - 60*x**2 + 1100*x - 6000) == \
        [(10, 10), (20, 20), (30, 30)]
    assert R.dup_isolate_real_roots_sqf(x**4 - 100*x**3 + 3500*x**2 - 50000*x + 240000) == \
        [(10, 10), (20, 20), (30, 30), (40, 40)]
    assert R.dup_isolate_real_roots_sqf(x**5 - 150*x**4 + 8500*x**3 - 225000*x**2 + 2740000*x - 12000000) == \
        [(10, 10), (20, 20), (30, 30), (40, 40), (50, 50)]

    assert R.dup_isolate_real_roots_sqf(x + 1) == \
        [(-1, -1)]
    assert R.dup_isolate_real_roots_sqf(x**2 + 3*x + 2) == \
        [(-2, -2), (-1, -1)]
    assert R.dup_isolate_real_roots_sqf(x**3 + 6*x**2 + 11*x + 6) == \
        [(-3, -3), (-2, -2), (-1, -1)]
    assert R.dup_isolate_real_roots_sqf(x**4 + 10*x**3 + 35*x**2 + 50*x + 24) == \
        [(-4, -4), (-3, -3), (-2, -2), (-1, -1)]
    assert R.dup_isolate_real_roots_sqf(x**5 + 15*x**4 + 85*x**3 + 225*x**2 + 274*x + 120) == \
        [(-5, -5), (-4, -4), (-3, -3), (-2, -2), (-1, -1)]

    assert R.dup_isolate_real_roots_sqf(x + 10) == \
        [(-10, -10)]
    assert R.dup_isolate_real_roots_sqf(x**2 + 30*x + 200) == \
        [(-20, -20), (-10, -10)]
    assert R.dup_isolate_real_roots_sqf(x**3 + 60*x**2 + 1100*x + 6000) == \
        [(-30, -30), (-20, -20), (-10, -10)]
    assert R.dup_isolate_real_roots_sqf(x**4 + 100*x**3 + 3500*x**2 + 50000*x + 240000) == \
        [(-40, -40), (-30, -30), (-20, -20), (-10, -10)]
    assert R.dup_isolate_real_roots_sqf(x**5 + 150*x**4 + 8500*x**3 + 225000*x**2 + 2740000*x + 12000000) == \
        [(-50, -50), (-40, -40), (-30, -30), (-20, -20), (-10, -10)]

    assert R.dup_isolate_real_roots_sqf(x**2 - 5) == [(-3, -2), (2, 3)]
    assert R.dup_isolate_real_roots_sqf(x**3 - 5) == [(1, 2)]
    assert R.dup_isolate_real_roots_sqf(x**4 - 5) == [(-2, -1), (1, 2)]
    assert R.dup_isolate_real_roots_sqf(x**5 - 5) == [(1, 2)]
    assert R.dup_isolate_real_roots_sqf(x**6 - 5) == [(-2, -1), (1, 2)]
    assert R.dup_isolate_real_roots_sqf(x**7 - 5) == [(1, 2)]
    assert R.dup_isolate_real_roots_sqf(x**8 - 5) == [(-2, -1), (1, 2)]
    assert R.dup_isolate_real_roots_sqf(x**9 - 5) == [(1, 2)]

    assert R.dup_isolate_real_roots_sqf(x**2 - 1) == \
        [(-1, -1), (1, 1)]
    assert R.dup_isolate_real_roots_sqf(x**3 + 2*x**2 - x - 2) == \
        [(-2, -2), (-1, -1), (1, 1)]
    assert R.dup_isolate_real_roots_sqf(x**4 - 5*x**2 + 4) == \
        [(-2, -2), (-1, -1), (1, 1), (2, 2)]
    assert R.dup_isolate_real_roots_sqf(x**5 + 3*x**4 - 5*x**3 - 15*x**2 + 4*x + 12) == \
        [(-3, -3), (-2, -2), (-1, -1), (1, 1), (2, 2)]
    assert R.dup_isolate_real_roots_sqf(x**6 - 14*x**4 + 49*x**2 - 36) == \
        [(-3, -3), (-2, -2), (-1, -1), (1, 1), (2, 2), (3, 3)]
    assert R.dup_isolate_real_roots_sqf(2*x**7 + x**6 - 28*x**5 - 14*x**4 + 98*x**3 + 49*x**2 - 72*x - 36) == \
        [(-3, -3), (-2, -2), (-1, -1), (-1, 0), (1, 1), (2, 2), (3, 3)]
    assert R.dup_isolate_real_roots_sqf(4*x**8 - 57*x**6 + 210*x**4 - 193*x**2 + 36) == \
        [(-3, -3), (-2, -2), (-1, -1), (-1, 0), (0, 1), (1, 1), (2, 2), (3, 3)]

    f = 9*x**2 - 2

    assert R.dup_isolate_real_roots_sqf(f) == \
        [(-1, 0), (0, 1)]

    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 10)) == \
        [(QQ(-1, 2), QQ(-3, 7)), (QQ(3, 7), QQ(1, 2))]
    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 100)) == \
        [(QQ(-9, 19), QQ(-8, 17)), (QQ(8, 17), QQ(9, 19))]
    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 1000)) == \
        [(QQ(-33, 70), QQ(-8, 17)), (QQ(8, 17), QQ(33, 70))]
    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 10000)) == \
        [(QQ(-33, 70), QQ(-107, 227)), (QQ(107, 227), QQ(33, 70))]
    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 100000)) == \
        [(QQ(-305, 647), QQ(-272, 577)), (QQ(272, 577), QQ(305, 647))]
    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 1000000)) == \
        [(QQ(-1121, 2378), QQ(-272, 577)), (QQ(272, 577), QQ(1121, 2378))]

    f = 200100012*x**5 - 700390052*x**4 + 700490079*x**3 - 200240054*x**2 + 40017*x - 2

    assert R.dup_isolate_real_roots_sqf(f) == \
        [(0, QQ(1, 10002)), (QQ(1, 10002), QQ(1, 10002)),
         (QQ(1, 2), QQ(1, 2)), (1, 1), (2, 2)]

    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 100000)) == \
        [(QQ(1, 10003), QQ(1, 10003)), (QQ(1, 10002), QQ(1, 10002)),
         (QQ(1, 2), QQ(1, 2)), (1, 1), (2, 2)]

    a, b, c, d = 10000090000001, 2000100003, 10000300007, 10000005000008

    f = 20001600074001600021*x**4 \
        + 1700135866278935491773999857*x**3 \
        - 2000179008931031182161141026995283662899200197*x**2 \
        - 800027600594323913802305066986600025*x \
        + 100000950000540000725000008

    assert R.dup_isolate_real_roots_sqf(f) == \
        [(-a, -a), (-1, 0), (0, 1), (d, d)]

    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 100000000000)) == \
        [(-QQ(a), -QQ(a)), (-QQ(1, b), -QQ(1, b)), (QQ(1, c), QQ(1, c)), (QQ(d), QQ(d))]

    (u, v), B, C, (s, t) = R.dup_isolate_real_roots_sqf(f, fast=True)

    assert u < -a < v and B == (-1, 0) and C == (0, 1) and s < d < t

    assert R.dup_isolate_real_roots_sqf(f, fast=True, eps=QQ(1, 100000000000000000000000000000)) == \
        [(-QQ(a), -QQ(a)), (-QQ(1, b), -QQ(1, b)), (QQ(1, c), QQ(1, c)), (QQ(d), QQ(d))]

    f = -10*x**4 + 8*x**3 + 80*x**2 - 32*x - 160

    assert R.dup_isolate_real_roots_sqf(f) == \
        [(-2, -2), (-2, -1), (2, 2), (2, 3)]

    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 100)) == \
        [(-2, -2), (-QQ(23, 14), -QQ(18, 11)), (2, 2), (QQ(39, 16), QQ(22, 9))]

    f = x - 1

    assert R.dup_isolate_real_roots_sqf(f, inf=2) == []
    assert R.dup_isolate_real_roots_sqf(f, sup=0) == []

    assert R.dup_isolate_real_roots_sqf(f) == [(1, 1)]
    assert R.dup_isolate_real_roots_sqf(f, inf=1) == [(1, 1)]
    assert R.dup_isolate_real_roots_sqf(f, sup=1) == [(1, 1)]
    assert R.dup_isolate_real_roots_sqf(f, inf=1, sup=1) == [(1, 1)]

    f = x**2 - 2

    assert R.dup_isolate_real_roots_sqf(f, inf=QQ(7, 4)) == []
    assert R.dup_isolate_real_roots_sqf(f, inf=QQ(7, 5)) == [(QQ(7, 5), QQ(3, 2))]
    assert R.dup_isolate_real_roots_sqf(f, sup=QQ(7, 5)) == [(-2, -1)]
    assert R.dup_isolate_real_roots_sqf(f, sup=QQ(7, 4)) == [(-2, -1), (1, QQ(3, 2))]
    assert R.dup_isolate_real_roots_sqf(f, sup=-QQ(7, 4)) == []
    assert R.dup_isolate_real_roots_sqf(f, sup=-QQ(7, 5)) == [(-QQ(3, 2), -QQ(7, 5))]
    assert R.dup_isolate_real_roots_sqf(f, inf=-QQ(7, 5)) == [(1, 2)]
    assert R.dup_isolate_real_roots_sqf(f, inf=-QQ(7, 4)) == [(-QQ(3, 2), -1), (1, 2)]

    i = [(-2, -1), (1, 2)]

    assert R.dup_isolate_real_roots_sqf(f, inf=-2) == i
    assert R.dup_isolate_real_roots_sqf(f, sup=+2) == i

    assert R.dup_isolate_real_roots_sqf(f, inf=-2, sup=2) == i

    assert R.dup_isolate_real_roots_sqf(f, inf=+1) == [(+1, +2)]
    assert R.dup_isolate_real_roots_sqf(f, sup=-1) == [(-2, -1)]

    R, x = ring("x", QQ)
    f = 8*x**2/5 - 87374*x/3855 - QQ(17, 771)

    assert R.dup_isolate_real_roots_sqf(f) == [(-1, 0), (14, 15)]
    assert [_.as_tuple() for _ in R.dup_isolate_real_roots_sqf(f, blackbox=True)] == [(-1, 0), (14, 15)]

    R, x = ring("x", EX)
    pytest.raises(DomainError, lambda: R.dup_isolate_real_roots_sqf(x + 3))

    R, x = ring("x", QQ.algebraic_field(I))
    f = (x - 1)*(x**3 + I*x - 2)

    assert R.dup_isolate_real_roots_sqf(f) == [(1, 1)]
    assert R.dup_isolate_real_roots_sqf(f, sup=0) == []

    f = (x**2 - 2)*(x**3 - x + I)

    assert R.dup_isolate_real_roots_sqf(f) == [(QQ(-3, 2), QQ(-4, 3)), (QQ(4, 3), QQ(3, 2))]
    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 10), inf=0) == [(QQ(7, 5), QQ(10, 7))]

    assert R.dup_isolate_real_roots_sqf(x) == [(0, 0)]
    assert R.dup_isolate_real_roots_sqf(x - 1) == [(1, 1)]
    assert R.dup_isolate_real_roots_sqf(x - I) == []

    R, x = ring("x", QQ.algebraic_field(sqrt(2)))

    f = (-x**3 + sqrt(2)*x - 1)*(x**2 + 1)

    assert R.dup_isolate_real_roots_sqf(f) == [(-2, -1)]
    assert R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 1000)) == [(QQ(-74, 51), QQ(-29, 20))]

    f = (x - sqrt(2))*(x + 2*sqrt(2))*(x - 7 + sqrt(2))*(x + 3*sqrt(2))*(x - 1)*(x + 1 - sqrt(2))

    assert R.dup_isolate_real_roots_sqf(f) == [(-5, -4), (-3, -2), (0, 1),
                                               (1, 1), (1, 2), (5, 6)]

    R, x = ring("x", QQ.algebraic_field(sqrt(2), sqrt(3)))

    f = (x - sqrt(2))*(x - sqrt(3))*(x - 2*sqrt(6))*(x - sqrt(6))*(x**2 + 2)

    assert R.dup_isolate_real_roots_sqf(f) == [(1, QQ(3, 2)), (QQ(3, 2), 2),
                                               (2, 3), (4, 5)]
    assert (R.dup_isolate_real_roots_sqf(f, eps=QQ(1, 1000)) ==
            [(QQ(41, 29), QQ(58, 41)), (QQ(71, 41), QQ(97, 56)),
             (QQ(169, 69), QQ(49, 20)), (QQ(436, 89), QQ(485, 99))])


def test_dup_isolate_real_roots():
    R, x = ring("x", ZZ)

    assert R.dup_isolate_real_roots(0) == []
    assert R.dup_isolate_real_roots(3) == []

    assert R.dup_isolate_real_roots(5*x) == [((0, 0), 1)]
    assert R.dup_isolate_real_roots(7*x**4) == [((0, 0), 4)]

    assert R.dup_isolate_real_roots(x**2 + x) == [((-1, -1), 1), ((0, 0), 1)]
    assert R.dup_isolate_real_roots(x**2 - x) == [((0, 0), 1), ((1, 1), 1)]

    assert R.dup_isolate_real_roots(x**4 + x + 1) == []

    i = [((-2, -1), 1), ((1, 2), 1)]

    assert R.dup_isolate_real_roots(x**2 - 2) == i
    assert R.dup_isolate_real_roots(-x**2 + 2) == i

    f = 16*x**14 - 96*x**13 + 24*x**12 + 936*x**11 - 1599*x**10 - 2880*x**9 + 9196*x**8 \
        + 552*x**7 - 21831*x**6 + 13968*x**5 + 21690*x**4 - 26784*x**3 - 2916*x**2 + 15552*x - 5832
    g = R.dmp_sqf_part(f)

    assert R.dup_isolate_real_roots(f) == \
        [((-2, -QQ(3, 2)), 2), ((-QQ(3, 2), -QQ(1, 1)), 3), ((1, QQ(3, 2)), 3),
         ((QQ(3, 2), QQ(3, 2)), 4), ((QQ(5, 3), 2), 2)]

    assert R.dup_isolate_real_roots_sqf(g) == \
        [(-2, -QQ(3, 2)), (-QQ(3, 2), -QQ(1, 1)), (1, QQ(3, 2)),
         (QQ(3, 2), QQ(3, 2)), (QQ(3, 2), 2)]
    assert R.dup_isolate_real_roots(g) == \
        [((-2, -QQ(3, 2)), 1), ((-QQ(3, 2), -QQ(1, 1)), 1), ((1, QQ(3, 2)), 1),
         ((QQ(3, 2), QQ(3, 2)), 1), ((QQ(3, 2), 2), 1)]

    f = x - 1

    assert R.dup_isolate_real_roots(f, inf=2) == []
    assert R.dup_isolate_real_roots(f, sup=0) == []

    assert R.dup_isolate_real_roots(f) == [((1, 1), 1)]
    assert R.dup_isolate_real_roots(f, inf=1) == [((1, 1), 1)]
    assert R.dup_isolate_real_roots(f, sup=1) == [((1, 1), 1)]
    assert R.dup_isolate_real_roots(f, inf=1, sup=1) == [((1, 1), 1)]

    f = x**4 - 4*x**2 + 4

    assert R.dup_isolate_real_roots(f, inf=QQ(7, 4)) == []
    assert R.dup_isolate_real_roots(f, inf=QQ(7, 5)) == [((QQ(7, 5), QQ(3, 2)), 2)]
    assert R.dup_isolate_real_roots(f, sup=QQ(7, 5)) == [((-2, -1), 2)]
    assert R.dup_isolate_real_roots(f, sup=QQ(7, 4)) == [((-2, -1), 2), ((1, QQ(3, 2)), 2)]
    assert R.dup_isolate_real_roots(f, sup=-QQ(7, 4)) == []
    assert R.dup_isolate_real_roots(f, sup=-QQ(7, 5)) == [((-QQ(3, 2), -QQ(7, 5)), 2)]
    assert R.dup_isolate_real_roots(f, inf=-QQ(7, 5)) == [((1, 2), 2)]
    assert R.dup_isolate_real_roots(f, inf=-QQ(7, 4)) == [((-QQ(3, 2), -1), 2), ((1, 2), 2)]

    i = [((-2, -1), 2), ((1, 2), 2)]

    assert R.dup_isolate_real_roots(f, inf=-2) == i
    assert R.dup_isolate_real_roots(f, sup=+2) == i

    assert R.dup_isolate_real_roots(f, inf=-2, sup=2) == i

    f = x**11 - 3*x**10 - x**9 + 11*x**8 - 8*x**7 - 8*x**6 + 12*x**5 - 4*x**4

    assert R.dup_isolate_real_roots(f) == \
        [((-2, -1), 2), ((0, 0), 4), ((1, 1), 3), ((1, 2), 2)]

    f = x**45 - 45*x**44 + 990*x**43 - 1
    g = (x**46 - 15180*x**43 + 9366819*x**40 - 53524680*x**39 + 260932815*x**38 - 1101716330*x**37 + 4076350421*x**36 - 13340783196*x**35 + 38910617655*x**34 - 101766230790*x**33 + 239877544005*x**32 - 511738760544*x**31 + 991493848554*x**30 - 1749695026860*x**29 + 2818953098830*x**28 - 4154246671960*x**27 + 5608233007146*x**26 - 6943526580276*x**25 + 7890371113950*x**24 - 8233430727600*x**23 + 7890371113950*x**22 - 6943526580276*x**21 + 5608233007146*x**20 - 4154246671960*x**19 + 2818953098830*x**18 - 1749695026860*x**17 + 991493848554*x**16 - 511738760544*x**15 + 239877544005*x**14 - 101766230790*x**13 + 38910617655*x**12 - 13340783196*x**11 + 4076350421*x**10 - 1101716330*x**9 + 260932815*x**8 - 53524680*x**7 + 9366819*x**6 - 1370754*x**5 + 163185*x**4 - 15180*x**3 + 1035*x**2 - 47*x + 1)

    assert R.dup_isolate_real_roots(f*g) == \
        [((0, QQ(1, 2)), 1), ((QQ(2, 3), QQ(3, 4)), 1), ((QQ(3, 4), 1), 1), ((6, 7), 1), ((24, 25), 1)]

    R, x = ring("x", EX)
    pytest.raises(DomainError, lambda: R.dup_isolate_real_roots(x + 3))
    pytest.raises(DomainError, lambda: R.dup_isolate_real_roots((x + 2)*(x + 3)**2))


def test_dup_isolate_imaginary_roots():
    R, x = ring("x", ZZ)

    f = x**2 + 1
    assert R.dup_isolate_imaginary_roots(f) == [((-1, -1), 1), ((1, 1), 1)]


def test_dup_isolate_real_roots_list():
    R, x = ring("x", ZZ)

    assert R.dup_isolate_real_roots_list([x**2 + x, x]) == \
        [((-1, -1), {0: 1}), ((0, 0), {0: 1, 1: 1})]
    assert R.dup_isolate_real_roots_list([x**2 - x, x]) == \
        [((0, 0), {0: 1, 1: 1}), ((1, 1), {0: 1})]

    assert R.dup_isolate_real_roots_list([x + 1, x + 2, x - 1, x + 1, x - 1, x - 1]) == \
        [((-2, -2), {1: 1}), ((-1, -1), {0: 1, 3: 1}), ((1, 1), {2: 1, 4: 1, 5: 1})]

    assert R.dup_isolate_real_roots_list([x + 1, x + 2, x - 1, x + 1, x - 1, x + 2]) == \
        [((-2, -2), {1: 1, 5: 1}), ((-1, -1), {0: 1, 3: 1}), ((1, 1), {2: 1, 4: 1})]

    f, g = x**4 - 4*x**2 + 4, x - 1

    assert R.dup_isolate_real_roots_list([f, g], inf=QQ(7, 4)) == []
    assert R.dup_isolate_real_roots_list([f, g], inf=QQ(7, 5)) == \
        [((QQ(7, 5), QQ(3, 2)), {0: 2})]
    assert R.dup_isolate_real_roots_list([f, g], sup=QQ(7, 5)) == \
        [((-2, -1), {0: 2}), ((1, 1), {1: 1})]
    assert R.dup_isolate_real_roots_list([f, g], sup=QQ(7, 4)) == \
        [((-2, -1), {0: 2}), ((1, 1), {1: 1}), ((1, QQ(3, 2)), {0: 2})]
    assert R.dup_isolate_real_roots_list([f, g], sup=-QQ(7, 4)) == []
    assert R.dup_isolate_real_roots_list([f, g], sup=-QQ(7, 5)) == \
        [((-QQ(3, 2), -QQ(7, 5)), {0: 2})]
    assert R.dup_isolate_real_roots_list([f, g], inf=-QQ(7, 5)) == \
        [((1, 1), {1: 1}), ((1, 2), {0: 2})]
    assert R.dup_isolate_real_roots_list([f, g], inf=-QQ(7, 4)) == \
        [((-QQ(3, 2), -1), {0: 2}), ((1, 1), {1: 1}), ((1, 2), {0: 2})]

    f, g = 2*x**2 - 1, x**2 - 2

    assert R.dup_isolate_real_roots_list([f, g]) == \
        [((-2, -1), {1: 1}), ((-1, 0), {0: 1}),
         ((0, 1), {0: 1}), ((1, 2), {1: 1})]
    assert R.dup_isolate_real_roots_list([f, g], strict=True) == \
        [((-QQ(3, 2), -QQ(4, 3)), {1: 1}), ((-1, -QQ(2, 3)), {0: 1}),
         ((QQ(2, 3), 1), {0: 1}), ((QQ(4, 3), QQ(3, 2)), {1: 1})]

    f, g = x**2 - 2, x**3 - x**2 - 2*x + 2

    assert R.dup_isolate_real_roots_list([f, g]) == \
        [((-2, -1), {1: 1, 0: 1}), ((1, 1), {1: 1}), ((1, 2), {1: 1, 0: 1})]

    f, g = x**3 - 2*x, x**5 - x**4 - 2*x**3 + 2*x**2

    assert R.dup_isolate_real_roots_list([f, g]) == \
        [((-2, -1), {1: 1, 0: 1}), ((0, 0), {0: 1, 1: 2}),
         ((1, 1), {1: 1}), ((1, 2), {1: 1, 0: 1})]

    f, g = x**9 - 3*x**8 - x**7 + 11*x**6 - 8*x**5 - 8*x**4 + 12*x**3 - 4*x**2, x**5 - 2*x**4 + 3*x**3 - 4*x**2 + 2*x

    assert R.dup_isolate_real_roots_list([f, g], basis=False) == \
        [((-2, -1), {0: 2}), ((0, 0), {0: 2, 1: 1}), ((1, 1), {0: 3, 1: 2}), ((1, 2), {0: 2})]
    assert R.dup_isolate_real_roots_list([f, g], basis=True) == \
        [((-2, -1), {0: 2}, [1, 0, -2]), ((0, 0), {0: 2, 1: 1}, [1, 0]),
         ((1, 1), {0: 3, 1: 2}, [1, -1]), ((1, 2), {0: 2}, [1, 0, -2])]

    R, x = ring("x", EX)
    pytest.raises(DomainError, lambda: R.dup_isolate_real_roots_list([x + 3]))


def test_dup_isolate_real_roots_list_QQ():
    R, x = ring("x", ZZ)

    f = x**5 - 200
    g = x**5 - 201

    assert R.dup_isolate_real_roots_list([f, g]) == \
        [((QQ(75, 26), QQ(101, 35)), {0: 1}), ((QQ(309, 107), QQ(26, 9)), {1: 1})]

    R, x = ring("x", QQ)

    f = -x**5/200 + 1
    g = -x**5/201 + 1

    assert R.dup_isolate_real_roots_list([f, g]) == \
        [((QQ(75, 26), QQ(101, 35)), {0: 1}), ((QQ(309, 107), QQ(26, 9)), {1: 1})]


def test_dup_count_real_roots():
    R, x = ring("x", ZZ)

    assert R.dup_count_real_roots(0) == 0
    assert R.dup_count_real_roots(7) == 0

    f = x - 1
    assert R.dup_count_real_roots(f) == 1
    assert R.dup_count_real_roots(f, inf=1) == 1
    assert R.dup_count_real_roots(f, sup=0) == 0
    assert R.dup_count_real_roots(f, sup=1) == 1
    assert R.dup_count_real_roots(f, inf=0, sup=1) == 1
    assert R.dup_count_real_roots(f, inf=0, sup=2) == 1
    assert R.dup_count_real_roots(f, inf=1, sup=2) == 1

    f = x**2 - 2
    assert R.dup_count_real_roots(f) == 2
    assert R.dup_count_real_roots(f, sup=0) == 1
    assert R.dup_count_real_roots(f, inf=-1, sup=1) == 0

    R, x = ring("x", QQ.algebraic_field(I))

    f = x**3 + I*x + 2
    assert R.dup_count_real_roots(f) == 0

    f *= x**2 - 1
    assert R.dup_count_real_roots(f) == 2


# parameters for test_dup_count_complex_roots_n(): n = 1..8
a, b = (-QQ(1), -QQ(1)), (QQ(1), QQ(1))
c, d = ( QQ(0),  QQ(0)), (QQ(1), QQ(1))


def test_dup_count_complex_roots_1():
    R, x = ring("x", ZZ)

    f = x - 1
    assert R.dup_count_complex_roots(f, a, b) == 1
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = 1 - x
    assert R.dup_count_complex_roots(f, a, b) == 1
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = x + 1
    assert R.dup_count_complex_roots(f, a, b) == 1
    assert R.dup_count_complex_roots(f, c, d) == 0

    R, x = ring("x", QQ)

    f = x - QQ(1, 2)
    assert R.dup_count_complex_roots(f, c, d) == 1

    R, x = ring("x", EX)
    pytest.raises(DomainError, lambda: R.dup_count_complex_roots(x))


def test_dup_count_complex_roots_2():
    R, x = ring("x", ZZ)

    f = (x - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = (x - 1)*(-x)
    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = (x + 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = (x + 1)*(-x)
    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 1


def test_dup_count_complex_roots_3():
    R, x = ring("x", ZZ)

    f = x**2 - 1
    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = (x**2 - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = (x**2 - 1)*(-x)
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 2


def test_dup_count_complex_roots_4():
    R, x = ring("x", ZZ)

    f = x**2 + 1
    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = (x**2 + 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = (x**2 + 1)*(-x)
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = (x**2 + 1)*(x - 1)
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = (x**2 + 1)*(x - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 3

    f = (x**2 + 1)*(x - 1)*(-x)
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 3

    f = (x**2 + 1)*(x**2 - 1)
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = (x**2 + 1)*(x**2 - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 5
    assert R.dup_count_complex_roots(f, c, d) == 3

    f = (x**2 + 1)*(x**2 - 1)*(-x)
    assert R.dup_count_complex_roots(f, a, b) == 5
    assert R.dup_count_complex_roots(f, c, d) == 3


def test_dup_count_complex_roots_5():
    R, x = ring("x", ZZ)

    f = (x + 1)**2 + 1
    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 0

    f = ((x + 1)**2 + 1)*(x - 1)
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x + 1)**2 + 1)*(x - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = ((x + 1)**2 + 1)*(x + 1)
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 0

    f = ((x + 1)**2 + 1)*(x + 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x + 1)**2 + 1)*(x**2 - 1)
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x + 1)**2 + 1)*(x**2 - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 5
    assert R.dup_count_complex_roots(f, c, d) == 2


def test_dup_count_complex_roots_6():
    R, x = ring("x", ZZ)

    f = (x - 1)**2 + 1
    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x - 1)**2 + 1)*(x - 1)
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = ((x - 1)**2 + 1)*(x - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 3

    f = ((x - 1)**2 + 1)*(x + 1)
    assert R.dup_count_complex_roots(f, a, b) == 3
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x - 1)**2 + 1)*(x + 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = ((x - 1)**2 + 1)*(x**2 - 1)
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = ((x - 1)**2 + 1)*(x**2 - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 5
    assert R.dup_count_complex_roots(f, c, d) == 3


def test_dup_count_complex_roots_7():
    R, x = ring("x", ZZ)

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x - 2)
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x**2 - 2)
    assert R.dup_count_complex_roots(f, a, b) == 4
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x - 1)
    assert R.dup_count_complex_roots(f, a, b) == 5
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 6
    assert R.dup_count_complex_roots(f, c, d) == 3

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x + 1)
    assert R.dup_count_complex_roots(f, a, b) == 5
    assert R.dup_count_complex_roots(f, c, d) == 1

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x + 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 6
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x**2 - 1)
    assert R.dup_count_complex_roots(f, a, b) == 6
    assert R.dup_count_complex_roots(f, c, d) == 2

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x**2 - 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 7
    assert R.dup_count_complex_roots(f, c, d) == 3

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x**2 - 1)*(x**2 + 1)
    assert R.dup_count_complex_roots(f, a, b) == 8
    assert R.dup_count_complex_roots(f, c, d) == 3


def test_dup_count_complex_roots_8():
    R, x = ring("x", ZZ)

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x**2 - 1)*(x**2 + 1)*x
    assert R.dup_count_complex_roots(f, a, b) == 9
    assert R.dup_count_complex_roots(f, c, d) == 4

    f = ((x - 1)**2 + 1)*((x + 1)**2 + 1)*(x**2 - 1)*(x**2 + 1)*(x**2 - 2)*x
    assert R.dup_count_complex_roots(f, a, b) == 9
    assert R.dup_count_complex_roots(f, c, d) == 4


def test_dup_count_complex_roots_9():
    R, x = ring("x", QQ.algebraic_field(sqrt(2)))

    f = -x**3 + sqrt(2)*x - 1

    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 1

    R, x = ring("x", QQ.algebraic_field(sqrt(2)).algebraic_field(I))

    f = -x**3 + I*x**2 + sqrt(2)*x - 1

    assert R.dup_count_complex_roots(f, a, b) == 2
    assert R.dup_count_complex_roots(f, c, d) == 1


def test_dup_count_complex_roots_implicit():
    R, x = ring("x", ZZ)

    f = (x**2 + 1)*(x**2 - 1)*x

    assert R.dup_count_complex_roots(f) == 5

    assert R.dup_count_complex_roots(f, sup=(0, 0)) == 3
    assert R.dup_count_complex_roots(f, inf=(0, 0)) == 3

    assert R.dup_count_complex_roots(f, inf=QQ(-2), sup=QQ(-1)) == 1


def test_dup_count_complex_roots_exclude():
    R, x = ring("x", ZZ)

    f = (x**2 + 1)*(x**2 - 1)*x

    a, b = (-QQ(1), QQ(0)), (QQ(1), QQ(1))

    assert R.dup_count_complex_roots(f, a, b) == 4

    assert R.dup_count_complex_roots(f, a, b, exclude=['S']) == 3
    assert R.dup_count_complex_roots(f, a, b, exclude=['N']) == 3

    assert R.dup_count_complex_roots(f, a, b, exclude=['S', 'N']) == 2

    assert R.dup_count_complex_roots(f, a, b, exclude=['E']) == 4
    assert R.dup_count_complex_roots(f, a, b, exclude=['W']) == 4

    assert R.dup_count_complex_roots(f, a, b, exclude=['E', 'W']) == 4

    assert R.dup_count_complex_roots(f, a, b, exclude=['N', 'S', 'E', 'W']) == 2

    assert R.dup_count_complex_roots(f, a, b, exclude=['SW']) == 3
    assert R.dup_count_complex_roots(f, a, b, exclude=['SE']) == 3

    assert R.dup_count_complex_roots(f, a, b, exclude=['SW', 'SE']) == 2
    assert R.dup_count_complex_roots(f, a, b, exclude=['SW', 'SE', 'S']) == 1
    assert R.dup_count_complex_roots(f, a, b, exclude=['SW', 'SE', 'S', 'N']) == 0

    a, b = (QQ(0), QQ(0)), (QQ(1), QQ(1))

    assert R.dup_count_complex_roots(f, a, b, exclude=True) == 1

    R, x = ring("x", QQ.algebraic_field(I))

    f = x**4 + I*x**3 - x + 1

    assert R.dup_count_complex_roots(f, inf=(QQ(0), QQ(0)), sup=(QQ(1), QQ(1))) == 1

    r = R.dup_isolate_complex_roots_sqf(f)

    assert r == [((QQ(-201, 100), QQ(-201, 100)), (0, 0)),
                 ((QQ(-201, 100), 0), (0, QQ(201, 100))),
                 ((0, QQ(-201, 100)), (QQ(201, 100), 0)),
                 ((0, 0), (QQ(201, 100), QQ(201, 100)))]
    assert all(R.dup_count_complex_roots(f, inf=i, sup=s) == 1
               for i, s in r)


def test_dup_isolate_complex_roots_sqf():
    R, x = ring("x", ZZ)
    f = x**2 - 2*x + 3

    assert R.dup_isolate_complex_roots_sqf(f) == \
        [((0, -6), (6, 0)), ((0, 0), (6, 6))]
    assert [r.as_tuple() for r in R.dup_isolate_complex_roots_sqf(f, blackbox=True)] == \
        [((0, -6), (6, 0)), ((0, 0), (6, 6))]

    assert R.dup_isolate_complex_roots_sqf(f, inf=QQ(1), sup=QQ(3)) == [((1, -3), (3, 0)), ((1, 0), (3, 3))]
    assert R.dup_isolate_complex_roots_sqf(f, inf=(QQ(1), QQ(0)), sup=QQ(3)) == [((1, 0), (3, 3))]
    assert R.dup_isolate_complex_roots_sqf(f, inf=(QQ(1), QQ(-1, 2)), sup=QQ(3)) == [((1, 0), (3, 3))]
    assert R.dup_isolate_complex_roots_sqf(f, inf=(QQ(1), QQ(-3)), sup=(QQ(3), QQ(-1))) == [((1, -2), (3, -1))]
    assert R.dup_isolate_complex_roots_sqf(f, inf=QQ(0), sup=QQ(1, 6)) == []

    assert R.dup_isolate_complex_roots_sqf(R.zero) == []

    pytest.raises(ValueError, lambda: R.dup_isolate_complex_roots_sqf(f, inf=QQ(1), sup=QQ(1)))

    assert R.dup_isolate_complex_roots_sqf(f, eps=QQ(1, 10)) == \
        [((QQ(15, 16), -QQ(3, 2)), (QQ(33, 32), -QQ(45, 32))),
         ((QQ(15, 16), QQ(45, 32)), (QQ(33, 32), QQ(3, 2)))]
    assert R.dup_isolate_complex_roots_sqf(f, eps=QQ(1, 100)) == \
        [((QQ(255, 256), -QQ(363, 256)), (QQ(513, 512), -QQ(723, 512))),
         ((QQ(255, 256), QQ(723, 512)), (QQ(513, 512), QQ(363, 256)))]

    f = 7*x**4 - 19*x**3 + 20*x**2 + 17*x + 20

    assert R.dup_isolate_complex_roots_sqf(f) == \
        [((-QQ(40, 7), -QQ(40, 7)), (0, 0)), ((-QQ(40, 7), 0), (0, QQ(40, 7))),
         ((0, -QQ(40, 7)), (QQ(40, 7), 0)), ((0, 0), (QQ(40, 7), QQ(40, 7)))]

    R, x = ring("x", QQ)

    f = x**2/2 - 3*x/7 + 1
    assert R.dup_isolate_complex_roots_sqf(f) == [((0, -4), (4, 0)), ((0, 0), (4, 4))]

    R, x = ring("x", EX)
    pytest.raises(DomainError,
                  lambda: R.dup_isolate_complex_roots_sqf(x, inf=(QQ(-1), QQ(0)),
                                                          sup=(QQ(1), QQ(1))))

    R, x = ring("x", QQ.algebraic_field(I))

    f = x**4 + I*x**3 - x + 1

    assert R.dup_isolate_complex_roots_sqf(f, inf=(QQ(0), QQ(0)),
                                           sup=(QQ(1), QQ(1))) == [((0, 0), (1, QQ(1, 2)))]
    assert R.dup_isolate_complex_roots_sqf(f, inf=(QQ(0), QQ(0)), sup=(QQ(1), QQ(1)),
                                           eps=QQ(1, 100)) == [((QQ(79, 128), QQ(19, 64)),
                                                                (QQ(5, 8), QQ(39, 128)))]
    assert R.dup_isolate_complex_roots_sqf(f, inf=(QQ(0), QQ(-1)),
                                           sup=(QQ(1), QQ(1))) == [((0, -1), (1, QQ(-1, 2))),
                                                                   ((0, 0), (1, QQ(1, 2)))]
    assert R.dup_isolate_complex_roots_sqf(f, inf=(QQ(0), QQ(-1)), sup=(QQ(1), QQ(1)),
                                           eps=QQ(1, 100)) == [((QQ(79, 128), QQ(19, 64)),
                                                                (QQ(5, 8), QQ(39, 128))),
                                                               ((QQ(45, 64), QQ(-91, 128)),
                                                                (QQ(91, 128), QQ(-45, 64)))]

    g = (x - 1)*f
    assert R.dup_isolate_complex_roots_sqf(g) == [((QQ(-401, 100), QQ(-401, 100)), (0, 0)),
                                                  ((QQ(-401, 100), 0), (0, QQ(401, 100))),
                                                  ((0, QQ(-401, 100)), (QQ(401, 100), 0)),
                                                  ((0, 0), (QQ(401, 100), QQ(401, 100)))]

    f = x**7 + I*x**4 - (2 + I)*x**3 - 3*x + 5

    assert R.dup_isolate_complex_roots_sqf(f) == [((QQ(-1001, 100), 0), (0, QQ(1001, 100))),
                                                  ((QQ(-1001, 400), QQ(-1001, 800)), (QQ(-1001, 800), 0)),
                                                  ((QQ(-1001, 800), QQ(-1001, 800)), (0, 0)),
                                                  ((0, QQ(-1001, 400)), (QQ(1001, 400), QQ(-1001, 800))),
                                                  ((0, QQ(-1001, 800)), (QQ(1001, 400), 0)),
                                                  ((0, 0), (QQ(1001, 400), QQ(1001, 800))),
                                                  ((0, QQ(1001, 800)), (QQ(1001, 400), QQ(1001, 400)))]

    R, x = ring("x", QQ.algebraic_field(sqrt(2)))

    f = -x**3 + sqrt(2)*x - 1

    assert R.dup_isolate_complex_roots_sqf(f) == [((0, QQ(-283, 100)), (QQ(283, 100), 0)),
                                                  ((0, 0), (QQ(283, 100), QQ(283, 100)))]

    R, x = ring("x", QQ.algebraic_field(sqrt(2)).algebraic_field(I))

    f = -x**3 + I*x**2 + sqrt(2)*x - 1

    assert R.dup_isolate_complex_roots_sqf(f) == [((QQ(-283, 100), 0), (0, QQ(283, 100))),
                                                  ((0, QQ(-283, 100)), (QQ(283, 100), 0)),
                                                  ((0, 0), (QQ(283, 100), QQ(283, 100)))]

    R, x = ring("x", EX)
    pytest.raises(DomainError, lambda: R.dup_isolate_complex_roots_sqf(x))


def test_dup_isolate_all_roots_sqf():
    R, x = ring("x", ZZ)
    f = 4*x**4 - x**3 + 2*x**2 + 5*x

    assert R.dup_isolate_all_roots_sqf(f) == \
        ([(-1, 0), (0, 0)],
         [((0, -QQ(5, 2)), (QQ(5, 2), 0)), ((0, 0), (QQ(5, 2), QQ(5, 2)))])

    assert R.dup_isolate_all_roots_sqf(f, eps=QQ(1, 10)) == \
        ([(QQ(-7, 8), QQ(-6, 7)), (0, 0)],
         [((QQ(35, 64), -QQ(35, 32)), (QQ(5, 8), -QQ(65, 64))), ((QQ(35, 64), QQ(65, 64)), (QQ(5, 8), QQ(35, 32)))])

    R, x = ring("x", EX)
    pytest.raises(DomainError, lambda: R.dup_isolate_all_roots_sqf(x, R))


def test_dup_isolate_all_roots():
    R, x = ring("x", ZZ)
    f = 4*x**4 - x**3 + 2*x**2 + 5*x

    assert R.dup_isolate_all_roots(f) == \
        ([((-1, 0), 1), ((0, 0), 1)],
         [(((0, -QQ(5, 2)), (QQ(5, 2), 0)), 1),
          (((0, 0), (QQ(5, 2), QQ(5, 2))), 1)])

    assert R.dup_isolate_all_roots(f, eps=QQ(1, 10)) == \
        ([((QQ(-7, 8), QQ(-6, 7)), 1), ((0, 0), 1)],
         [(((QQ(35, 64), -QQ(35, 32)), (QQ(5, 8), -QQ(65, 64))), 1),
          (((QQ(35, 64), QQ(65, 64)), (QQ(5, 8), QQ(35, 32))), 1)])

    f = x**5 + x**4 - 2*x**3 - 2*x**2 + x + 1
    pytest.raises(NotImplementedError, lambda: R.dup_isolate_all_roots(f))

    D = ZZ.poly_ring("y")
    R, x = ring("x", D)
    y, = D.gens
    f = x**2 + y*x - 1
    pytest.raises(DomainError, lambda: R.dup_isolate_all_roots(f))


def test_RealInterval():
    R, x = ring("x", ZZ)
    f = (x - 1)**2
    pytest.raises(ValueError, lambda: RealInterval((-2, 1), R.to_dense(f),
                                                   R.domain))


def test_ComplexInterval():
    R, x = ring("x", QQ.algebraic_field(I))

    f = x**3 + x + I

    _, r1, r2 = R.dup_isolate_complex_roots_sqf(f, blackbox=True)

    assert r1.is_disjoint(r2) is True
    assert r1.is_disjoint(r2, check_re_refinement=True) is False

    for i in range(4):
        r1, r2 = r1.refine(), r2.refine()

    assert r1.is_disjoint(r2, check_re_refinement=True) is True


def test_diofantissue_745():
    D, y = ring('y', ZZ)
    R, x = ring('x', D)
    pytest.raises(DomainError, lambda: R.dup_count_real_roots(x**7 + y*x + 1))