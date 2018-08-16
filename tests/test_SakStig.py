import sakstig
import sys

# Hackety hack...  make the tests test sakstig instead of ObjectPath
import objectpath
sys.modules["objectpath.core"] = sakstig
sys.modules["objectpath.core.interpreter"] = sakstig
objectpath.core = sakstig
objectpath.core.interpreter = sakstig

import ObjectPath.tests.test_ObjectPath as optest
def execute(expr):
    r=optest.tree1.execute(expr)
    if len(r) == 1:
        return r[0]
    elif len(r) == 0:
        return None
    return r        
optest.execute = execute
            
def execute2(expr):
    r=optest.tree2.execute(expr)
    if len(r) == 1:
        return r[0]
    elif len(r) == 0:
        return None
    return r
optest.execute2 = execute2

ObjectPath = optest.ObjectPath
