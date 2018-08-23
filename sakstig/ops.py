from . import ast_base_types
from . import typeinfo
from . import queryset
import re
import datetime
import math

class op_path_one(ast_base_types.Op):
    def __call__(self, global_qs, local_qs):
        return self.args[1](global_qs, self.args[0](global_qs, local_qs))

class op_path_multi(ast_base_types.Op):
    def __call__(self, global_qs, local_qs):
        assert isinstance(self.args[1], ast_base_types.Name)
        local_qs = self.args[0](global_qs, local_qs).descendants()
        local_qs.is_path_multi = True
        return self.args[1](global_qs, local_qs)

class MathOp(ast_base_types.Op):
    abstract = True
    def op(self, a, b):
        raise NotImplementedError
    def __call__(self, global_qs, local_qs):
        def result():
            for a in self.args[0](global_qs, local_qs):
                for b in self.args[1](global_qs, local_qs):
                    yield self._op(a, b)
        return queryset.QuerySet(result())
    def _op(self, a, b):
        if a is None:
            if typeinfo.is_dict(b):
                a = {}
            elif typeinfo.is_list(b):
                a = []
            elif typeinfo.is_set(b):
                a = set()
            else:
                a = 0
        if b is None:
            if typeinfo.is_dict(a):
                b = {}
            elif typeinfo.is_list(a):
                b = []
            elif typeinfo.is_set(a):
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
        if typeinfo.is_dict(a) and typeinfo.is_dict(b):
            res = {}
            res.update(a)
            res.update(b)
            return res
        elif typeinfo.is_set(a) and typeinfo.is_set(a):
            return a.union(b)
        return a + b

class op_add_sub(MathOp):
    def op(self, a, b):
        if typeinfo.is_time(a):
            a = datetime.datetime.combine(datetime.datetime(1970,1,1), a)
        if typeinfo.is_time(b):
            b = datetime.datetime.combine(datetime.datetime(1970,1,1), b)
        return a - b

class op_comp_in(MathOp):
    def op(self, a, b):
        if self.context.args.get("in_queryset", True) and op_comp_is(self.context, None).op(a, b):
            return True
        if typeinfo.is_list(a) and set(a).intersection(set(b)):
            return True
        try:
            return a in b
        except:
            return False

class op_comp_not_in(MathOp):
    def op(self, a, b):
        if self.context.args.get("in_queryset", True) and op_comp_is(self.context, None).op(a, b):
            return False
        if typeinfo.is_list(a) and set(a).intersection(set(b)):
            return False
        try:
            return a not in b
        except:
            return True
        
class op_comp_is(MathOp):
    def op(self, a, b):
        if a == b:
            return True
        try:
            b = type(a)(b)
        except:
            return False
        if typeinfo.is_float(a):
            return math.isclose(a, b)
        else:
            return a == b
            
class op_comp_is_not(MathOp):
    def op(self, a, b):
        if a == b:
            return False
        try:
            b = type(a)(b)
        except:
            return True
        if typeinfo.is_float(a):
            return not math.isclose(a, b)
        else:
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
        if typeinfo.is_str(a):
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

class nop_expr(ast_base_types.Op):
    def __call__(self, global_qs, local_qs):
        def result():
            for a in self.args[0](global_qs, local_qs):
                yield not a
        return queryset.QuerySet(result())

class op_union_union(ast_base_types.Op):
    def __call__(self, global_qs, local_qs):
        def result():
            for a in self.args[0](global_qs, local_qs):
                yield a
            for b in self.args[1](global_qs, local_qs):
                yield b
        return queryset.QuerySet(result())
    
class filter(ast_base_types.Op):
    def filter_qs(self, filter, global_qs, local_qs):
        for item in local_qs:
            for filter_res in filter(global_qs, queryset.QuerySet([item])):
                if typeinfo.is_int(filter_res) or typeinfo.is_str(filter_res):
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
            local_qs = queryset.QuerySet(self.filter_qs(filter, global_qs, local_qs))
        return local_qs
