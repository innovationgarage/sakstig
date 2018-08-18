# Array functions

from .. import ast_base_types
from .. import queryset
from .. import typeinfo

class sort(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        kw = {}
        if len(args) > 1:
            kw["key"] = lambda a: a[args[1][0]]
        return queryset.QuerySet([list(sorted(args[0].flatten(no_dict=True), **kw))])

class reverse(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([list(reversed(args[0].flatten()))])

def compat_len(item):
    # For compatibility with ObjectPath-ng
    if item in (True, False, None, 0, 1):
        return item
    else:
        return len(item)
    
class count(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda item: compat_len(item))

class _len(count):
    __name__ = "len"

class join(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        items = args[0].flatten()
        if len(args) > 1:
            joiner = args[1][0]
        elif len(items):
            joiner = type(items[0])()
        else:
            joiner = ''
        if len(items) == 0:
            return type(joiner)()
        res = items[0]
        for item in items[1:]:
            res += type(res)(joiner)
            res += type(res)(item)
        return queryset.QuerySet([res])

class keys(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        def result():
            for item in args[0]:
                if typeinfo.is_dict(item):
                    for key in item.keys():
                        yield key
                else:
                    raise ValueError(item)
        return queryset.QuerySet(result())

        
