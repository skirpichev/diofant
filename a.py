from diofant import *
from diofant.abc import x, y, z
e = sin(E*10**100 - I/10)
r = e.evalfng(maxn=400)
print(r)
e = sin(E*10**100)
r = e.evalfng(n=20, maxn=500)
print(r)
e = Float('1.3')
print(e.evalfng())
e = (x - 1)*((1 - x))**1000
r = e.evalfng()
print(sstr(r, full_prec=True))
e = (-100000*sqrt(2500000001) + 5000000001)
r = e.evalfng()
print(r)
v = ((-27*12**Rational(1, 3)*sqrt(31)*I +
              27*2**Rational(2, 3)*3**Rational(1, 3)*sqrt(31)*I) /
             (-2511*2**Rational(2, 3)*3**Rational(1, 3) +
              (29*18**Rational(1, 3) +
               9*2**Rational(1, 3)*3**Rational(2, 3)*sqrt(31)*I +
               87*2**Rational(1, 3)*3**Rational(1, 6)*I)**2))
r = v.evalfng()
print(r)
