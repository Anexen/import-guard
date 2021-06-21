from __future__ import print_function

import inspect
from functools import wraps

from .models import CallerInfo, ImportInfo
from .observers import DefendingObserver, TracingObserver


def _get_import_function():
    if isinstance(__builtins__, dict):
        return __builtins__["__import__"]

    return __builtins__.__import__


def _set_import_function(f):
    if isinstance(__builtins__, dict):
        __builtins__["__import__"] = f
    else:
        __builtins__.__import__ = f


_original_import = _get_import_function()

# see importlib._bootstrap_external._setup
_builtin_modules_injected_by_importlib = {
    "_io",
    "_warnings",
    "builtins",
    "marshal",
}

_skip_modules = {"linecache"} | _builtin_modules_injected_by_importlib


class _Guard:
    def __init__(self):
        self.strict = False
        self.entrypoint = None
        self._observers = {}

    def register(self, observer):
        name = getattr(observer, "name", observer.__class__.__name__)
        self._observers[name] = observer

    def trace(self):
        self.register(TracingObserver())

    def enable(self, strict=False, entrypoint=None):
        self.strict = strict

        if entrypoint is None:
            entrypoint = inspect.currentframe().f_back.f_code.co_filename

        self.entrypoint = entrypoint
        _set_import_function(self._import_hook)

    def disable(self):
        _set_import_function(_original_import)

    def set_deny_rules(self, rules):
        self.register(DefendingObserver(rules))

    def is_import_allowed(self, caller, imported_module, top_level=True):
        defender = self._observers.get("defender")

        if not defender:
            return True

        if isinstance(caller, str):
            caller = CallerInfo.from_string(caller, top_level)

        if isinstance(imported_module, str):
            imported_module = ImportInfo.from_string(imported_module)

        return defender.is_import_allowed(imported_module, caller)

    @wraps(_original_import)
    def _import_hook(
        self, name, globals_=None, locals_=None, fromlist=(), level=0
    ):
        # skip specific modules and private modules
        if name in _skip_modules or name[0] == "_":
            return _original_import(name, globals_, locals_, fromlist, level)

        parent_frame = inspect.currentframe().f_back

        full_name = ImportInfo.get_full_module_name(name, globals_, level)
        import_info = ImportInfo(full_name, fromlist, level)

        stack = CallerInfo.stack(parent_frame, self.entrypoint)

        try:
            for observer in self._observers.values():
                observer.on_import_begin(import_info, stack, self.strict)

            return _original_import(name, globals_, locals_, fromlist, level)
        finally:
            for observer in self._observers.values():
                observer.on_import_end(import_info, stack, self.strict)


guard = _Guard()
