from .. import ast_base_types
from .. import queryset

class keys(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([item.keys() for item in args[0]]).flatten()

class values(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([item.values() for item in args[0]]).flatten()
