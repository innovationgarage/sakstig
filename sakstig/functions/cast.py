# Casting functions

from .. import ast_base_types
from .. import queryset
from .. import typeinfo
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
    if hasattr(item, "as_list"):
        return item.as_list()
    elif typeinfo.is_timedelta(item):
        return item.total_seconds()
    elif typeinfo.is_datetime(item):
        return [item.year, item.month, item.day, item.hour, item.minute, item.second, item.microsecond]
    elif typeinfo.is_date(item):
        return [item.year, item.month, item.day]
    elif typeinfo.is_time(item):
        return [item.hour, item.minute, item.second, item.microsecond]
    else:
        return list(item)
    
class _array(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return queryset.QuerySet([[]])
        return args[0].map(comp_list)

def comp_datetime(item):
    if typeinfo.is_datetime(item):
        return item
    elif typeinfo.is_list(item):
        item = list(item)
        item += ([0] * 7)[len(item):] + [datetime.timezone.utc]
        return datetime.datetime(*item)
    elif typeinfo.is_str(item):
        return datetime.datetime.strptime(item + " +0000", "%Y-%m-%d %H:%M:%S %z")
    
def comp_date(item):
    if typeinfo.is_date(item):
        return item
    elif typeinfo.is_datetime(item):
        return item.date()
    elif typeinfo.is_list(item):
        return datetime.date(*item)
    elif typeinfo.is_str(item):
        return datetime.datetime.strptime(item, "%Y-%m-%d").date()

def comp_time(item):
    if typeinfo.is_time(item):
        return item
    elif typeinfo.is_datetime(item):
        return item.time()
    elif typeinfo.is_list(item):
        item = list(item)
        item += ([0] * 4)[len(item):] + [datetime.timezone.utc]
        return datetime.time(*item)
    elif typeinfo.is_str(item):
        return datetime.datetime.strptime(item + " +0000", "%H:%M:%S %z").time()
    
class _dateTime(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return queryset.QuerySet([datetime.datetime.now(datetime.timezone.utc)])
        elif len(args) == 2:
            if len(args[1]) == 1 and typeinfo.is_str(args[1][0]):
                return args[0].map(lambda l: datetime.datetime.strptime(l, args[1][0]))
            else:
                return args[1].map(lambda t: datetime.datetime.combine(comp_date(args[0][0]), comp_time(t)))
        return args[0].map(lambda l: comp_datetime(l))

class _date(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return queryset.QuerySet([datetime.date.today()])
        return args[0].map(lambda l: comp_date(l))

class _time(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return queryset.QuerySet([datetime.datetime.now().time()])
        return args[0].map(lambda l: comp_time(l))
