# Array functions

from .. import ast_base_types
from .. import queryset
from .. import typeinfo
import functools
import collections

class sort(ast_base_types.Op):
    def __call__(self, global_qs, local_qs):        
        array = self.args[0](global_qs, local_qs).flatten(no_dict=True)
        kw = {}
        if len(self.args) > 1:
            if isinstance(self.args[1], ast_base_types.Const):
                key = self.args[1](global_qs, local_qs)
                kw["key"] = lambda a: a[key[0]]
            else:
                kw["key"] = lambda a: self.args[1](global_qs, queryset.QuerySet([a]))[0]
        return queryset.QuerySet([list(sorted(array, **kw))])
    
    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(repr(arg) for arg in self.args))

class reverse(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([list(reversed(args[0].flatten()))])

class unique(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([list(collections.OrderedDict.fromkeys(args[0].flatten()))])
    
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

class _map(ast_base_types.Op):
    __name__ = "map"
    def __call__(self, global_qs, local_qs):
        fn = self.args[0]
        if isinstance(fn, ast_base_types.Name):
            fn = ast_base_types.Function(
                self.context, fn.name,
                ast_base_types.Name(self.context, "@"))
        array = self.args[1](global_qs, local_qs).flatten(no_dict=True)
        return queryset.QuerySet([
            list(queryset.QuerySet(item
                          for item in (fn(global_qs, queryset.QuerySet([item]))
                                       for item in array)
                          if item).flatten())])
    
    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(repr(arg) for arg in self.args))

class _reduce(ast_base_types.Op):
    __name__ = "reduce"
    def __call__(self, global_qs, local_qs):
        array = self.args[0](global_qs, local_qs).flatten(no_dict=True)

        initial = []
        if len(self.args) > 2:
            initial = [self.args[2](global_qs, local_qs).flatten(no_dict=True)]

        def reducer(a, b):
            if isinstance(a, queryset.QuerySet):
                a = list(a)
            else:
                a = [a]
            arg = queryset.QuerySet([a + [b]])
            return self.args[1](global_qs, arg)
            
        return functools.reduce(reducer, array, *initial)
    
    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(repr(arg) for arg in self.args))
