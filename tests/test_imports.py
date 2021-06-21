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
    def test_myproject(self):
        # rules are defined inside myproject
        expected = {
            # <module> forbidden in <caller>
            ("csv", "myproject.api"),
            ("bisect", "myproject.api"),
            ("myproject.business_logic", "myproject.core"),
            ("json", "myproject.logging")
        }

        # capture all warnings, extract affected modules
        # and compare to expected
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import_module("myproject").run()

        pattern = re.compile(r"Importing `([\w\.]+)` from `([\w\.]+)`")
        actual = {pattern.findall(str(x.message))[0] for x in w}

        self.assertEqual(actual, expected)
