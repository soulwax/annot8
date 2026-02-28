# File: tests/__init__.py

"""Tests package."""

from typing import List

from . import test_utils as _test_utils
from .helpers import components as _components

# Re-export shared test utilities and components at the package level
__all__: List[str] = []

for _module in (_test_utils, _components):
    _public_names = getattr(_module, "__all__", None)
    if _public_names is None:
        _public_names = [name for name in dir(_module) if not name.startswith("_")]
    for _name in _public_names:
        globals()[_name] = getattr(_module, _name)
    __all__.extend(_public_names)

globals().pop("_module", None)
globals().pop("_public_names", None)
globals().pop("_name", None)
