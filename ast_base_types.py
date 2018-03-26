import functools

class QuerySet(list):
    def execute(self, query):
        import grammar
        import ast
        tree = grammar.grammar.parse(query)
        if not tree.is_valid:
            raise SyntaxError("Malformed query: %s<ERROR>%s\n%s" % (
                query[:tree.pos],
                query[tree.pos:],
                grammar.format_tree(tree.tree)))
        return ast.AST(tree.tree)(self)

class Expr(object):
    def __call__(self, queryset):
        raise NotImplementedError

class Const(Expr):
    def __init__(self, value):
        self.value = value
    def __call__(self, queryset):
        return QuerySet([self.value])
    def __repr__(self):
        return "%s" % self.value

class Registry(type):
    _registry = {}
    def __init__(cls, name, bases, members):
        type.__init__(cls, name, bases, members)
        if 'abstract' not in members:
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
    def __call__(self, queryset):
        raise NotImplementedError
    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(repr(arg) for arg in self.args))

class Function(Op):
    abstract = True
    def __call__(self, queryset):
        raise NotImplementedError
    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(repr(arg) for arg in self.args))

def children(item):
    if hasattr(item, "values"):
        return item.values()
    elif hasattr(item, "__iter__"):
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
    def __call__(self, queryset):
        if self.name == "$":
            return queryset
        elif self.name == "*":
            return QuerySet(child_item
                            for item in queryset
                            for child_item in children(item))
        else:
            return QuerySet(item[self.name] for item in queryset
                            if self.name in item)
    def __repr__(self):
        return "%s" % (self.name,)

class Array(Expr):
    def __init__(self, items):
        self.items = items
    def __call__(self, queryset):
        return [item[0]
                for item in (item(queryset)
                             for item in self.items)
                if item]
    def __repr__(self):
        return "[%s]" % (", ".join(repr(item) for item in self.items),)

class Dict(Expr):
    def __init__(self, items):
        self.items = items
    def __call__(self, queryset):
        return {key[0]: value[0]
                for key, value in ((key(queryset), value(queryset))
                                   for key, value in self.items)
                if key and value}
    def __repr__(self):
        return "{%s}" % (", ".join("%s: %s" % (repr(key), repr(value))
                                               for key, value in self.items),)

class op_path_one(Op):
    def __call__(self, queryset):
        assert isinstance(self.args[1], Name)
        return self.args[1](self.args[0](queryset))

class op_path_multi(Op):
    def __call__(self, queryset):
        assert isinstance(self.args[1], Name)
        return self.args[1](descendants(self.args[0](queryset)))

class MathOp(Op):
    def op(self, a, b):
        raise NotImplementedError
    def __call__(self, queryset):
        def result():
            for a in self.args[0](queryset):
                for b in self.args[1](queryset):
                    yield self.op(a, b)
        return QuerySet(result())

class op_mul_mul(MathOp):
    def op(self, a, b):
        return a * b

class op_mul_div(MathOp):
    def op(self, a, b):
        return a / b
    
class op_add_add(MathOp):
    def op(self, a, b):
        return a + b

class op_add_sub(MathOp):
    def op(self, a, b):
        return a - b

class op_comp_in(MathOp):
    def op(a, b):
        return a in b

class op_comp_is(MathOp):
    def op(self, a, b):
        return a == b

class op_comp_lt(MathOp):
    def op(self, a, b):
        return a < b

class op_comp_gt(MathOp):
    def op(self, a, b):
        return a > b

class op_comp_lte(MathOp):
    def op(self, a, b):
        return a >= b

class op_comp_gte(MathOp):
    def op(self, a, b):
        return a >= b

class op_bool_and(MathOp):
    def op(self, a, b):
        return a and b

class op_bool_or(MathOp):
    def op(self, a, b):
        return a or b

class filter(Op):
    def is_true(self, queryset):
        return queryset and functools.reduce(lambda a, b: a and b, queryset, True)
        
    def __call__(self, queryset):
        queryset = self.args[0](queryset)
        for filter in self.args[1:]:
            queryset = QuerySet(
                item
                for item in queryset
                if self.is_true(filter(QuerySet([item]))))
        return queryset
