# Array functions

from .. import ast_base_types

class sort(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        kw = {}
        if len(args) > 1:
            kw["key"] = args[1][0]
        return ast_base_types.QuerySet([list(sorted(args[0].flatten(), *kw))])

class reverse(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return ast_base_types.QuerySet([list(reversed(args[0].flatten()))])

class count(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return ast_base_types.QuerySet([len(args[0].flatten())])

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
            res += joiner
            res += item
        return ast_base_types.QuerySet([res])
