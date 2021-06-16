import sys
from collections import namedtuple

CallerInfo = namedtuple(
    "CallerInfo", ["module_name", "function", "filename", "lineno"]
)

ImportInfo = namedtuple("ImportInfo", ["module_name", "from_list", "level"])

StackItem = namedtuple("stackItem", ["import_info", "caller_info"])

_module_cache = {}


def _get_filename_from_module(module):
    if hasattr(module, "__file__"):
        if module.__file__ is not None:
            return module.__file__.replace(".pyc", ".py")

    if hasattr(module, "__spec__"):
        return module.__spec__.origin


def _get_module_name_by_filename(filename):
    if filename in _module_cache:
        return _module_cache[filename]

    _module_cache.setdefault(filename, filename)

    _module_cache.update(
        {
            _get_filename_from_module(module): name
            for name, module in sys.modules.items()
            if hasattr(module, "__file__")
        }
    )

    return _module_cache[filename]


def caller_info_from_frame(frame):
    filename = frame.f_code.co_filename

    return CallerInfo(
        _get_module_name_by_filename(filename),
        frame.f_code.co_name,
        filename,
        frame.f_lineno,
    )


def is_lazy(caller_info):
    return caller_info.function == "<module>"
