# Arithmetic functions

from .. import ast_base_types
from .. import queryset
from .. import ops
import functools

_add_op = ops.op_add_add(None)._op
def add_op(a, b):
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

class _sum(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([
            functools.reduce(add_op, args[0].flatten(), None)
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
        return queryset.QuerySet([
            float(functools.reduce(add_op, local_qs, None)) / len(local_qs)])
