# File: tests/test_cjs_mjs.py

"""Tests for CommonJS (.cjs) and ES Module (.mjs) file annotation handling.

Covers:
- Basic annotation of .cjs and .mjs files
- Shebang preservation in .cjs files
- Existing header detection (correct and wrong comment style)
- Idempotency (re-running doesn't duplicate or corrupt)
- JSDoc-style block comment files
- Content-based fallback skipping shebangs
"""

from pathlib import Path

import pytest

from annot8.annotate_headers import _get_comment_style, _has_existing_header, process_file
from tests.test_utils import cleanup_test_directory, create_temp_test_directory

TEST_DIR = Path("tests/sample_cjs_mjs")


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Setup test environment and cleanup after tests."""
    create_temp_test_directory(TEST_DIR)
    yield
    cleanup_test_directory(TEST_DIR)


class TestCjsMjsCommentStyleDetection:
    """Test that .cjs and .mjs files are recognized with // comment style."""

    def test_cjs_comment_style(self):
        """CJS files should use // comment style."""
        cjs_file = TEST_DIR / "test.cjs"
        cjs_file.write_text("module.exports = {};\n")
        style = _get_comment_style(cjs_file)
        assert style == ("//", ""), f"Expected ('//','') for .cjs, got {style}"

    def test_mjs_comment_style(self):
        """MJS files should use // comment style."""
        mjs_file = TEST_DIR / "test.mjs"
        mjs_file.write_text("export default {};\n")
        style = _get_comment_style(mjs_file)
        assert style == ("//", ""), f"Expected ('//','') for .mjs, got {style}"


class TestCjsBasicAnnotation:
    """Test basic annotation of .cjs files."""

    def test_simple_cjs_file(self):
        """A plain .cjs file gets a // File: header."""
        cjs_file = TEST_DIR / "simple.cjs"
        cjs_file.write_text("module.exports = { foo: 'bar' };\n")
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        assert content.startswith("// File: simple.cjs\n")
        assert "module.exports" in content

    def test_simple_mjs_file(self):
        """A plain .mjs file gets a // File: header."""
        mjs_file = TEST_DIR / "simple.mjs"
        mjs_file.write_text("export const foo = 'bar';\n")
        process_file(mjs_file, TEST_DIR)
        content = mjs_file.read_text()
        assert content.startswith("// File: simple.mjs\n")
        assert "export const foo" in content


class TestCjsShebangHandling:
    """Test shebang handling in .cjs files."""

    def test_cjs_with_shebang_no_existing_header(self):
        """A .cjs file with shebang should get // header after the shebang."""
        cjs_file = TEST_DIR / "cli.cjs"
        cjs_file.write_text("#!/usr/bin/env node\nconsole.log('hello');\n")
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        lines = content.splitlines()
        assert lines[0] == "#!/usr/bin/env node", "Shebang must be preserved"
        assert lines[1] == "// File: cli.cjs", "Header must be // style after shebang"
        assert "console.log" in content

    def test_cjs_with_shebang_idempotent(self):
        """Running annot8 twice on a shebang .cjs file should not duplicate headers."""
        cjs_file = TEST_DIR / "cli_idem.cjs"
        cjs_file.write_text("#!/usr/bin/env node\nconsole.log('hello');\n")
        process_file(cjs_file, TEST_DIR)
        first_pass = cjs_file.read_text()
        process_file(cjs_file, TEST_DIR)
        second_pass = cjs_file.read_text()
        assert first_pass == second_pass, "Second pass should not change the file"

    def test_cjs_shebang_no_hash_comment(self):
        """A .cjs file with shebang must NOT get a # File: header (bug regression)."""
        cjs_file = TEST_DIR / "no_hash.cjs"
        cjs_file.write_text("#!/usr/bin/env node\nconst x = 1;\n")
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        assert "# File:" not in content, "Must not use # comment style for .cjs"
        assert "// File:" in content, "Must use // comment style for .cjs"


class TestCjsExistingHeaderHandling:
    """Test handling of files that already have annotations."""

    def test_cjs_with_correct_existing_header(self):
        """A .cjs file with a correct // File: header should not be re-annotated."""
        cjs_file = TEST_DIR / "already_annotated.cjs"
        original = "// File: already_annotated.cjs\nmodule.exports = {};\n"
        cjs_file.write_text(original)
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        # Count occurrences of "File:" - should be exactly 1
        assert content.count("File:") == 1, "Should not add duplicate header"

    def test_cjs_with_wrong_hash_header(self):
        """A .cjs file with a wrong # File: header (from previous bug) should be fixed."""
        cjs_file = TEST_DIR / "wrong_hash.cjs"
        cjs_file.write_text("# File: wrong_hash.cjs\nmodule.exports = {};\n")
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        # The wrong header should be detected and replaced
        assert "# File:" not in content, "Wrong # header should be removed"
        assert "// File: wrong_hash.cjs" in content, "Correct // header should be added"

    def test_cjs_shebang_with_wrong_hash_header(self):
        """A .cjs file with shebang + wrong # File: header should be corrected."""
        cjs_file = TEST_DIR / "shebang_wrong.cjs"
        cjs_file.write_text("#!/usr/bin/env node\n# File: shebang_wrong.cjs\nconst x = 1;\n")
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        lines = content.splitlines()
        assert lines[0] == "#!/usr/bin/env node", "Shebang must be preserved"
        assert "# File:" not in content, "Wrong # header should be gone"
        assert "// File: shebang_wrong.cjs" in content, "Correct // header should be present"

    def test_cjs_shebang_with_correct_header_already(self):
        """A .cjs with shebang + correct // File: header should be left alone."""
        cjs_file = TEST_DIR / "shebang_correct.cjs"
        original = "#!/usr/bin/env node\n// File: shebang_correct.cjs\n\nconst x = 1;\n"
        cjs_file.write_text(original)
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        assert content.count("File:") == 1, "Should not duplicate header"
        assert content.startswith("#!/usr/bin/env node\n")


class TestCjsJSDocBlockComment:
    """Test that .cjs files starting with JSDoc blocks are handled correctly."""

    def test_cjs_with_jsdoc_block(self):
        """A .cjs file starting with a JSDoc block should get // header, not /* */."""
        cjs_file = TEST_DIR / "ecosystem.docker.cjs"
        cjs_file.write_text(
            "/**\n"
            " * PM2 config for Docker.\n"
            " * Env is provided by the container.\n"
            " */\n"
            "module.exports = {\n"
            "  apps: [{ name: 'app', script: 'index.js' }]\n"
            "};\n"
        )
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        assert content.startswith(
            "// File: ecosystem.docker.cjs\n"
        ), "Header should use // style, not /* */"
        assert "/* File:" not in content, "Must not use block comment for header"
        # JSDoc block should be preserved
        assert "PM2 config for Docker." in content

    def test_cjs_with_jsdoc_idempotent(self):
        """Re-running on a .cjs with JSDoc + correct header should be idempotent."""
        cjs_file = TEST_DIR / "eco_idem.cjs"
        cjs_file.write_text(
            "// File: eco_idem.cjs\n\n" "/**\n" " * Some JSDoc.\n" " */\n" "module.exports = {};\n"
        )
        original = cjs_file.read_text()
        process_file(cjs_file, TEST_DIR)
        content = cjs_file.read_text()
        assert content == original, "Already-annotated file should not change"


class TestContentBasedFallbackShebang:
    """Test that the content-based comment style fallback skips shebangs."""

    def test_unknown_ext_with_shebang_and_js_comment(self):
        """An unrecognized extension with shebang + // content should detect //."""
        weird_file = TEST_DIR / "script.weird"
        weird_file.write_text("#!/usr/bin/env node\n// some comment\nconst x = 1;\n")
        style = _get_comment_style(weird_file)
        assert style == (
            "//",
            "",
        ), f"Should detect // from content after skipping shebang, got {style}"

    def test_unknown_ext_with_shebang_and_hash_comment(self):
        """An unrecognized extension with shebang + # content should detect #."""
        weird_file = TEST_DIR / "script.weird2"
        weird_file.write_text("#!/bin/bash\n# some comment\necho hello\n")
        style = _get_comment_style(weird_file)
        assert style == (
            "#",
            "",
        ), f"Should detect # from content after skipping shebang, got {style}"


class TestHasExistingHeaderWrongStyle:
    """Test that _has_existing_header detects headers written with wrong comment style."""

    def test_detects_hash_header_when_expecting_slashes(self):
        """Should detect # File: even when comment_start is //."""
        lines = ["# File: some_file.cjs", "module.exports = {};"]
        assert _has_existing_header(
            lines, "//"
        ), "Should detect # File: header even with // comment_start"

    def test_detects_block_comment_header_when_expecting_slashes(self):
        """Should detect /* File: even when comment_start is //."""
        lines = ["/* File: some_file.cjs */", "module.exports = {};"]
        assert _has_existing_header(
            lines, "//"
        ), "Should detect /* File: header even with // comment_start"

    def test_does_not_false_positive(self):
        """Should not detect a header where there is none."""
        lines = ["module.exports = {};", "const x = 1;"]
        assert not _has_existing_header(lines, "//"), "Should not detect header in plain code"
