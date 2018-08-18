import functools
import datetime
import re
from .queryset import QuerySet
from . import typeinfo

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
    if typeinfo.is_dict(item):
        return item.values()
    elif typeinfo.is_list(item):
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

