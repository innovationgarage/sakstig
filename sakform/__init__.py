import itertools
import types

import sakstig

class global_template(sakstig.Function):
    __name__ = "$template"
    def call(self, global_qs, local_qs, args):
        return global_qs._global_template_qs

class local_template(sakstig.Function):
    __name__ = "@template"
    def call(self, global_qs, local_qs, args):
        return global_qs._local_template_qs

def transform(data, template, debug=False, debug_path=False):
    """Transforms data according to the template.
    """
    
    def path(global_qs, local_qs, expr):
        if debug_path:
            print("path(\n%s,\n%s)" % (repr(data), repr(expr)))
        global_qs._global_template_qs = template_qs
        global_qs._local_template_qs = local_qs
        res = local_qs.execute(expr, global_qs)
        if debug_path:
            print("=> %s" % repr(res))
        return res
    
    def transform(qs, template):
        if sakstig.is_dict(template):
            result = sakstig.QuerySet([{
                key: value[0]
                for key, value in
                ((key, transform(qs, value))
                 for key, value in template.items()
                 if key != "$")
                if value}])
            if '$' in template:
                result = path(qs, result, template["$"])
            return result
        elif sakstig.is_list(template):
            return sakstig.QuerySet([list(sakstig.QuerySet(
                transform(qs, item)
                for item in template).flatten())])
        else:
            return sakstig.QuerySet([template])

    if debug:
        print("transform(\n%s,\n%s)" % (repr(data), repr(template)))

    template_qs = sakstig.QuerySet([template])

    if not isinstance(data, sakstig.QuerySet):
        data = sakstig.QuerySet([data])
    
    res = transform(data, template)

    if debug:
        print("=> %s" % repr(res))
    
    return res

def main():
    import sys
    import json
    with open(sys.argv[1]) as f:
        template = json.load(f)
    if len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    print(json.dumps(transform(data, template)))

