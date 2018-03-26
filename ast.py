import grammar

class AST(object):
    def __new__(cls, node):
        self = object.__new__(cls)
        return self._build_ast(node)
    def _build_ast(self, node):
        name = getattr(node.element, 'name', None)
        if len(node.children) == 1:
            return self._build_ast(node.children[0])
        elif name is not None and hasattr(self, name):
            return getattr(self, name)(node, *(self._build_ast(child) for child in node.children))
        elif node.children:
            children = node.children
            left = self._build_ast(children[0])
            children = children[1:]
            while children:
                opname = getattr(children[0].element, 'name', None)
                left = getattr(self, opname)(children[0], left, self._build_ast(children[1]))
                children = children[2:]
            return left
        else:
            return self.other(node)
    class other(object):
        def __init__(self, node):
            self.type = getattr(node.element, 'name', None)
        def __repr__(self):
            return "<%s>" % self.type
    def t_number(self, node):
        if 'e' in node.string or '.' in node.string:
            return float(node.string)
        else:
            return int(node.string)
    def t_string(self, node):
        return node.string[1:-1]
    def t_null(self, node):
        return None
    def t_true(self, node):
        return True
    def t_false(self, node):
        return False
    class name(object):
        def __init__(self, node):
            self.name = node.string
        def __repr__(self):
            return "%s" % self.name
    def t_array(self, node, *items):
        return items[1:-1]
    def t_dict_item(self, node, left, sep, right):
        return (left, right)
    def t_dict(self, node, *items):
        return dict(items[1:1])
    def p_expr(self, node, l, expr, r):
        return expr
    def f_expr(self, node, l, expr, r):
        return expr
    def a_expr(self, node, *args):
        return args[1:-1]
    class c_expr(object):
        def __init__(self, node, name, args):
            self.name = name
            self.args = args
        def __repr__(self):
            return "%s(%s)" % (self.name, ", ".join(repr(arg) for arg in self.args))
    class nop_expr(object):
        def __init__(self, node, nop, expr):
            self.expr = expr
        def __repr__(self):
            return "not %s" % repr(self.expr)
    class Op(object):
        def __init__(self, node, left, right):
            self.op = node.string
            self.left = left
            self.right = right
        def __repr__(self):
            return "%s %s %s" % (repr(self.left), self.op, repr(self.right))
    op_path = Op
    op_mul = Op
    op_add = Op
    op_comp = Op
    op_bool = Op
    class fpath(object):
        def __new__(cls, node, path, *filters):
            filters = [f for f in filters if not (isinstance(f, AST.other) and f.type is None)]
            if not filters:
                return path
            self = object.__new__(cls)
            self.path = path
            self.filters = filters
            return self
        def __repr__(self):
            return "%s%s" % (self.path, "".join("[%s]" % repr(filter) for filter in self.filters))

if __name__ == "__main__":
    import sys
    res = grammar.grammar.parse(sys.argv[1])
    if not res.is_valid:
        print("INVALID EXPRESSION")
    else:
        print("Parsed valid expression")
        print(AST(res.tree))
