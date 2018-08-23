from . import grammar
from . import ast
from . import ast_base_types
from . import queryset
from .typeinfo import *

Function = ast_base_types.Function

compile = ast.compile
QuerySet = queryset.QuerySet

# For compatibility with objectpath
Tree = queryset.Tree
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
