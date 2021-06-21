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
    "test_proj.logging": ~mod.explicit(["logging", "yaml"]),
})

# raise ForbiddenImportError
guard.enable(strict=True)
```

# Rules

> the code below is copy-pastable into the Python interpreter
> and assumes the following imports:

```python
from importlib import reload
from import_guard import guard, mod
# enable guard in advance
guard.enable()
```

#### Exact match

```python
guard.set_deny_rules({"<stdin>": "decimal"})
# shortcut for mod("decimal")

# matches:
from decimal import Decimal

# doesn't match:
from enum import Enum
```

#### Explicit match

Consider the following code:

```python
guard.set_deny_rules({"<stdin>": "re"})

import csv  # shows warning!
```

What happened?

`csv` imports some modules under the hood, e.g. `re` or `io`.
`main.py` implicitly initiated `re` module loading through the `csv` module (rules matches at the depth = 1).
This is the default behavior. You can check only explicit imports using `mod.explicit("re")` function.

```python
guard.set_deny_rules({"<stdin>": mod.explicit("re")})
reload(csv)
```

#### Match multiple modules

```python
guard.set_deny_rules({"<stdin>": ["logging", "json"]})
# the same as mod.any(["logging", "json'])
# the same as mod("logging") | mod("json")

# matches
import json
from logging import getLogger
```

#### Match by regular expression

```python
guard.set_deny_rules({"<stdin>": mod.matches("log.*")})

# shows multiple warnings
from logging.config import dictConfig
```

#### Inversion

```python
guard.set_deny_rules({"<stdin>": ~mod.matches("log.*")})

import io
```

#### Match only module-level imports

It's common practice doing a local import instead of a global one to break a
cycle import or to postpone importing until you run code that actually needs
the module you're importing.

```python
guard.set_deny_rules({"<stdin>": mod.top_level("array")})

def some_function():
    import array

some_function()  # allowed
import array  # shows warning
```

#### Complex rules

Rules are very flexible. You can combine them together in a different ways
and build very complex conditions.

```python
mod.explicit(
    ~mod.top_level(["math", "json"])
    | mod.matches("log.*")
)
```

Nice example: deny non-lazy imports in some module:

```python
guard.set_deny_rules({
    "test_proj.business_logic": mod.top_level(mod.matches(".*")),
})
```

#### Non-strict mode

```python
# not enabled for `prod`
if env == "staging":
    # warn on forbidden import
    guard.enable(strict=False)
elif env == "local":
    # raise ForbiddenImportError
    guard.enable(strict=True)
```

# Testing

### Rules

Testing rules directly:

```python
rule = mod.top_level(mod.matches(".*"))
# True; mod1 imported at the module level in mod2
rule.test("mod1", caller="mod2")
# False; mod1 doesn't match the top_level constraint
rule.test("mod1", caller="<stdin>", top_level=False)
```

Testing deny rules through the guard:

```python
guard.is_import_allowed("test_proj.api", "csv")  # False
guard.is_import_allowed("test_proj.api", "logging")  # True
guard.is_import_allowed("test_proj.api", "selenium")  # False
guard.is_import_allowed("test_proj.api", "test_proj.tasks")  # False
guard.is_import_allowed("test_proj.api", "test_proj.tasks", top_level=False)  # True
```

### Unit tests

Testing with current Python interpreter:

```bash
$ python -m unittest discover tests -v
```

Testing with different Python versions and interpreters:

```bash
$ tox
```
