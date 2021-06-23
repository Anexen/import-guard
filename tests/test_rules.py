import unittest

from import_guard import guard, mod
from import_guard.models import ImportInfo


class TestRules(unittest.TestCase):
    def test_simple_rule(self):
        guard.set_deny_rules({"<stdin>": "io"})

        assert guard.is_import_allowed("bisect")
        assert not guard.is_import_allowed("io")

    def test_inverted_rule(self):
        guard.set_deny_rules({"<stdin>": ~mod("io")})

        assert not guard.is_import_allowed("bisect")
        assert guard.is_import_allowed("io")

    def test_multiple_modules_in_rule(self):
        guard.set_deny_rules({"<stdin>": ["io", "logging"]})

        assert guard.is_import_allowed("bisect")
        assert not guard.is_import_allowed("io")
        assert not guard.is_import_allowed("logging")

    def test_regex_rule(self):
        guard.set_deny_rules({"<stdin>": mod.matches(".*io")})

        assert guard.is_import_allowed("bisect")
        assert not guard.is_import_allowed("io")
        assert not guard.is_import_allowed("asyncio")

    def test_lazy_import(self):
        guard.set_deny_rules({"<stdin>": mod.top_level("logging")})

        assert not guard.is_import_allowed("logging")
        assert guard.is_import_allowed("logging", top_level=False)

    def test_allow_only_lazy_imports(self):
        guard.set_deny_rules({"test_proj": mod.top_level(mod.matches(".*"))})

        assert guard.is_import_allowed(
            "csv", caller="test_proj", top_level=False
        )
        assert not guard.is_import_allowed("csv", caller="test_proj")
        assert not guard.is_import_allowed("test_proj.api", caller="test_proj")

    def test_start_import(self):
        guard.set_deny_rules({"<stdin>": mod.star("csv")})

        assert guard.is_import_allowed(ImportInfo("csv", ["DictReader"], 0))
        assert not guard.is_import_allowed(ImportInfo("csv", ["*"], 0))

    def test_rules_from_readme(self):
        guard.set_deny_rules(
            {
                "test_proj": "csv",
                "test_proj.api": [
                    "selenium",
                    mod.top_level("test_proj.tasks"),
                ],
                "test_proj.core": mod.matches(
                    r"test_proj\.(api|business_logic)"
                ),
                "test_proj.logging": ~mod.any(["logging", "yaml"]),
            }
        )

        assert not guard.is_import_allowed("csv", caller="test_proj.api")
        assert not guard.is_import_allowed("selenium", caller="test_proj.api")
        assert not guard.is_import_allowed(
            "test_proj.tasks", caller="test_proj.api"
        )
        assert not guard.is_import_allowed(
            "test_proj.api", caller="test_proj.core.db"
        )
        assert guard.is_import_allowed("logging", caller="test_proj.api")
        assert guard.is_import_allowed(
            "test_proj.tasks", caller="test_proj.api", top_level=False
        )


if __name__ == "__main__":
    unittest.main()
