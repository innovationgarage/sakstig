# Arithmetic functions

from .. import ast_base_types
from .. import queryset
from .. import ops
import functools

_add_op = ops.op_add_add(None, None)._op
def add_op_cast(a, b):
    try:
        return _add_op(a, b)
    except:
        return a

def min_op(a, b):
    try:
        return a if a < b else b
    except:
        return a

def max_op(a, b):
    try:
        return a if a > b else b
    except:
        return a

def add_op(a, b):
    if a is None:
        return b
    else:
        try:
            return a + b
        except:
            return a

def non_cast_len(lst):
    l = 0
    res = None
    for item in lst:
        if res is None:
            res = item
            if res is not None: l += 1
        else:
            try:
                res + item
                l += 1
            except:
                pass
    return l
    
class _round(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        arg = [x[0] for x in args[1:]]
        return args[0].map(lambda x: round(x, *arg))
    
class _sum(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        local_qs = args[0].flatten()
        if self.context.args.get("aggregate_casts", False):
            op = add_op_cast
        else:
            op = add_op
        return queryset.QuerySet([
            functools.reduce(op, local_qs, None)
        ])

class _max(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([
            functools.reduce(max_op, args[0].flatten())])

class _min(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([
            functools.reduce(min_op, args[0].flatten())])

class _avg(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        local_qs = args[0].flatten()
        if self.context.args.get("aggregate_casts", False):
            op = add_op_cast
            ln = len
        else:
            op = add_op
            ln = non_cast_len
        return queryset.QuerySet([
            float(functools.reduce(op, local_qs, None)) / ln(local_qs)])
