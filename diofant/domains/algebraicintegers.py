import operator

from .domainelement import DomainElement


_maximal_orders_cache = {}


class MaximalOrder(CharacteristicZero, SimpleDomain, Ring):
    is_Numerical = True

    def __new__(cls, alg_field):
        obj = super().__new__()

        obj._field = alg_field
        obj.basis = cls._compute_integral_basis(obj._field)

        try:
            obj.dtype = _maximal_orders_cache[(obj._field)]
        except KeyError:
            obj.dtype = type("OrderElement", (OrderElement,), {"_parent": obj})
            _maximal_orders_cache[(obj._field)] = obj.dtype

        return obj

    @staticmethod
    def _compute_integral_basis(field):
        if field.domain.is_RationalField and field.degree == 2:
            d = field.minpoly.discriminant() // 4
            if d % 4 == 1:
                return [field.one, (1 + field.unit)/2]
            else:
                return [field.one, field.unit]
        raise NotImplementedError("Can't compute the maximal order "
                                  "of %s" % field)


class OrderElement(DomainElement):
    def __init__(self, rep):
        self.rep = list(rep)

    def __neg__(self):
        return self.__class__([-_ for _ in self.rep])

    def __add__(self, other):
        try:
            other = self.parent.convert(other)
        except CoercionFailed:
            return NotImplemented
        return self.__class__(map(operator.add, (self.rep, other.rep)))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        try:
            other = self.parent.convert(other)
        except CoercionFailed:
            return NotImplemented
        return self.__class__(self.rep * other.rep)

    def __rmul__(self, other):
        return self.__mul__(other)
