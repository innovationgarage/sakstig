# Casting functions

from .. import ast_base_types

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

class _array(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        if not args:
            return ast_base_types.QuerySet([[]])
        return args[0].map(list)
