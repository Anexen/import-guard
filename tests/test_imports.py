import re
import unittest
import warnings
from importlib import import_module

from import_guard import ForbiddenImportError, guard, mod


class TestImports(unittest.TestCase):
    def setUp(self):
        guard.set_deny_rules({"csv": "re"})
        guard.enable(strict=True)

    def test_strict_mode(self):
        with self.assertRaises(ForbiddenImportError):
            import_module("csv")


class TestProject(unittest.TestCase):
    def setUp(self):
        rules = {
            "myproject": "csv",
            "myproject.api": ["bisect", mod.top_level("myproject.tasks")],
            "myproject.core": mod.matches(r"myproject\.(api|business_logic)"),
            "myproject.logging": ~mod.any(["logging", "yaml"]),
        }

        guard.set_deny_rules(rules)
        guard.enable()

    def test_myproject(self):
        # rules are defined inside myproject

        expected = {
            # <module> forbidden in <caller>
            ("csv", "myproject.api"),
            ("bisect", "myproject.api"),
            ("json", "myproject.logging"),
            ("myproject.business_logic", "myproject.core"),
        }

        # capture all warnings, extract affected modules
        # and compare to expected
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import_module("myproject").run()

        pattern = re.compile(r"Importing `([\w\.]+)` from `([\w\.]+)`")
        actual = {pattern.findall(str(x.message))[0] for x in w}

        self.assertEqual(actual, expected)
