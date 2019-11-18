import datetime

from .. import ast_base_types
from .. import queryset

class age(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        def pretty_print(d):
            # This stuff is really inconsistent, but we have to copy ObjectPath
            d = d.total_seconds()
            if d >= 365 * 24 * 60 * 60:
                return [int(d) // (365 * 24 * 60 * 60), "year"]
            if d >= 30 * 24 * 60 * 60:
                return [int(d) // (30 * 24 * 60 * 60), "month"]
            if d >= 24 * 60 * 60:
                return [int(d) // (24 * 60 * 60), "day"]
            if d >= 60 * 60:
                return [int(d) // (60 * 60), "hour"]
            if d >= 60:
                return [int(d) // 60, "minute"]
            if int(d) == 1:
                return [int(d), "second"]
            return [int(d), "seconds"]
        if len(args) > 1:
            now = args[1][0]
        else:
            now = datetime.datetime.now(datetime.timezone.utc)
        return queryset.QuerySet([pretty_print(now - ts) for ts in args[0]])
    
class _now(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([datetime.datetime.now(datetime.timezone.utc)])

class toMillis(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda t: int(t.timestamp() * 1000))

