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
    # deny `csv` import from `test_proj` and submodules
    "test_proj": "csv",  # the same as mod("csv")
    # deny `selenium` and top_level `test_proj.tasks` imports from test_proj.api
    # but allow `test_proj.tasks` import inside the function (lazy import)
    # the same as mod("selenium") | (mod("test_proj.tasks") & Flags.TopLevel)
    "test_proj.api": ["selenium", mod.top_level("test_proj.tasks")],
    # deny `test_proj.api` and `test_proj.business_logic` imports from `test_proj.core`
    "test_proj.core": mod.matches(r"test_proj\.(api|business_logic)"),
    # deny all imports except `logging` and `yaml`
    "test_proj.logging": ~mod.any(["logging", "yaml"]),
})

# raise ForbiddenImportError
guard.enable(strict=True)
```

### Rules testing

```python
guard.is_import_allowed("test_proj.api", "csv")  # False
guard.is_import_allowed("test_proj.api", "logging")  # True
guard.is_import_allowed("test_proj.api", "selenium")  # False
guard.is_import_allowed("test_proj.api", "test_proj.tasks")  # False
guard.is_import_allowed("test_proj.api", "test_proj.tasks", top_level=False)  # True
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
    "test_proj.core": [
        # deny top-level import of `test_proj.api` and `test_proj.business_logic`
        mod.top_level(mod.matches(r"test_proj\.(api|business_logic)"))
    ],
    # deny all imports expect `logging` and lazy sentry
    "test_proj.logging": ~mod.any(["logging", mod.top_level("sentry")]),
})
```

### lazy imports only

```python
guard.set_deny_rules({
    "test_proj.business_logic": mod.top_level(mod.matches(".*")),
})
```
