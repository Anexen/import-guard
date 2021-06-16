import unittest
from importlib import import_module

from import_guard import ForbiddenImportError, guard


class TestImports(unittest.TestCase):
    def test_simple_rule(self):
        guard.set_deny_rules({"csv": "re"})
        guard.enable(strict=True)

        with self.assertRaises(ForbiddenImportError):
            import_module("csv")
