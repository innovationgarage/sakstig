from . import ast_base_types
from . import ops
from . import functions
from . import grammar
import re

no_compatibility = dict(
    in_queryset=False,
    autoflatten_lists=False,
    aggregate_casts=True,
    nop_star=False,
    add_as_join=False,
    index_filter_queryset=False,
    descendant_leaves=True,
    cmp_empty_same=True,
    empty_queryset_is_none=False,
    object_slicing=False,
    filter_lists=False,
    filter_bad_syntax=False
)

class AST(object):
    def __new__(cls, node, **args):
        self = object.__new__(cls)
        if not args.get("compatibility", True):
            res = {}
            res.update(no_compatibility)
            res.update(args)
            args = res
        self.args = args
        return self._build_ast(node)
    def _build_ast(self, node):
        name = getattr(node.element, 'name', None)
        if name is not None and hasattr(self, name):
            children = [self._build_ast(child) for child in node.children]
            try:
                return getattr(self, name)(node, *children)
            except Exception as e:
                e.args = ("Unable to instantiate %s(%s)" % (name, ", ".join(repr(child) for child in children)),) + e.args
                raise                
        elif len(node.children) == 1:
            return self._build_ast(node.children[0])
        elif node.children:
            children = node.children
            left = self._build_ast(children[0])
            children = children[1:]
            while children:
                opname = getattr(children[0].element, 'name', None)
                if len(children) < 2:
                    raise Exception("Missing right-hand side to operator at %s(%s, MISSING) (node.element=%s)" % (opname, repr(left), name))
                right = self._build_ast(children[1])
                try:
                    left = getattr(self, opname)(children[0], left, right)
                except Exception as e:
                    e.args = ("Unable to instantiate %s(%s, %s)" % (opname, repr(left), repr(right)),) + e.args
                    raise
                children = children[2:]
            return left
        else:
            if hasattr(node.element, 'name'):
                return self.other(node)
            else:
                return self.sep(node)
    class other(object):
        def __init__(self, node):
            self.type = getattr(node.element, 'name', None)
        def __repr__(self):
            return "<%s>" % self.type
    class sep(object):
        def __init__(self, node):
            self.str = node.string
        def __repr__(self):
            return "<%s>" % self.str
    def t_number(self, node):
        s = node.string.replace("+", "").replace("--", "")
        if 'e' in s or '.' in s:
            return ast_base_types.Const(self, float(s))
        else:
            return ast_base_types.Const(self, int(s))
    def t_string(self, node):
        return ast_base_types.Const(self, node.string[1:-1])
    def t_regexp(self, node):
        return ast_base_types.Const(self, re.compile(node.string[1:-1]))
    def simple_name(self, node):
        name = node.string
        name_lower = name.lower()
        if name_lower in ('null', 'none', 'nil', 'n'):
            return ast_base_types.Const(self, None)
        elif name_lower in ('true', 't'):
            return ast_base_types.Const(self, True)
        elif name_lower in ('false', 'f'):
            return ast_base_types.Const(self, False)
        else:
            return ast_base_types.Name(self, name)
    def star(self, node):
        return ast_base_types.Name(self, "*")
    def t_array_list(self, node, *items):
        return ast_base_types.Array(
            self,
            [item
             for item in items
             if not isinstance(item, self.sep)])
    def t_array(self, node, l, items, r):
        return items
    def t_dict_item(self, node, left, sep, right):
        return (left, right)
    def t_dict_list(self, node, *items):
        return ast_base_types.Dict(
            self,
            [item
             for item in items
             if not isinstance(item, self.sep)])
    def t_dict(self, node, l, items, r):
        return items
    def p_expr(self, node, l, expr, r):
        return ast_base_types.ParenExpr(self, expr)
    def f_expr(self, node, l, expr, r):
        return expr
    def a_expr_list(self, node, *items):
        return [item
                for item in items
                if not isinstance(item, self.sep)]
    def a_expr(self, node, l, args, r):
        return args
    def c_expr(self, node, name, args):
        return ast_base_types.Function(self, name.name, *args)
    def nop_expr(self, node, nop, expr):
        return ast_base_types.Op(self, "nop_expr", expr)
    def op(self, node, left, right):
        return ast_base_types.Op(self, node.children[0].element.name, left, right)
    op_path = op
    op_mul = op
    op_add = op
    op_comp = op
    op_bool = op
    op_union = op
    def filters(self, node, *filters):
        return filters
    def fpath(self, node, path, filters):
        if not filters:
            return path
        return ast_base_types.Op(self, "filter", path, *filters)

def compile(query, **args):
    gramr = grammar.SakstigGrammar()
    tree = gramr.parse(query)
    if not tree.is_valid:
        raise SyntaxError("Malformed query: %s<ERROR>%s\n%s" % (
            query[:tree.pos],
            query[tree.pos:],
            gramr.format_tree(tree.tree)))
    return AST(tree.tree, **args)
    
def main():
    from . import grammar
    import sys
    res = grammar.SakstigGrammar().parse(sys.argv[1])
    if not res.is_valid:
        print("INVALID EXPRESSION")
    else:
        print("Parsed valid expression")
        print(AST(res.tree))
