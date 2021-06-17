"""Enforce that some modules can't be imported from other modules."""

from __future__ import print_function

import inspect
import warnings
from functools import wraps

from .matchers import mod
from .models import CallerInfo, ImportInfo, caller_info_from_frame, is_lazy
from .trie import Trie

__all__ = ["guard", "mod", "ForbiddenImportError", "ForbiddenImportWarning"]


def get_import_function():
    if isinstance(__builtins__, dict):
        return __builtins__["__import__"]

    return __builtins__.__import__


def set_import_function(f):
    if isinstance(__builtins__, dict):
        __builtins__["__import__"] = f
    else:
        __builtins__.__import__ = f


_original_import = get_import_function()

# def iter_callers(frame):
#     _is_lazy = False

#     for _frame in reversed(list(stack_trace(frame))):
#         info = caller_info_from_frame(_frame)
#         if _is_lazy:
#             if not is_lazy(info):
#                 info = info._replace(function="<lazy module>")
#         else:
#             _is_lazy = is_lazy(info)

#         yield info


class ForbiddenImportError(ImportError):
    pass


class ForbiddenImportWarning(UserWarning):
    pass


class _Observer(object):
    def on_import_begin(self, import_info, caller_info, stack, strict):
        raise NotImplementedError

    def on_import_end(self, import_info, caller_info, stack, strict):
        pass


class _TracingObserver(_Observer):
    name = "tracer"

    def on_import_begin(self, import_info, caller_info, stack, strict):
        print("  " * len(stack) + ">", import_info.module_name)

    def on_import_end(self, import_info, caller_info, stack, strict):
        print("  " * len(stack) + "<", import_info.module_name)


class _DefendingObserver(_Observer):
    name = "defender"

    def __init__(self, rules):
        self._rules = Trie()
        self._rules.update({k: mod.wrap(v) for k, v in rules.items()})
        self._seen_modules = set()

    def on_import_begin(self, import_info, caller_info, stack, strict):
        if self.is_import_allowed(import_info, caller_info):
            return

        # avoid duplicated warnings
        key = (
            import_info.module_name,
            caller_info.module_name,
            caller_info.function,
        )
        if key in self._seen_modules:
            return

        path = [(x.filename, x.lineno) for _, x in reversed(stack)]

        message = "Importing `{}` from `{}` is not allowed ({})".format(
            import_info.module_name,
            caller_info.module_name,
            " -> ".join(map(lambda x: "{}:{}".format(*x), path)),
        )

        if strict:
            raise ForbiddenImportError(message)

        warnings.warn(message, ForbiddenImportWarning, stacklevel=4)
        self._seen_modules.add(key)

    def is_import_allowed(self, import_info, caller_info):
        caller = caller_info.module_name

        for node in self._rules.path(caller):
            if node.data.matches(import_info, caller_info):
                return False

        return True


class _ProfilingObserver(_Observer):
    # TODO
    name = "profiler"


class _Guard:
    def __init__(self):
        self.strict = False
        self._stack = []
        self._observers = {}

    def register(self, observer):
        name = getattr(observer, "name", observer.__class__.__name__)
        self._observers[name] = observer

    def trace(self):
        self.register(_TracingObserver())

    def enable(self, strict=False):
        set_import_function(self._import_hook)
        self.strict = strict

    def disable(self):
        set_import_function(_original_import)

    def set_deny_rules(self, rules):
        self.register(_DefendingObserver(rules))

    def is_import_allowed(self, caller, imported_module, top_level=True):
        defender = self._observers.get("defender")

        if not defender:
            return True

        if isinstance(caller, str):
            caller = CallerInfo(
                caller,
                function="<module>" if top_level else "dummy",
                filename="main.py",
                lineno=0,
            )

        if isinstance(imported_module, str):
            imported_module = ImportInfo(imported_module, None, 0)

        return defender.is_import_allowed(imported_module, caller)

    @wraps(_original_import)
    def _import_hook(
        self, name, globals_=None, locals_=None, fromlist=(), level=0
    ):
        parent_frame = inspect.currentframe().f_back
        full_name = self._get_full_module_name(name, globals_, level)

        import_info = ImportInfo(full_name, fromlist, level)
        caller_info = caller_info_from_frame(parent_frame)

        self._stack.append((import_info, caller_info))

        self._on_import("begin", import_info, caller_info)

        try:
            return _original_import(name, globals_, locals_, fromlist, level)
        finally:
            self._on_import("end", import_info, caller_info)
            self._stack.pop()

    def _on_import(self, event, import_info, caller_info):
        for observer in self._observers.values():
            method = getattr(observer, "on_import_" + event)
            method(import_info, caller_info, self._stack, self.strict)

    def _get_full_module_name(self, name, globals_, level):
        if level == 0 or not globals_:
            # absolute import
            return name

        # calculate package from the relative import:
        # from .exceptions import Error

        # see _calc___package__ from importlib._bootstrap
        package = globals_.get("__package__")

        if package is None:
            spec = globals_.get("__spec__")
            if spec is not None:
                package = spec.parent
            else:
                package = globals_["__name__"]

                if "__path__" not in globals_:
                    package = package.rpartition(".")[0]

        package = package.split(".")

        # from . import exceptions
        # leads to empty name
        if name:
            package.append(name)

        return ".".join(package)


guard = _Guard()
