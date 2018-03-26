import ast_base_types
import html
import uuid

# Casting functions

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

# Arithmetic functions
    
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

class _round(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        precision = args[1][0]
        return args[0].map(lambda a: round(a, precision))

# String functions
    
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
        return args[0].map(lambda s: s.split(*args[1:]))

class slice(ast_base_types.Function):
    def call(self, global_qs, local_qs, args):
        spec = args[1][0]
        def slice(s):
            if hasattr(spec[0], '__iter__'):
                return [s[item[0]:item[1]]
                        for item in spec]
            else:
                return s[spec[0]:spec[1]]
        return args[0].map(slice)

# Array functions

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

# Date and time functions

# NOT SUPPORTED FOR NOW

# Misc functions

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
