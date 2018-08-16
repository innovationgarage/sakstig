import sakstig
import sys

# Hackety hack...  make the tests test sakstig instead of ObjectPath
import objectpath
sys.modules["objectpath.core"] = sakstig
sys.modules["objectpath.core.interpreter"] = sakstig
objectpath.core = sakstig
objectpath.core.interpreter = sakstig

from ObjectPath.tests.test_ObjectPath import ObjectPath
