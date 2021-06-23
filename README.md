# import-guard

Enforce that some modules can't be imported from other modules. In runtime!

> If you need a static analysis tools, take a look at [flake8-import-graph](https://pypi.org/project/flake8-import-graph/).

Features:

- works in runtime
- checks dynamic imports
- customizable rules

> This library has some performance overhead.
> In some cases it may lead to 1.5-2x slower import time (and startup time respectively).
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

from decimal import Decimal  # shows warning

from enum import Enum  # ok
```

#### Explicit match

Consider the following code:

```python
guard.set_deny_rules({"<stdin>": "re"})

import csv  # shows warning!
```

What happened?

`csv` imports some modules under the hood, e.g. `re` or `io`.
We implicitly initiated loading of the `re` module through the `csv` module (rule matches at depth = 1).
This is the default behavior. You can check only explicit imports using `mod.explicit("re")` function.

```python
guard.set_deny_rules({"<stdin>": mod.explicit("re")})
reload(csv)  # allowed
import re  # shows warning
```

#### Match multiple modules

```python
guard.set_deny_rules({"<stdin>": ["logging", "json"]})
# the same as mod.any(["logging", "json'])
# the same as mod("logging") | mod("json")


import json  # shows warning
from logging import getLogger  # shows warning
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

import io # shows warning
```

#### Match only module-level imports

It's common practice doing a local import instead of a global one to break a
cycle import or to postpone importing until you run code that actually needs
the module you're importing.

```python
# deny module-level imports
guard.set_deny_rules({"<stdin>": mod.top_level("array")})

def some_function():
    import array  # allowed (lazy import)

some_function()
import array  # shows warning
```

#### Match star import

```python
guard.set_deny_rules({"<stdin>": mod.star("csv")})

from csv import *  # shows warning
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

Nice examples:

- deny non-lazy imports in some module:

```python
guard.set_deny_rules({
    "test_proj.business_logic": mod.top_level(mod.matches(".*")),
})
```

- deny start imports in project:

```python
guard.set_deny_rules({
    "test_proj": mod.star(mod.explicit(mod.matches(".*"))),
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

#### Rules hierarchy

The set of deny rule for a module also affects its submodules.

```python
guard.set_deny_rules({
    "test_proj": "json",
    "test_proj.api": ["selenum", "pandas"],
    "test_proj.core": "celery"
})
```

`test_proj.core` disallows `json` and `celery` imports.
`test_proj.api.views` disallows `json`, `selenium`, `pandas` imports.

#### Lazy module

Consider the following project structure:

```python
# main.py
import api

# api.py
def view():
    import tasks

# tasks.py
import pandas
```

Here `main.py` imports `api`, which imports `tasks` lazily, which imports `pandas` at module level.
`import_guard` handles this case as lazy module import and will think that pandas being imported lazily.
Thus, in this case, the following rules do not raise a warning:

```python
guard.set_deny_rules({"tasks": mod.top_level("pandas")})
```

#### Custom module matcher

```python
def is_relative_import(import_info, caller_info):
    return import_info.level > 1

# deny relative import
guard.set_deny_rules({"proj": mod.hook(is_relative_import)})

from .api import view  # shows warning
from proj.api import view  # ok
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
guard.is_import_allowed("csv", caller="test_proj.api")  # False
guard.is_import_allowed("logging", caller="test_proj.api")  # True
guard.is_import_allowed("selenium", caller="test_proj.api")  # False
guard.is_import_allowed(
    "test_proj.tasks", caller="test_proj.api"
)  # False
guard.is_import_allowed(
    "test_proj.tasks", caller="test_proj.api", top_level=False
)  # True
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
