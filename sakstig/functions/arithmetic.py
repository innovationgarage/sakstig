# Arithmetic functions

from .. import ast_base_types

class _sum(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return ast_base_types.QuerySet([
            sum(args[0].flatten())])

class _max(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return ast_base_types.QuerySet([
            max(args[0].flatten())])
        
class _min(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return ast_base_types.QuerySet([
            min(args[0].flatten())])

class _avg(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        local_qs = args[0].flatten()
        return ast_base_types.QuerySet([
            float(sum(local_qs)) / len(local_qs)])
