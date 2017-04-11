from diofant import *
from diofant.abc import x, y
#eqs = (x**2 - y - sqrt(2), x**2 + x*y - y**2)
#eqs = (x**2 - y - sqrt(3), x**2 + x*y - y**2)
#r = solve_poly_system(eqs, x, y)
zero = RootOf(y**8 - 6*y**7 + 11*y**6 - 6*y**5 - 13*y**4 + 12*y**3 - 4*y**2 + 4, y, 3)
b = Poly(x - sqrt(2)/2*y**3 + 3*sqrt(2)/2*y**2 + (-sqrt(2)/2 + 2)*y - 1, x, y, domain='QQ<sqrt(2)>')
r = b.eval(y, zero)
pprint(r)
