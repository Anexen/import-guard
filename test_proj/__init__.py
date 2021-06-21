# isort:skip_file

from import_guard import guard, mod


rules = {
    "test_proj": "csv",
    # deny bisect OR top_level(test_proj.tasks OR socket)
    "test_proj.api": ["bisect", mod.top_level(["socket", "test_proj.tasks"])],
    "test_proj.core": mod.matches(r"test_proj\.(api|business_logic)"),
    # deny explicit import for any modules except logging and yaml
    "test_proj.logging": mod.explicit(~mod(["logging", "yaml"])),
}

guard.set_deny_rules(rules)
# guard.trace()
guard.enable()


from .api import run_server  # noqa:E402


def run():
    run_server()
