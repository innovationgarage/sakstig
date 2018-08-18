# Misc functions

from .. import ast_base_types
from .. import queryset
from .. import typeinfo
import uuid
try:
    import jsonschema
except:
    jsonschema = None

class _type(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        def t(o):
            if typeinfo.is_str(o):
                return 'str'
            elif typeinfo.is_dict(o):
                return 'object'
            elif typeinfo.is_list(o):
                return 'array'
            else:
                return type(o).__name__.lower()
        return args[0].map(t)

class generateID(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return queryset.QuerySet([str(uuid.uuid4())])

class matches(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        def validate(item):
            for schema in args[1]:
                jsonschema.validate(item, schema)
            return item
        return args[0].map(validate)
