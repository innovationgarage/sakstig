# String functions

from .. import ast_base_types
import html
    
class replace(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda s: s.replace(args[1][0], args[2][0]))

class escape(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(html.escape)

class unescape(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(html.unescape)

class upper(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda s: s.upper())

class lower(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda s: s.lower())

class capitalize(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda s: s.capitalize())

class title(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda s: s.title())

class split(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        return args[0].map(lambda s: s.split(*(arg[0] for arg in args[1:])))

class slice(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        spec = args[1][0]
        if not isinstance(spec, (list, tuple)):
            raise Exception("Second argument to slice must be a list")
        def slice(s):
            if hasattr(spec[0], '__iter__'):
                return [s[item[0]:item[1]]
                        for item in spec]
            else:
                return s[spec[0]:spec[1]]
        return args[0].map(slice)
