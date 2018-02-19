#
# 1. take nroots
# 2. rationalize
# 3. shift poly by these roots, get coeffs
# 4. check Rouche crit for some finite eps
# 5. check that circles of R=eps allow sorting of roots
#

import time
from diofant import *
R, x = ring('x', QQ.algebraic_field(I))
#p = x**16 - 4*x**14 + 8*x**12 - 6*x**10 + 10*x**8 + 5*x**4 + 2*x**2 + 1
p = x**18 + 60*x**13 - 4*x**12 - 8000*x**9 + 3600*x**8 - 120*x**7 + 4*x**6 - 240000*x**4 + 16000*x**3 + 16000000
p_e = p.as_expr()
p_nroots = nroots(p_e)
p_nroots_exact = [Rational(re(_)) + I*Rational(im(_)) for _ in p_nroots]

def rouche_crit(poly, root, eps=Rational(1, 10**5)):
    K = poly.ring.domain
    poly = poly.shift(K(root))
    test = sum(eps**n*abs(K.to_diofant(c))*(-1 if n == 1 else 1)
               for n, c in enumerate(reversed(poly.coeffs()))) < 0
    return test

#print(rouche_crit(p, p_nroots_exact[0]))

def is_disjoint(roots, eps=Rational(1, 10**5)):
    for i, a in enumerate(roots):
        for j, b in enumerate(roots):
            if i < j:
                if abs(re(a) - re(b)) < 2*eps and abs(im(a) - im(b)) < 2*eps:
                    return False
    else:
        return True

start = time.time()
p_nroots = nroots(p_e)
p_nroots_exact = [Rational(re(_)) + I*Rational(im(_)) for _ in p_nroots]
end = time.time()
print(end - start)

start = time.time()
#r = R.dup_isolate_all_roots(p)
r = [rouche_crit(p, _) for _ in p_nroots_exact]
end = time.time()
pprint(r)
print(end - start)

start = time.time()
pprint(is_disjoint(p_nroots_exact))
end = time.time()
print(end - start)

R2, x2 = ring('x', QQ)
p2 = R2(p_e)
start = time.time()
r = R2.dup_isolate_complex_roots_sqf(p2)
end = time.time()
pprint(r)
print(end - start)

P_e = Poly(p_e, domain=ZZ)
start = time.time()
r = P_e.all_roots()
end = time.time()
pprint(r)
print(end - start)
