import functools
import datetime
import re
from . import queryset
from . import typeinfo

class Expr(object):
    def __call__(self, global_qs, local_qs):
        raise NotImplementedError

class Const(Expr):
    def __init__(self, context, value):
        self.context = context
        self.value = value
    def __call__(self, global_qs, local_qs):
        return queryset.QuerySet([self.value])
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
    def __new__(cls, context, name, *args):
        if 'abstract' in cls.__dict__:
            return cls._registry[name](context, name, *args)
        return Expr.__new__(cls)
    def __init__(self, context, name, *args):
        self.context = context
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

class ParenExpr(Expr):
    def __init__(self, context, args):
        self.context = context
        self.args = args
    
    def __call__(self, global_qs, local_qs):
        if self.context.args.get("object_slicing", True):
            if not local_qs or local_qs.is_path_multi:
                parent = local_qs
            else:
                parent = local_qs.flatten()
            if isinstance(self.args, Name):
                res = queryset.QuerySet({self.args.name: value}
                                         for value in self.args(global_qs, parent))
                res.is_path_multi = local_qs and local_qs.is_path_multi
                return res
            elif type(self.args).__name__ == "op_union_union":
                res = queryset.QuerySet(
                    item
                    for item in ({matchname: match[0]
                                  for matchname, match in ((name.name, name(global_qs, queryset.QuerySet([value])))
                                                           for name in self.args.args)
                                  if match}
                                 for value in parent)
                    if item
                )
                res.is_path_multi = local_qs and local_qs.is_path_multi
                return res
        return self.args(global_qs, local_qs)
            
    def __repr__(self):
        return "(%s)" % (repr(self.args),)
    
class Name(Expr):
    def __init__(self, context, name):
        self.context = context
        self.name = name
    def __call__(self, global_qs, local_qs):
        if self.name == "$":
            return global_qs
        elif self.name == "@":
            return queryset.QuerySet(local_qs) # Reset any is_filter_qs flags...
        elif self.name == "*":
            if not self.context.args.get('nop_star', True) and not getattr(local_qs, 'is_path_multi', False):
                local_qs = local_qs.flatten(children_only=True)
            return local_qs
        elif self.name == "null":
            return queryset.QuerySet([None])
        elif local_qs is None or getattr(local_qs, "is_filter_qs", False):
            return queryset.QuerySet([self.name])
        else:
            if self.context.args.get("autoflatten_lists", True) and not getattr(local_qs, 'is_path_multi', False):
                local_qs = local_qs.flatten(no_dict=True)
            def get(item):
                try:
                    return item[self.name]
                except:
                    return getattr(item, self.name)
            return local_qs.map(get)
    def __repr__(self):
        return "%s" % (self.name,)

class Array(Expr):
    def __init__(self, context, items):
        self.context = context
        self.items = items
    def __call__(self, global_qs, local_qs):
        return queryset.QuerySet([
            list(queryset.QuerySet(item
                          for item in (item(global_qs, local_qs)
                                       for item in self.items)
                          if item).flatten())])
    def __repr__(self):
        return "[%s]" % (", ".join(repr(item) for item in self.items),)

class Dict(Expr):
    def __init__(self, context, items):
        self.context = context
        self.items = items
    def __call__(self, global_qs, local_qs):
        return queryset.QuerySet([{key[0]: value[0]
                          for key, value in ((key(global_qs, local_qs), value(global_qs, local_qs))
                                             for key, value in self.items)
                          if key and value}])
    def __repr__(self):
        return "{%s}" % (", ".join("%s: %s" % (repr(key), repr(value))
                                               for key, value in self.items),)

