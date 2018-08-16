# Casting functions

from .. import ast_base_types
import datetime

def comp_str(item):
    if item is True:
        return "true"
    elif item is False:
        return "false"
    elif item is None:
        return "null"
    else:
        return str(item)

class _str(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(comp_str)

class _int(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(int)

class _float(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(float)

def comp_list(item):
    if ast_base_types.is_timedelta(item):
        tms = int(item.total_seconds() * 1000000)
        ms = tms % 1000000
        tms = tms // 1000000
        s = tms % 60
        tms = tms // 60
        m = tms % 60
        h = tms // 60
        return [h, m, s, ms]
    elif ast_base_types.is_datetime(item):
        return [item.year, item.month, item.day, item.hour, item.minute, item.second, item.microsecond]
    elif ast_base_types.is_date(item):
        return [item.year, item.month, item.day]
    elif ast_base_types.is_time(item):
        return [item.hour, item.minute, item.second, item.microsecond]
    else:
        return list(item)
    
class _array(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return ast_base_types.QuerySet([[]])
        return args[0].map(comp_list)

def comp_datetime(item):
    if ast_base_types.is_datetime(item):
        return item
    elif ast_base_types.is_list(item):
        item = list(item)
        item += ([0] * 7)[len(item):] + [datetime.timezone.utc]
        return datetime.datetime(*item)
    elif ast_base_types.is_str(item):
        return datetime.datetime.strptime(item + " +0000", "%Y-%m-%d %H:%M:%S %z")
    
def comp_date(item):
    if ast_base_types.is_date(item):
        return item
    elif ast_base_types.is_datetime(item):
        return item.date()
    elif ast_base_types.is_list(item):
        return datetime.date(*item)
    elif ast_base_types.is_str(item):
        return datetime.datetime.strptime(item, "%Y-%m-%d").date()

def comp_time(item):
    if ast_base_types.is_time(item):
        return item
    elif ast_base_types.is_datetime(item):
        return item.time()
    elif ast_base_types.is_list(item):
        item = list(item)
        item += ([0] * 4)[len(item):] + [datetime.timezone.utc]
        return datetime.time(*item)
    elif ast_base_types.is_str(item):
        return datetime.datetime.strptime(item + " +0000", "%H:%M:%S %z").time()
    
class _dateTime(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return ast_base_types.QuerySet([datetime.datetime.now()])
        elif len(args) == 2:
            return args[1].map(lambda t: datetime.datetime.combine(comp_date(args[0][0]), comp_time(t)))
        return args[0].map(lambda l: comp_datetime(l))

class _date(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return ast_base_types.QuerySet([datetime.date.today()])
        return args[0].map(lambda l: comp_date(l))

class _time(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return ast_base_types.QuerySet([datetime.datetime.now().time()])
        return args[0].map(lambda l: comp_time(l))
