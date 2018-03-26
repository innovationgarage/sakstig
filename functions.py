import ast_base_types

class _str(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        return self.args[0](global_qs, local_qs).map(str)

class _int(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        return self.args[0](global_qs, local_qs).map(int)

class _float(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        return self.args[0](global_qs, local_qs).map(float)

class _array(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        return self.args[0](global_qs, local_qs).map(list)

class _sum(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        return ast_base_types.QuerySet([
            sum(self.args[0](global_qs, local_qs).flatten())])

class _max(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        return ast_base_types.QuerySet([
            max(self.args[0](global_qs, local_qs).flatten())])
        
class _min(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        return ast_base_types.QuerySet([
            min(self.args[0](global_qs, local_qs).flatten())])

class _avg(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        local_qs = self.args[0](global_qs, local_qs).flatten()
        return ast_base_types.QuerySet([
            float(sum(local_qs)) / len(local_qs)])

class _round(ast_base_types.Function):
    def __call__(self, global_qs, local_qs):
        precision = self.args[1](global_qs, local_qs)[0]
        return self.args[0](global_qs, local_qs).map(lambda a: round(a, precision))
