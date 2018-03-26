import grammar
import ast
import ast_base_types

QuerySet = ast_base_types.QuerySet

# For compatibility with objectpath
def Tree(root):
    return QuerySet([root])


if __name__ == "__main__":
    import sys
    import json
    print(json.dumps(QuerySet([json.load(sys.stdin)]).execute(sys.argv[1])))
