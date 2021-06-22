from collections import namedtuple
from sys import modules as sys_modules


__all__ = ["ImportInfo", "CallerInfo"]


def iter_stack(frame, entrypoints):
    while frame:
        filename = frame.f_code.co_filename

        if (
            filename.startswith("<frozen importlib")
            or "import_guard/" in filename
        ):
            frame = frame.f_back
            continue

        yield frame

        if filename in entrypoints:
            break

        frame = frame.f_back


class ImportInfo(
    namedtuple(
        "_ImportInfo",
        [
            "module_name",
            "from_list",
            "level",
        ],
    )
):
    @classmethod
    def from_string(cls, imported_module):
        return cls(imported_module, None, 0)

    @staticmethod
    def get_full_module_name(name, globals_, level):
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


class CallerInfo(
    namedtuple(
        "_CallerInfo",
        [
            "module_name",
            "function",
            "filename",
            "lineno",
            "depth",
        ],
    )
):
    _module_cache = {}
    _module_cache_keys = set()

    @classmethod
    def from_frame(cls, frame, depth=0, _is_lazy=False):
        filename = frame.f_code.co_filename
        co_name = frame.f_code.co_name

        return cls(
            cls._get_module_name_by_filename(filename),
            co_name if not _is_lazy else "<lazy {}>".format(co_name),
            filename,
            frame.f_lineno,
            depth,
        )

    @classmethod
    def from_string(cls, caller, top_level=True):
        return cls(
            caller,
            function="<module>" if top_level else "<lazy>",
            filename="main.py",
            lineno=0,
            depth=0,
        )

    @classmethod
    def stack(cls, initial_frame, entrypoints):
        is_lazy = False
        stack = []

        for depth, frame in reversed(
            list(enumerate(iter_stack(initial_frame, entrypoints)))
        ):
            info = CallerInfo.from_frame(frame, depth, is_lazy)

            if not is_lazy:
                is_lazy = info.is_lazy()

            stack.append(info)

        return stack

    def is_lazy(self):
        return self.function != "<module>"

    @classmethod
    def _get_module_name_by_filename(cls, filename):
        cache = cls._module_cache

        if filename in cache:
            return cache[filename]

        modules_to_fetch = set(sys_modules) - cls._module_cache_keys

        for name in modules_to_fetch:
            module = sys_modules[name]
            f = getattr(module, "__file__", None)
            if f is not None:
                cache[f[:-1] if f[-3:] == "pyc" else f] = name
            else:
                spec = getattr(module, "__spec__", None)
                if spec is not None:
                    cache[spec.origin] = name

        cls._module_cache_keys.update(modules_to_fetch)
        return cache.get(filename, filename)
