import warnings

from .matchers import mod
from .trie import Trie


class ForbiddenImportError(ImportError):
    pass


class ForbiddenImportWarning(UserWarning):
    pass


class Observer(object):
    def on_import_begin(self, import_info, stack, strict):
        raise NotImplementedError

    def on_import_end(self, import_info, stack, strict):
        pass


class TracingObserver(Observer):
    name = "tracer"

    def __init__(self):
        self.depth = 0

    def on_import_begin(self, import_info, stack, strict):
        print(
            "{indent} > {module_name}{is_lazy}".format(
                indent="  " * self.depth,
                module_name=import_info.module_name,
                is_lazy=" (lazy)" if stack[-1].is_lazy() else "",
            )
        )
        self.depth += 1

    def on_import_end(self, import_info, stack, strict):
        self.depth -= 1
        print(
            "{indent} < {module_name}{is_lazy}".format(
                indent="  " * self.depth,
                module_name=import_info.module_name,
                is_lazy=" (lazy)" if stack[-1].is_lazy() else "",
            )
        )


class DefendingObserver(Observer):
    name = "defender"

    def __init__(self, rules):
        self._rules = Trie()
        self._rules.update({k: mod(v) for k, v in rules.items()})
        self._seen_modules = set()

    def on_import_begin(self, import_info, stack, strict):
        for caller_info in reversed(stack):
            if not self.is_import_allowed(import_info, caller_info):
                break
        else:
            return

        # avoid duplicated warnings
        key = (
            import_info.module_name,
            caller_info.module_name,
            caller_info.function,
        )
        if key in self._seen_modules:
            return

        path = [(x.filename, x.lineno) for x in stack]

        message = "Importing `{}` from `{}` is not allowed [{}] ({})".format(
            import_info.module_name,
            caller_info.module_name,
            caller_info.depth,
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


# TODO
# class ProfilingObserver(Observer):
#     name = "profiler"
