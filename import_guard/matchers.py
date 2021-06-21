import re


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


class TopLevel(Matcher):
    def matches(self, import_info, caller_info):
        return not caller_info.is_lazy()

    def __repr__(self):
        return "TopLevel"


class Depth(Matcher):
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def matches(self, import_info, caller_info):
        return caller_info.depth <= self.max_depth

    def __repr__(self):
        return "Depth({})".format(self.max_depth)


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

    def __call__(self, module_name):
        return wrap(module_name)

    def top_level(self, matcher):
        return All([self(matcher), TopLevel()])

    def explicit(self, matcher):
        return self.depth(0, matcher)

    def depth(self, depth, matcher):
        return All([Depth(depth), self(matcher)])

    # def not_std(self):
    #     # TODO
    #     raise NotImplementedError

    # def hook(self, func):
    #     # TODO
    #     raise NotImplementedError


mod = ModuleMatcherHelpers()
