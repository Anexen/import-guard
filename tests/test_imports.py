import re
import unittest
import warnings
from importlib import import_module

from import_guard import ForbiddenImportError, guard


class TestForbiddenImportError(unittest.TestCase):
    def test_strict_mode(self):
        guard.set_deny_rules({"csv": "re"})
        guard.enable(strict=True)

        with self.assertRaises(ForbiddenImportError):
            import_module("csv")


class TestProject(unittest.TestCase):
    def test_test_proj(self):
        # rules are defined inside test_proj
        expected = {
            # <module> forbidden in <caller>
            ("csv", "test_proj.api"),
            ("bisect", "test_proj.api"),
            ("json", "test_proj.logging"),
            ("test_proj.business_logic", "test_proj.core"),
            ("test_proj.logging", "test_proj.api"),
        }

        # capture all warnings, extract affected modules
        # and compare to expected
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import_module("test_proj").run()

        pattern = re.compile(r"Importing `([\w\.]+)` from `([\w\.]+)`")
        actual = {pattern.findall(str(x.message))[0] for x in w}

        self.assertEqual(actual, expected)
