from . import grammar
from . import ast
from . import ast_base_types

Function = ast_base_types.Function

is_str = ast_base_types.is_str
is_dict = ast_base_types.is_dict
is_list = ast_base_types.is_list
is_int = ast_base_types.is_int
is_float = ast_base_types.is_float

compile = ast_base_types.compile
QuerySet = ast_base_types.QuerySet

# For compatibility with objectpath
class Tree(object):
    def __init__(self, obj):
        self.queryset = QuerySet([obj])
    def execute(self, query):
        r=self.queryset.execute(query)
        if len(r) == 1:
            return r[0]
        elif len(r) == 0:
            return None
        return r

ProgrammingError = Exception
ExecutionError = Exception
generator = chain = QuerySet
NUM_TYPES = [int, float]
ITER_TYPES = [list, tuple]
STR_TYPES = [str]

def main():
    import sys
    import json
    query = sys.argv[1]
    if len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    for result in QuerySet([data]).execute(query):
        print(json.dumps(result))

if __name__ == "__main__":
    main()
