from pyleri import *

class SakstigGrammar(Grammar):
    START = Ref()

    t_number = Regex(r'[+-]?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?')
    t_string = Regex(r"""("([^"]|(\\"))*")|('([^']|(\\'))*')""")
    t_null = Regex(r"([nN][uU][lL][lL])|([nN][oO][nN][eE])|[nN]|([nN][iI][lL])")
    t_true = Regex(r"([tT][rR][uU][eE])|[tT]")
    t_false = Regex(r"([fF][aA][lL][sS][eE])|[fF]")

    name = Regex(r"[a-zA-Z_$@#*]*")

    p_round_l = Regex(r"\(")
    p_round_r = Regex(r"\)")
    p_hard_l = Regex(r"\[")
    p_hard_r = Regex(r"\]")
    p_curly_l = Regex(r"{")
    p_curly_r = Regex(r"}")

    t_array = Sequence(p_hard_l, List(START, delimiter=',', mi=0, ma=None, opt=True), p_hard_r)

    t_dict_item = Sequence(START, Token(":"), START)
    t_dict = Sequence(p_curly_l, List(t_dict_item, delimiter=',', mi=0, ma=None, opt=True), p_curly_r)

    t = Choice(t_number, t_string, t_null, t_true, t_false, t_array, t_dict)
    s_expr = Choice(name, t)

    p_expr = Sequence(p_round_l, START, p_round_r)
    f_expr = Sequence(p_hard_l, START, p_hard_r)

    nop = Tokens("not")
    nop_expr = Sequence(nop, START)
    
    l_expr = Choice(s_expr, p_expr, nop_expr)

    op_path = Tokens(". ..")
    op_mul = Tokens("* /")
    op_add = Tokens("- +")
    op_comp = Tokens("in is < > <= >=")
    op_bool = Tokens("and or")

    path = List(l_expr, delimiter=op_path, mi=1, ma=None)
    fpath = Sequence(path, Repeat(f_expr, mi=0, ma=None))
    mfpath = List(fpath, delimiter=op_path, mi=1, ma=None)
    mul = List(mfpath, delimiter=op_mul, mi=1, ma=None)
    add = List(mul, delimiter=op_add, mi=1, ma=None)
    comp = List(add, delimiter=op_comp, mi=1, ma=None)
    bool = List(comp, delimiter=op_bool, mi=1, ma=None)
    
    START = Sequence(bool)

    
sakstig_grammar = SakstigGrammar()

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
    
        
def format_tree(node, indent=''):
    if len(node.children) == 1:
        return format_tree(node.children[0], indent)
    if node.children:
        info = "\n" + "".join(format_tree(child, indent+'  ') for child in node.children)
    else:
        info = "=%s\n" % (node.string, )
    return "%s%s%s" % (indent, getattr(node.element, 'name', '[anon]'), info)


#res = sakstig_grammar.parse('$..*[foo].name')
res = sakstig_grammar.parse('$..*[@..temp > 25 and @.clouds.all is 0].name')
#res = sakstig_grammar.parse('$.foo')
print(res.is_valid)
print(format_tree(res.tree))

try:
    print(AST(res.tree))
except Exception as e:
    print(e)
    import pdb, sys
    sys.last_traceback = sys.exc_info()[2]
    pdb.pm()
#import pdb
#pdb.set_trace()
