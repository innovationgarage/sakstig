import datetime

def is_str(o):
    return hasattr(o, 'lower')
def is_regexp(o):
    return hasattr(i, 'search')
def is_dict(o):
    return hasattr(o, 'values')
def is_list(o):
    return hasattr(o, '__iter__') and not is_dict(o) and not is_str(o)
def is_set(o):
    return hasattr(o, 'union')
def is_int(o):
    return hasattr(o, 'real') and not hasattr(o, 'is_integer') and not isinstance(o, bool)
def is_float(o):
    return hasattr(o, 'is_integer') and not isinstance(o, bool)
def is_timedelta(o):
    return hasattr(o, 'total_seconds')
def is_datetime(o):
    return hasattr(o, 'year') and hasattr(o, 'hour')
def is_date(o):
    return hasattr(o, 'year') and not hasattr(o, 'hour')
def is_time(o):
    return not hasattr(o, 'year') and hasattr(o, 'hour')    

EPOCH=datetime.datetime(1970,1,1)
MIDNIGHT=datetime.time(0, 0, 0)

class Time(datetime.time):
    def __init__(self, *arg, **kw):
        if len(arg) == 1:
            if is_list(arg[0]):
                arg = arg[0]
            elif is_time(arg[0]):
                arg = self.as_list(arg[0])
            elif is_int(arg[0]) or is_float(arg[0]):
                arg = self.as_list(EPOCH + datetime.timedelta(seconds=arg[0]))
        datetime.time.__init__(self, *arg, **kw)
    def __add__(self, other):
        a = datetime.datetime.combine(EPOCH, self)
        b = other
        if is_time(b):
            b = datetime.datetime.combine(EPOCH, b)
        elif not (is_datetime(b) or is_date(b) or is_timedelta(b)):
            b = TimeOnlyDelta(b)
        return Time(a + b)
    def __sub__(self, other):
        a = datetime.datetime.combine(EPOCH, self)
        b = other
        if is_time(b):
            b = datetime.datetime.combine(EPOCH, b)
        res = a - b
        if is_timedelta(res):
            return TimeOnlyDelta(res)
        else:
            return res.time()
    def as_list(self, t=None):
        if t is None: t = self
        return [t.hour, t.minute, t.second, t.microsecond]
    def as_float(self, t=None):
        if t is None: t = self
        return (datetime.datetime.combine(EPOCH, t)
                -  EPOCH).total_seconds()
            
class Date(datetime.date):
    def __init__(self, *arg, **kw):
        if len(arg) == 1:
            if is_list(arg[0]):
                arg = arg[0]
            elif is_time(arg[0]):
                arg = self.as_list(arg[0])
            elif is_int(arg[0]) or is_float(arg[0]):
                arg = self.as_list(EPOCH + datetime.timedelta(seconds=arg[0]))
        datetime.time.__init__(self, *arg, **kw)
    def as_list(self, d=None):
        if d is None: d = self
        return [d.year, d.month, d.day]
    def as_float(self, d=None):
        if d is None: d = self
        return (datetime.datetime.combine(d, MIDNIGHT)
                -  EPOCH).total_seconds()

class DateTime(datetime.datetime):
    pass

class DateTimeDelta(datetime.timedelta):
    pass

class TimeOnlyDelta(datetime.timedelta):
    def as_list(self):
        tms = int(self.total_seconds() * 1000000)
        ms = tms % 1000000
        tms = tms // 1000000
        s = tms % 60
        tms = tms // 60
        m = tms % 60
        h = (tms // 60) % 24
        return [h, m, s, ms]
