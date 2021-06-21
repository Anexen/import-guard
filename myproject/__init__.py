# isort:skip_file

from import_guard import guard, mod


rules = {
    "myproject": "csv",
    # deny bisect OR top_level(myproject.tasks OR socket)
    "myproject.api": ["bisect", mod.top_level(["socket", "myproject.tasks"])],
    "myproject.core": mod.matches(r"myproject\.(api|business_logic)"),
    # deny explicit import for any modules except logging and yaml
    "myproject.logging": mod.explicit(~mod(["logging", "yaml"])),
}

guard.set_deny_rules(rules)
# guard.trace()
guard.enable()


from .api import run_server  # noqa:E402


def run():
    run_server()
