import time
from diofant import *
from diofant.core.cache import clear_cache
from diofant.abc import x

R = ZZ.poly_ring(x)
e = x**7 + x - 1
p = Poly(e)
r = R.from_expr(e)

t1 = time.process_time()
rs = p.all_roots()
rs0 = [_ for _ in rs if _.is_real is False]
t2 = time.process_time()

print(t2 - t1)

clear_cache()

t1 = time.process_time()
rs1 = [_ for _ in p.nroots() if _.is_real is False]
d = oo
for a in rs1:
    for b in rs1:
        if a != b:
            td = abs(a - b)
            if d > td:
                d = td
assert d > 0
eps = 1e-6
de = d*eps
t2 = time.process_time()
newrs = [((QQ.from_expr(re(_) - de), QQ.from_expr(im(_) - de)),
          (QQ.from_expr(re(_) + de), QQ.from_expr(im(_) + de))) for _ in rs1]
rs2 = []
for n in newrs:
    t = R.dup_isolate_complex_roots_sqf(r, inf=n[0], sup=n[1])
    rs2.append(t)
print(t2 - t1)

assert len(rs0) == len(rs2)
