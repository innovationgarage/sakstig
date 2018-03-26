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
    query = sys.argv[1]
    if len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    print(json.dumps(QuerySet([data]).execute(query)))
