from pyleri import *

class SakstigGrammar(Grammar):
    START = Ref()

    t_number = Regex(r'[+-]?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?')
    t_string = Regex(r"""("([^"]|(\\"))*")|('([^']|(\\'))*')""")

    name = Regex(r"[a-zA-Z_$@#*0-9]*")

    p_round_l = Regex(r"\(")
    p_round_r = Regex(r"\)")
    p_hard_l = Regex(r"\[")
    p_hard_r = Regex(r"\]")
    p_curly_l = Regex(r"{")
    p_curly_r = Regex(r"}")

    t_array_list = List(START, delimiter=',', mi=0, ma=None, opt=True)
    t_array = Sequence(p_hard_l, t_array_list, p_hard_r)

    t_dict_item = Sequence(START, Token(":"), START)
    t_dict_list = List(t_dict_item, delimiter=',', mi=0, ma=None, opt=True)
    t_dict = Sequence(p_curly_l, t_dict_list, p_curly_r)

    t = Choice(t_number, t_string, t_array, t_dict)
    s_expr = Choice(t, name)

    p_expr = Sequence(p_round_l, START, p_round_r)
    f_expr = Sequence(p_hard_l, START, p_hard_r)

    a_expr_list = List(START, delimiter=',', mi=0, ma=None, opt=True)
    a_expr = Sequence(p_round_l, a_expr_list, p_round_r)

    nop = Tokens("not")
    nop_expr = Sequence(nop, START)

    c_expr = Sequence(name, a_expr)

    l_expr = Choice(s_expr, p_expr, nop_expr, c_expr)

    op_path_one = Token(".")
    op_path_multi = Token("..")
    op_path = Choice(op_path_one, op_path_multi)
    op_mul_mul = Token("*")
    op_mul_div = Token("/")
    op_mul = Choice(op_mul_mul, op_mul_div)
    op_add_add = Token("+")
    op_add_sub = Token("-")
    op_add = Choice(op_add_add, op_add_sub)
    op_comp_in = Token("in")
    op_comp_is = Token("is")
    op_comp_lt = Token("<")
    op_comp_gt = Token(">")
    op_comp_lte = Token("<=")
    op_comp_gte = Token(">=")
    op_comp = Choice(op_comp_in, op_comp_is, op_comp_lt, op_comp_gt, op_comp_lte, op_comp_gte)
    op_bool_and = Token("and")
    op_bool_or = Token("or")
    op_bool = Choice(op_bool_and, op_bool_or)

    path = List(l_expr, delimiter=op_path, mi=1, ma=None)    
    fpath = Sequence(path, Repeat(f_expr, mi=0, ma=None))
    mfpath = List(fpath, delimiter=op_path, mi=1, ma=None)
    mul = List(mfpath, delimiter=op_mul, mi=1, ma=None)
    add = List(mul, delimiter=op_add, mi=1, ma=None)
    comp = List(add, delimiter=op_comp, mi=1, ma=None)
    bool = List(comp, delimiter=op_bool, mi=1, ma=None)
    
    START = Sequence(bool)

    
grammar = SakstigGrammar()

        
def format_tree(node, indent=''):
    if len(node.children) == 1:
        return format_tree(node.children[0], indent)
    if node.children:
        info = "\n" + "".join(format_tree(child, indent+'  ') for child in node.children)
    else:
        info = "=%s\n" % (node.string, )
    return "%s%s%s" % (indent, getattr(node.element, 'name', '[anon]'), info)

def main():
    import sys
    res = grammar.parse(sys.argv[1])
    if not res.is_valid:
        print("INVALID EXPRESSION")
    else:
        print("Parsed valid expression")
        print(format_tree(res.tree))
