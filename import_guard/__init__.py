"""Enforce that some modules can't be imported from other modules."""

from ._guard import ForbiddenImportError, ForbiddenImportWarning, guard
from .matchers import mod

__all__ = ["guard", "mod", "ForbiddenImportError", "ForbiddenImportWarning"]

__version__ = "0.0.1"
