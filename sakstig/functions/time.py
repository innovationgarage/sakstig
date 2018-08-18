import datetime

from .. import ast_base_types

class _now(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return ast_base_types.QuerySet([datetime.datetime.now()])

class toMillis(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda t: int(t.timestamp() * 1000))
