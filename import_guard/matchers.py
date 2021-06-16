import re

from .models import is_lazy


def wrap(obj):
    if isinstance(obj, Matcher):
        return obj

    if isinstance(obj, str):
        return Exact(obj)

    if isinstance(obj, (list, tuple)):
        return Any(obj)

    if isinstance(obj, re.Pattern):
        return Regex(obj)

    raise TypeError


class Matcher:
    def matches(self, import_info, caller_info):
        raise NotImplementedError

    def __invert__(self):
        return Invert(self)

    def __or__(self, other):
        return Any([self, other])

    def __and__(self, other):
        return All([self, other])


class MultiMatcher(Matcher):
    def __init__(self, matchers):
        self.matchers = [wrap(x) for x in matchers]


class FlagMatcher(Matcher):
    def __repr__(self):
        return "Flags.{}".format(self.__class__.__name__)


class Invert(Matcher):
    def __init__(self, obj):
        self.matcher = wrap(obj)

    def matches(self, *args):
        return not self.matcher.matches(*args)

    def __repr__(self):
        return "(not {})".format(repr(self.matcher))


class Exact(Matcher):
    def __init__(self, module_name):
        self.module_name = module_name

    def matches(self, import_info, caller_info):
        return self.module_name == import_info.module_name

    def __repr__(self):
        return "'{}'".format(self.module_name)


class Regex(Matcher):
    def __init__(self, pattern):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern = pattern

    def matches(self, import_info, caller_info):
        return self.pattern.match(import_info.module_name)

    def __repr__(self):
        return "re('{}')".format(self.pattern.pattern)


class TopLevel(FlagMatcher):
    def matches(self, import_info, caller_info):
        return is_lazy(caller_info)


class Any(MultiMatcher):
    def matches(self, *args):
        return any(x.matches(*args) for x in self.matchers)

    def __repr__(self):
        return "({})".format(" | ".join(map(repr, self.matchers)))


class All(MultiMatcher):
    def matches(self, *args):
        return all(x.matches(*args) for x in self.matchers)

    def __repr__(self):
        return "({})".format(" & ".join(map(repr, self.matchers)))


class ModuleMatcherHelpers:
    any = Any
    all = All
    matches = Regex

    wrap = staticmethod(wrap)

    def __call__(self, module_name):
        return Exact(module_name)

    def top_level(self, matcher):
        return All([self.wrap(matcher), TopLevel()])

    def not_std(self):
        # TODO
        raise NotImplementedError

    def hook(self, func):
        # TODO
        raise NotImplementedError


mod = ModuleMatcherHelpers()
