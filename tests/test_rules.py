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
        guard.set_deny_rules({"myproject": mod.top_level(mod.matches(".*"))})

        assert guard.is_import_allowed("myproject", "csv", top_level=False)
        assert not guard.is_import_allowed("myproject", "csv")
        assert not guard.is_import_allowed("myproject", "myproject.api")

    def test_rules_from_readme(self):
        guard.set_deny_rules(
            {
                "myproject": "csv",
                "myproject.api": [
                    "selenium",
                    mod.top_level("myproject.tasks"),
                ],
                "myproject.core": mod.matches(
                    r"myproject\.(api|business_logic)"
                ),
                "myproject.logging": ~mod.any(["logging", "yaml"]),
            }
        )

        assert not guard.is_import_allowed("myproject.api", "csv")
        assert not guard.is_import_allowed("myproject.api", "selenium")
        assert not guard.is_import_allowed("myproject.api", "myproject.tasks")
        assert not guard.is_import_allowed(
            "myproject.core.db", "myproject.api"
        )
        assert guard.is_import_allowed("myproject.api", "logging")
        assert guard.is_import_allowed(
            "myproject.api", "myproject.tasks", top_level=False
        )


if __name__ == "__main__":
    unittest.main()
