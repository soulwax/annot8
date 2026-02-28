"""Backward-compatible package alias for legacy ``pyannotate`` imports.

Prefer importing from ``annot8``.
"""

# pylint: disable=import-outside-toplevel

from typing import Any

__all__ = ["process_file", "walk_directory", "main"]


def process_file(*args: Any, **kwargs: Any):
    """Proxy to ``annot8.annotate_headers.process_file``."""
    from annot8.annotate_headers import process_file as _process_file

    return _process_file(*args, **kwargs)


def walk_directory(*args: Any, **kwargs: Any):
    """Proxy to ``annot8.annotate_headers.walk_directory``."""
    from annot8.annotate_headers import walk_directory as _walk_directory

    return _walk_directory(*args, **kwargs)


def main(*args: Any, **kwargs: Any):
    """Proxy to ``annot8.cli.main``."""
    from annot8.cli import main as _main

    return _main(*args, **kwargs)
