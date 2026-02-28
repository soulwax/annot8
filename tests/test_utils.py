# File: tests/test_utils.py
# pylint: disable=duplicate-code

"""Shared utilities for tests to reduce code duplication."""

import json
import shutil
from pathlib import Path

from annot8.annotate_headers import process_file
from annot8.config import load_config


def create_temp_test_directory(test_dir: Path) -> None:
    """Create a temporary test directory, removing it if it exists."""
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)


def cleanup_test_directory(test_dir: Path) -> None:
    """Clean up a test directory."""
    if test_dir.exists():
        shutil.rmtree(test_dir)


def create_test_file_with_header_processing(
    file_path: Path, content: str, project_root: Path
) -> str:
    """Create a test file, process it, and return the processed content."""
    file_path.write_text(content)
    process_file(file_path, project_root)
    return file_path.read_text()


def process_test_file_with_json_config(
    project_root: Path, file_name: str, file_content: str, config_data: dict
) -> str:
    """
    Write a JSON configuration file, process a single test file, and return its
    processed content.

    Parameters
    ----------
    project_root:
        Root directory for the test project where the `.annot8.json` config
        file will be written and from which configuration is loaded.
    file_name:
        Name of the file to create and process relative to ``project_root``.
    file_content:
        Initial content to write into the test file before processing.
    config_data:
        Dictionary representing the annot8 configuration to be written to
        ``.annot8.json``. This should be JSON-serializable and match the
        structure expected by ``load_config`` (for example, containing any
        header or file-matching options required by the tests).

    Returns
    -------
    str
        The full text content of the test file after it has been processed
        by ``process_file`` using the provided configuration.
    """
    config_file = project_root / ".annot8.json"
    config_file.write_text(json.dumps(config_data))

    test_file = project_root / file_name
    test_file.write_text(file_content)

    config = load_config(project_root)
    process_file(test_file, project_root, config=config)
    return test_file.read_text()


def assert_file_content_unchanged(
    file_path: Path, original_content: str, file_description: str
) -> None:
    """Assert that a file's content has not changed."""
    processed_content = file_path.read_text()
    assert (
        processed_content == original_content
    ), f"{file_description} was modified but should be ignored"


def assert_header_added(file_path: Path, expected_header_start: str, file_description: str) -> None:
    """Assert that a header was added to a file."""
    content = file_path.read_text()
    assert content.startswith(
        expected_header_start
    ), f"Header not added correctly for {file_description}"


def create_standard_test_env(test_dir: Path) -> None:
    """Create a standard test environment with common files."""
    create_temp_test_directory(test_dir)

    # Create basic test files
    (test_dir / "test.py").write_text("print('Hello, World!')")
    (test_dir / "test.js").write_text("console.log('Hello, World!');")
    (test_dir / "test.css").write_text("body { margin: 0; }")

    # Create nested directory
    nested_dir = test_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "script.sh").write_text('#!/bin/bash\necho "Hello!"')


def prepare_existing_header_js(test_dir: Path, filename: str = "existing_header.js") -> Path:
    """
    Write a JS file with a legacy header used by multiple tests and return its path.
    This centralizes setup to avoid duplicate code across test modules.
    """
    js_file = test_dir / filename
    js_file.write_text("""// Old header comment
// Author: Someone
console.log("Hello, World!");""")
    return js_file
