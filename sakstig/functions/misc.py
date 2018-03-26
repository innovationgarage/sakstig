# Misc functions

from .. import ast_base_types
import uuid

class _type(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        def t(o):
            if ast_base_types.is_str(o):
                return 'string'
            elif ast_base_types.is_dict(o):
                return 'object'
            elif ast_base_types.is_list(o):
                return 'array'
            else:
                return type(o).__name__.lower()
        return args[0].map(t)

class generateID(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return ast_base_types.QuerySet([str(uuid.uuid4())])
