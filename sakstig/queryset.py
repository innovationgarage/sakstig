from . import typeinfo

class QuerySet(list):
    def __init__(self, *arg, **kw):
        list.__init__(self, *arg, **kw)
        self.is_path_multi = False
        
    def __repr__(self):
        return "%s\n" % ("\n".join(repr(item) for item in self))

    def execute(self, query, global_qs = None, **args):
        from . import ast
        from . import ast_base_types
        if not isinstance(query, ast_base_types.Expr):
            if not isinstance(query, str):
                return QuerySet([query])
            query = ast.compile(query, **args)
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
                if typeinfo.is_dict(item):
                    if no_dict:
                        if not children_only:
                            yield item
                    else:
                        for value in item.values():
                            yield value
                elif typeinfo.is_list(item):
                    for value in item:
                        yield value
                elif not children_only:
                    yield item
        return QuerySet(flatten())

    def descendants(self, include_lists=False, include_leaves=True):
        def children(item):
            if typeinfo.is_dict(item):
                return item.values()
            elif typeinfo.is_list(item):
                return iter(item)
            else:
                return []
        def descendants(item):
            if ((include_lists or not typeinfo.is_list(item))
                and (include_leaves or typeinfo.is_dict(item))):
                yield item
            for child in children(item):
                for descendant in descendants(child):
                    yield descendant
        return QuerySet(descendants(self))
    
    def __add__(self, other):
        return type(self)(list.__add__(self, other))


# For compatibility with objectpath
class Tree(object):
    def __init__(self, obj):
        if not typeinfo.is_list(obj) and not typeinfo.is_set(obj):
            obj = [obj]
        self.queryset = QuerySet(obj)
    def execute(self, query, **args):
        r=self.queryset.execute(query, **args)
        if len(r) == 1 and not r.is_path_multi:
            return r[0]
        elif len(r) == 0:
            return None
        return r
