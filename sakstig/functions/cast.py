# Casting functions

from .. import ast_base_types

class _str(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(str)

class _int(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(int)

class _float(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(float)

class _array(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(list)
