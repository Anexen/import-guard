import unittest

from import_guard import guard, mod


class TestRules(unittest.TestCase):
    def test_simple_rule(self):
        guard.set_deny_rules({"csv": "io"})

        assert guard.is_import_allowed("csv", "bisect")
        assert not guard.is_import_allowed("csv", "io")

    def test_inverted_rule(self):
        guard.set_deny_rules({"csv": ~mod("io")})

        assert not guard.is_import_allowed("csv", "bisect")
        assert guard.is_import_allowed("csv", "io")

    def test_multiple_modules_in_rule(self):
        guard.set_deny_rules({"csv": ["io", "logging"]})

        assert guard.is_import_allowed("csv", "bisect")
        assert not guard.is_import_allowed("csv", "io")
        assert not guard.is_import_allowed("csv", "logging")

    def test_regex_rule(self):
        guard.set_deny_rules({"csv": mod.matches(".*io")})

        assert guard.is_import_allowed("csv", "bisect")
        assert not guard.is_import_allowed("csv", "io")
        assert not guard.is_import_allowed("csv", "_io")

    def test_lazy_import(self):
        guard.set_deny_rules({"csv": mod.top_level("logging")})

        assert not guard.is_import_allowed("csv", "logging")
        assert guard.is_import_allowed("csv", "logging", top_level=False)

    def test_allow_only_lazy_imports(self):
        guard.set_deny_rules({"test_proj": mod.top_level(mod.matches(".*"))})

        assert guard.is_import_allowed("test_proj", "csv", top_level=False)
        assert not guard.is_import_allowed("test_proj", "csv")
        assert not guard.is_import_allowed("test_proj", "test_proj.api")

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

        assert not guard.is_import_allowed("test_proj.api", "csv")
        assert not guard.is_import_allowed("test_proj.api", "selenium")
        assert not guard.is_import_allowed("test_proj.api", "test_proj.tasks")
        assert not guard.is_import_allowed(
            "test_proj.core.db", "test_proj.api"
        )
        assert guard.is_import_allowed("test_proj.api", "logging")
        assert guard.is_import_allowed(
            "test_proj.api", "test_proj.tasks", top_level=False
        )


if __name__ == "__main__":
    unittest.main()
