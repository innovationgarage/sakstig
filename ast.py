import ast_base_types

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
            return ast_base_types.Const(float(node.string))
        else:
            return ast_base_types.Const(int(node.string))
    def t_string(self, node):
        return ast_base_types.Const(node.string[1:-1])
    def t_null(self, node):
        return ast_base_types.Const(None)
    def t_true(self, node):
        return ast_base_types.Const(True)
    def t_false(self, node):
        return ast_base_types.Const(False)
    def name(self, node):
        return ast_base_types.Name(node.string)
    def t_array(self, node, *items):
        return ast_base_types.Array(items[1:-1])
    def t_dict_item(self, node, left, sep, right):
        return (left, right)
    def t_dict(self, node, *items):
        return ast_base_types.Dict(items[1:1])
    def p_expr(self, node, l, expr, r):
        return expr
    def f_expr(self, node, l, expr, r):
        return expr
    def a_expr(self, node, *args):
        return args[1:-1]
    def c_expr(self, node, name, args):
        return ast_base_types.Function(name, *args)
    def nop_expr(self, node, nop, expr):
        return ast_base_types.Op("not", expr)
    def op(self, node, left, right):
        return ast_base_types.Op(node.children[0].element.name, left, right)
    op_path = op
    op_mul = op
    op_add = op
    op_comp = op
    op_bool = op
    def fpath(self, node, path, *filters):
        filters = [f for f in filters if not (isinstance(f, AST.other) and f.type is None)]
        if not filters:
            return path
        return ast_base_types.Op("filter", path, *filters)

if __name__ == "__main__":
    import grammar
    import sys
    res = grammar.grammar.parse(sys.argv[1])
    if not res.is_valid:
        print("INVALID EXPRESSION")
    else:
        print("Parsed valid expression")
        print(AST(res.tree))
