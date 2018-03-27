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
def Tree(root):
    return QuerySet([root])

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
