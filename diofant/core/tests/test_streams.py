from diofant import *
from diofant.core.containers import Stream


# http://web.mit.edu/kmill/www/programming/tailcall.html

class TailCaller(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, *args, **kwargs):
        ret = self.f(*args, **kwargs)
        while type(ret) is TailCall:
            ret = ret.handle()
        return ret


class TailCall(object):
    def __init__(self, call, *args, **kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs
    def handle(self):
        if type(self.call) is TailCaller:
            return self.call.f(*self.args, **self.kwargs)
        else:
            return self.f(*self.args, **self.kwargs)


def make_integer_stream(first=Integer(1)):
    return Stream(first, lambda: make_integer_stream(first + Integer(1)))


def map_streams(fn, *streams):
    if any(s.empty for s in streams):
        raise NotImplementedError
    return Stream(fn(*[s.first for s in streams]),
                  lambda: map_streams(fn, *[s.rest for s in streams]))


def integrate_stream(s):
    return map_streams(lambda x, y: x/y, s, integers)


def make_exp_series():
    return Stream(Integer(1), lambda: integrate_stream(make_exp_series()))


def make_sine_series():
    return Stream(Integer(0), lambda: integrate_stream(make_cosine_series()))


def make_cosine_series():
    return Stream(Integer(1), lambda:
        map_streams(lambda x: x*Integer(-1),
                              integrate_stream(make_sine_series())))


integers = make_integer_stream()
exp_series = make_exp_series()
sine_series  = make_sine_series()
cosine_series = make_cosine_series()
