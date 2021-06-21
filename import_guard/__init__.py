"""Enforce that some modules can't be imported from other modules."""

from ._guard import guard
from .matchers import mod
from .observers import ForbiddenImportError, ForbiddenImportWarning


__all__ = ["guard", "mod", "ForbiddenImportError", "ForbiddenImportWarning"]

__version__ = "0.0.1"
