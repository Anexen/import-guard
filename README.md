# import-guard

Enforce that some modules can't be imported from other modules. In runtime!

> If you need a static analysis tools, take a look at [flake8-import-graph](https://pypi.org/project/flake8-import-graph/).

Features:

- works in runtime
- checks dynamic imports
- customizable rules

> This library has some performance overhead.
> In some cases it may lead to 2-3x slower import time (and startup time respectively).
> It's recommended to enable import_guard only during the development.

# Usage

```python
from import_guard import guard, mod


guard.set_deny_rules({
    # deny `csv` import from `myproject` and submodules
    "myproject": "csv",  # the same as mod("csv")
    # deny `selenium` and top_level `myproject.tasks` imports from myproject.api
    # but allow `myproject.tasks` import inside the function (lazy import)
    # the same as mod("selenium") | (mod("myproject.tasks") & Flags.TopLevel)
    "myproject.api": ["selenium", mod.top_level("myproject.tasks")],
    # deny `myproject.api` and `myproject.business_logic` imports from `myproject.core`
    "myproject.core": mod.matches(r"myproject\.(api|business_logic)"),
    # deny all imports except `logging` and `yaml`
    "myproject.logging": ~mod.any(["logging", "yaml"]),
})

# raise ForbiddenImportError
guard.enable(strict=True)
```

### Rules testing

```python
guard.is_import_allowed("myproject.api", "csv")  # False
guard.is_import_allowed("myproject.api", "logging")  # True
guard.is_import_allowed("myproject.api", "selenium")  # False
guard.is_import_allowed("myproject.api", "myproject.tasks")  # False
guard.is_import_allowed("myproject.api", "myproject.tasks", top_level=False)  # True
```

# Advanced usage

### non-strict mode

```python
# not enabled for `prod`
if env == 'staging':
    # warn on forbidden import
    guard.enable(strict=False)
elif env == 'local':
    # raise ForbiddenImportError
    guard.enable(strict=True)
```

### mixed rules

```python
guard.set_deny_rules({
    "myproject.core": [
        # deny top-level import of `myproject.api` and `myproject.business_logic`
        mod.top_level(mod.matches(r"myproject\.(api|business_logic)"))
    ],
    # deny all imports expect `logging` and lazy sentry
    "myproject.logging": ~mod.any(["logging", mod.top_level("sentry")]),
})
```

### lazy imports only

```python
guard.set_deny_rules({
    "myproject.business_logic": mod.top_level(mod.matches(".*")),
})
```
