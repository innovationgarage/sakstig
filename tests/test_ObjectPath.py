import sakstig
import sys
import re
import unittest

# workaround for rename in Python3
if hasattr(unittest.TestCase, "assertCountEqual"):
    unittest.TestCase.assertItemsEqual = unittest.TestCase.assertCountEqual

# Hackety hack...  make the tests test sakstig instead of ObjectPath
import objectpath
sys.modules["objectpath.core"] = sakstig
sys.modules["objectpath.core.interpreter"] = sakstig
objectpath.core = sakstig
objectpath.core.interpreter = sakstig

import ObjectPath.tests.test_ObjectPath
ObjectPath.tests.test_ObjectPath.re = re # Bug workaround

from ObjectPath.tests.test_ObjectPath import ObjectPath
from ObjectPath.tests.test_ObjectPath import ObjectPath_Paths
