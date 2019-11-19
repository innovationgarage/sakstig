from . import ast_base_types
from . import typeinfo
from . import queryset
import re
import datetime
import math

class op_path_one(ast_base_types.Op):
    def __call__(self, global_qs, local_qs):
        parent = self.args[0](global_qs, local_qs)
        res = self.args[1](global_qs, parent)
        res.is_path_multi = parent.is_path_multi
        return res
    
class op_path_multi(ast_base_types.Op):
    def __call__(self, global_qs, local_qs):
        assert isinstance(self.args[1], ast_base_types.Name) or isinstance(self.args[1], ast_base_types.ParenExpr), "..%s is invalid" % type(self.args[1])
        local_qs = self.args[0](global_qs, local_qs).descendants(
            include_leaves=self.context.args.get("descendant_leaves", False))
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
    def __call__(self, global_qs, local_qs):
        left = self.args[0](global_qs, local_qs)
        right = self.args[1](global_qs, local_qs)
        if self.context.args.get("add_as_join", True) and (len(left) != 1 or len(right) != 1):
            # Same as op_union_union
            def result():
                for a in left:
                    yield a
                for b in right:
                    yield b
            return queryset.QuerySet(result())
        else:
            # Same as base class
            def result():
                for a in left:
                    for b in right:
                        yield self._op(a, b)
            return queryset.QuerySet(result())    
    def op(self, a, b):
        if not (isinstance(a, int) and isinstance(b, float)):
            try:
                b = type(a)(b)
            except:
                pass
        if typeinfo.is_dict(a) and typeinfo.is_dict(b):
            res = {}
            res.update(a)
            res.update(b)
            return res
        elif typeinfo.is_set(a) and typeinfo.is_set(a):
            return a.union(b)
        elif typeinfo.is_time(a) and typeinfo.is_time(b):
            # Isn't this a bit of a hack? But ObjectPath allows this...
            time_as_delta = (datetime.datetime.combine(datetime.datetime(1970,1,1), b)
                             - datetime.datetime.combine(datetime.datetime(1970,1,1), datetime.time(0, 0, 0, 0, b.tzinfo)))
            return (datetime.datetime.combine(datetime.datetime(1970,1,1), a) + time_as_delta).time()
        return a + b

class op_add_sub(MathOp):
    def op(self, a, b):
        if typeinfo.is_time(a) and typeinfo.is_time(b):
            a = datetime.datetime.combine(datetime.datetime(1970,1,1), a)
            b = datetime.datetime.combine(datetime.datetime(1970,1,1), b)
            res = a - b
            return typeinfo.TimeOnlyDelta(res.days, res.seconds, res.microseconds)
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
    def __call__(self, global_qs, local_qs):
        def result():
            a_qs = self.args[0](global_qs, local_qs)
            b_qs = self.args[1](global_qs, local_qs)
            if self.context.args.get("empty_queryset_is_none", True):
                if not a_qs and len(b_qs) == 1 and (b_qs[0] is None):
                    yield True
                    return
                if not b_qs and len(a_qs) == 1 and (a_qs[0] is None):
                    yield True
                    return
            for a in a_qs:
                for b in b_qs:
                    yield self._op(a, b)
        return queryset.QuerySet(result())
    def op(self, a, b):
        if a == b:
            return True
        if not a and not b:
            if not self.context.args.get("cmp_empty_same", False):
                return type(a) is type(b)
            return True
        if typeinfo.is_float(b):
            a, b = b, a
        try:
            b = type(a)(b)
        except:
            return False
        if typeinfo.is_float(a):
            return math.isclose(a, b)
        else:
            return a == b
            
class op_comp_is_not(MathOp):
    def __call__(self, global_qs, local_qs):
        def result():
            a_qs = self.args[0](global_qs, local_qs)
            b_qs = self.args[1](global_qs, local_qs)
            if self.context.args.get("empty_queryset_is_none", True):
                if not a_qs and len(b_qs) == 1 and (b_qs[0] is None):
                    yield False
                    return
                if not b_qs and len(a_qs) == 1 and (a_qs[0] is None):
                    yield False
                    return
            for a in a_qs:
                for b in b_qs:
                    yield self._op(a, b)
        return queryset.QuerySet(result())
    def op(self, a, b):
        if a == b:
            return False
        if not a and not b:
            if not self.context.args.get("cmp_empty_same", False):
                return type(a) is not type(b)
            return False
        if typeinfo.is_float(b):
            a, b = b, a
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
        if isinstance(b, str):
            res = a.match(b)
            if not res: return False
            if len(res.groups()) == 0:
                return True
            return res.groups()
        else:
            for bitem in b:
                if a.match(bitem):
                    return True
            return False

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
        if self.context.args.get("filter_lists", True) and len(local_qs) == 1 and typeinfo.is_list(local_qs[0]):
            if isinstance(filter, ast_base_types.Const) and typeinfo.is_int(filter.value):
                yield local_qs[0][filter.value]
            else:
                yield list(self.filter_qs(filter, global_qs, queryset.QuerySet(local_qs[0])))
            return
        def getitem(obj, key):
            if typeinfo.is_list(obj):
                for item in obj:
                    try:
                        yield item[key]
                    except:
                        pass
            else:
                try:
                    yield obj[key]
                except:
                    pass
        for idx, item in enumerate(local_qs):
            filter_qs = queryset.QuerySet([item])
            filter_qs.is_filter_qs = True
            if isinstance(filter, ast_base_types.Name) and filter.name not in ("$", "@"):
                for res in getitem(item, filter.name):
                    yield res
            elif (    self.context.args.get("filter_bad_syntax", True)
                  and isinstance(filter, op_path_one)
                  and isinstance(filter.args[0], ast_base_types.Name)
                  and filter.args[0].name == "@"
                  and isinstance(filter.args[1], ast_base_types.Name)):
                for res in getitem(item, filter.args[1].name):
                    yield res                
            else:
                for filter_res in filter(global_qs, filter_qs):
                    if (self.context.args.get("index_filter_queryset", True)
                        and typeinfo.is_int(filter_res)
                        and len(local_qs) > 0
                        and not typeinfo.is_list(local_qs[0])):
                        if idx == filter_res:
                            yield item
                    elif typeinfo.is_int(filter_res):
                        try:
                            yield item[filter_res]
                        except:
                            pass
                    elif typeinfo.is_str(filter_res):
                        for res in getitem(item, filter_res):
                            yield res
                    else:
                        if filter_res:
                            yield item
    def __call__(self, global_qs, local_qs):
        local_qs = self.args[0](global_qs, local_qs)
        for filter in self.args[1:]:
            res_qs = queryset.QuerySet(self.filter_qs(filter, global_qs, local_qs))
            if not isinstance(filter, ast_base_types.Const) or not typeinfo.is_int(filter.value):
                res_qs.is_path_multi = local_qs.is_path_multi
            local_qs = res_qs
        return local_qs
