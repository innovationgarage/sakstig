import functools
import datetime
import re

def is_str(o):
    return hasattr(o, 'lower')
def is_regexp(o):
    return hasattr(i, 'search')
def is_dict(o):
    return hasattr(o, 'values')
def is_list(o):
    return hasattr(o, '__iter__') and not is_dict(o) and not is_str(o)
def is_set(o):
    return hasattr(o, 'union')
def is_int(o):
    return hasattr(o, 'real') and not hasattr(o, 'is_integer') and not isinstance(o, bool)
def is_float(o):
    return hasattr(o, 'is_integer') and not isinstance(o, bool)
def is_timedelta(o):
    return hasattr(o, 'total_seconds')
def is_datetime(o):
    return hasattr(o, 'year') and hasattr(o, 'hour')
def is_date(o):
    return hasattr(o, 'year') and not hasattr(o, 'hour')
def is_time(o):
    return not hasattr(o, 'year') and hasattr(o, 'hour')

def compile(query):
    from . import grammar
    from . import ast
    tree = grammar.grammar.parse(query)
    if not tree.is_valid:
        raise SyntaxError("Malformed query: %s<ERROR>%s\n%s" % (
            query[:tree.pos],
            query[tree.pos:],
            grammar.format_tree(tree.tree)))
    return ast.AST(tree.tree)
    
class QuerySet(list):
    def __repr__(self):
        return "%s\n" % ("\n".join(repr(item) for item in self))

    def execute(self, query, global_qs = None):
        if not isinstance(query, Expr):
            if not isinstance(query, str):
                return QuerySet([query])
            query = compile(query)
        if global_qs is None:
            global_qs = self
        return query(global_qs, None)

    def map(self, fn):
        def map():
            for item in self:
                try:
                    yield fn(item)
                except Exception as e:
                    pass
        return QuerySet(map())

    def flatten(self, children_only=False, no_dict=False):
        def flatten():
            for item in self:
                if is_dict(item):
                    if no_dict:
                        if not children_only:
                            yield item
                    else:
                        for value in item.values():
                            yield value
                elif is_list(item):
                    for value in item:
                        yield value
                elif not children_only:
                    yield item
        return QuerySet(flatten())

    def __add__(self, other):
        return type(self)(list.__add__(self, other))
    
class Expr(object):
    def __call__(self, global_qs, local_qs):
        raise NotImplementedError

class Const(Expr):
    def __init__(self, value):
        self.value = value
    def __call__(self, global_qs, local_qs):
        return QuerySet([self.value])
    def __repr__(self):
        return repr(self.value)

class Registry(type):
    _registry = {}
    def __init__(cls, name, bases, members):
        type.__init__(cls, name, bases, members)
        if 'abstract' not in members:
            if name.startswith("_"):
                name = name[1:]
            if '__name__' in members:
                name = members['__name__']
            cls._registry[name] = cls
    
class Op(Expr, metaclass=Registry):
    abstract = True
    def __new__(cls, name, *args):
        if 'abstract' in cls.__dict__:
            return cls._registry[name](name, *args)
        return Expr.__new__(cls)
    def __init__(self, name, *args):
        self.name = name
        self.args = args
    def __call__(self, global_qs, local_qs):
        raise NotImplementedError
    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(repr(arg) for arg in self.args))

class Function(Op):
    abstract = True
    def __call__(self, global_qs, local_qs):
        return self.call(
            global_qs,
            local_qs,
            [arg(global_qs, local_qs) for arg in self.args])
    def call(self, global_qs, local_qs, args):
        raise NotImplementedError
    
    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(repr(arg) for arg in self.args))

def children(item):
    if is_dict(item):
        return item.values()
    elif is_list(item):
        return iter(item)
    else:
        return []

def descendants(item):
    yield item
    for child in children(item):
        for descendant in descendants(child):
            yield descendant
    
class Name(Expr):
    def __init__(self, name):
        self.name = name
    def __call__(self, global_qs, local_qs):
        if self.name == "$":
            return global_qs
        elif self.name == "@":
            return local_qs        
        elif self.name == "*":
            return local_qs.flatten(children_only=True)
        elif local_qs is None:
            return QuerySet([self.name])
        else:
            return local_qs.map(lambda item: item[self.name])
    def __repr__(self):
        return "%s" % (self.name,)

class Array(Expr):
    def __init__(self, items):
        self.items = items
    def __call__(self, global_qs, local_qs):
        return QuerySet([
            list(QuerySet(item
                          for item in (item(global_qs, local_qs)
                                       for item in self.items)
                          if item).flatten())])
    def __repr__(self):
        return "[%s]" % (", ".join(repr(item) for item in self.items),)

class Dict(Expr):
    def __init__(self, items):
        self.items = items
    def __call__(self, global_qs, local_qs):
        return QuerySet([{key[0]: value[0]
                          for key, value in ((key(global_qs, local_qs), value(global_qs, local_qs))
                                             for key, value in self.items)
                          if key and value}])
    def __repr__(self):
        return "{%s}" % (", ".join("%s: %s" % (repr(key), repr(value))
                                               for key, value in self.items),)

class op_path_one(Op):
    def __call__(self, global_qs, local_qs):
        return self.args[1](global_qs, self.args[0](global_qs, local_qs))

class op_path_multi(Op):
    def __call__(self, global_qs, local_qs):
        assert isinstance(self.args[1], Name)
        return self.args[1](global_qs, QuerySet(descendants(self.args[0](global_qs, local_qs))))

class MathOp(Op):
    abstract = True
    def op(self, a, b):
        raise NotImplementedError
    def __call__(self, global_qs, local_qs):
        def result():
            for a in self.args[0](global_qs, local_qs):
                for b in self.args[1](global_qs, local_qs):
                    yield self._op(a, b)
        return QuerySet(result())
    def _op(self, a, b):
        if a is None:
            if is_dict(b):
                a = {}
            elif is_list(b):
                a = []
            elif is_set(b):
                a = set()
            else:
                a = 0
        if b is None:
            if is_dict(a):
                b = {}
            elif is_list(a):
                b = []
            elif is_set(a):
                b = set()
            else:
                b = 0
        return self.op(a, b)
    
    
class op_mul_mul(MathOp):
    def op(self, a, b):
        return a * b

class op_mul_div(MathOp):
    def op(self, a, b):
        return a / b

class op_mul_mod(MathOp):
    def op(self, a, b):
        return a % b
    
class op_add_add(MathOp):
    def op(self, a, b):
        if not (isinstance(a, int) and isinstance(b, float)):
            b = type(a)(b)
        if is_dict(a) and is_dict(b):
            res = {}
            res.update(a)
            res.update(b)
            return res
        elif is_set(a) and is_set(a):
            return a.union(b)
        return a + b

class op_add_sub(MathOp):
    def op(self, a, b):
        if is_time(a):
            a = datetime.datetime.combine(datetime.datetime(1970,1,1), a)
        if is_time(b):
            b = datetime.datetime.combine(datetime.datetime(1970,1,1), b)
        return a - b

class op_comp_in(MathOp):
    def op(self, a, b):
        return a in b

class op_comp_not_in(MathOp):
    def op(self, a, b):
        return a not in b

class op_comp_is(MathOp):
    def op(self, a, b):
        if a == b:
            return True
        try:
            b = type(a)(b)
        except:
            return False
        return a == b
            
class op_comp_is_not(MathOp):
    def op(self, a, b):
        if a == b:
            return False
        try:
            b = type(a)(b)
        except:
            return True
        return not a == b

class op_comp_lt(MathOp):
    def op(self, a, b):
        return a < b

class op_comp_gt(MathOp):
    def op(self, a, b):
        return a > b

class op_comp_lte(MathOp):
    def op(self, a, b):
        return a <= b

class op_comp_gte(MathOp):
    def op(self, a, b):
        return a >= b

class op_comp_regexp(MathOp):
    def op(self, a, b):
        if is_str(a):
            a = re.compile(a)
        res = a.match(b)
        if not res: return False
        if len(res.groups()) == 0:
            return True
        return res.groups()

class op_bool_and(MathOp):
    def op(self, a, b):
        return a and b

class op_bool_or(MathOp):
    def op(self, a, b):
        return a or b

class nop_expr(Op):
    def __call__(self, global_qs, local_qs):
        def result():
            for a in self.args[0](global_qs, local_qs):
                yield not a
        return QuerySet(result())

class op_union_union(Op):
    def __call__(self, global_qs, local_qs):
        def result():
            for a in self.args[0](global_qs, local_qs):
                yield a
            for b in self.args[1](global_qs, local_qs):
                yield b
        return QuerySet(result())
    
class filter(Op):
    def filter_qs(self, filter, global_qs, local_qs):
        for item in local_qs:
            for filter_res in filter(global_qs, QuerySet([item])):
                if is_int(filter_res) or is_str(filter_res):
                    try:
                        yield item[filter_res]
                    except:
                        pass
                else:
                    if filter_res:
                        yield item
    def __call__(self, global_qs, local_qs):
        local_qs = self.args[0](global_qs, local_qs)
        for filter in self.args[1:]:
            local_qs = QuerySet(self.filter_qs(filter, global_qs, local_qs))
        return local_qs
