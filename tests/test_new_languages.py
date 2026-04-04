# File: tests/test_new_languages.py
# pylint: disable=duplicate-code,too-few-public-methods

"""Tests for language support added in 0.12.4."""

from pathlib import Path

import pytest

from annot8.annotate_headers import _get_comment_style, process_file
from tests.test_utils import cleanup_test_directory, create_temp_test_directory

TEST_DIR = Path("tests/sample_files_new")


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Setup test environment and cleanup after tests."""
    create_temp_test_directory(TEST_DIR)
    yield
    cleanup_test_directory(TEST_DIR)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _write_process_read(name: str, content: str) -> str:
    f = TEST_DIR / name
    f.write_text(content)
    process_file(f, TEST_DIR)
    return f.read_text()


# ---------------------------------------------------------------------------
# Systems programming
# ---------------------------------------------------------------------------


class TestCUDA:
    def test_comment_style(self):
        f = TEST_DIR / "kernel.cu"
        f.write_text("__global__ void add(int *a, int *b) {}")
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("kernel.cu", "__global__ void add(int *a) {}")
        assert result.startswith("// File: kernel.cu")

    def test_cuh_comment_style(self):
        f = TEST_DIR / "device.cuh"
        f.write_text("#pragma once")
        assert _get_comment_style(f) == ("//", "")


class TestSystemVerilog:
    def test_comment_style(self):
        f = TEST_DIR / "counter.sv"
        f.write_text("module counter(input clk);")
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("counter.sv", "module counter(input clk);")
        assert result.startswith("// File: counter.sv")

    def test_svh_comment_style(self):
        f = TEST_DIR / "types.svh"
        f.write_text("`ifndef TYPES_SVH")
        assert _get_comment_style(f) == ("//", "")


class TestDLanguage:
    def test_comment_style(self):
        f = TEST_DIR / "main.d"
        f.write_text("void main() {}")
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("main.d", "void main() {}")
        assert result.startswith("// File: main.d")


class TestKotlinScript:
    def test_comment_style(self):
        f = TEST_DIR / "build.gradle.kts"
        # suffix is .kts
        f.write_text('plugins { kotlin("jvm") }')
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("build.kts", 'plugins { kotlin("jvm") }')
        assert result.startswith("// File: build.kts")


# ---------------------------------------------------------------------------
# Build systems
# ---------------------------------------------------------------------------


class TestCMake:
    def test_comment_style(self):
        f = TEST_DIR / "CMakeLists.cmake"
        f.write_text("cmake_minimum_required(VERSION 3.10)")
        assert _get_comment_style(f) == ("#", "")

    def test_header_added(self):
        result = _write_process_read("find_package.cmake", "find_package(Boost)")
        assert result.startswith("# File: find_package.cmake")


class TestMakeIncludes:
    def test_mk_comment_style(self):
        f = TEST_DIR / "rules.mk"
        f.write_text("CC = gcc")
        assert _get_comment_style(f) == ("#", "")

    def test_mk_header_added(self):
        result = _write_process_read("rules.mk", "CC = gcc\nLDFLAGS = -lm")
        assert result.startswith("# File: rules.mk")


class TestBazelStarlark:
    def test_bzl_comment_style(self):
        f = TEST_DIR / "defs.bzl"
        f.write_text("def my_rule():\n    pass")
        assert _get_comment_style(f) == ("#", "")

    def test_bzl_header_added(self):
        result = _write_process_read("defs.bzl", "def my_rule():\n    pass")
        assert result.startswith("# File: defs.bzl")

    def test_star_comment_style(self):
        f = TEST_DIR / "macros.star"
        f.write_text("def macro():\n    pass")
        assert _get_comment_style(f) == ("#", "")


# ---------------------------------------------------------------------------
# Game / scripting
# ---------------------------------------------------------------------------


class TestGDScript:
    def test_comment_style(self):
        f = TEST_DIR / "player.gd"
        f.write_text("extends Node\nfunc _ready():\n    pass")
        assert _get_comment_style(f) == ("#", "")

    def test_header_added(self):
        result = _write_process_read("player.gd", "extends Node\nfunc _ready():\n    pass")
        assert result.startswith("# File: player.gd")


class TestWren:
    def test_comment_style(self):
        f = TEST_DIR / "game.wren"
        f.write_text("class Game {}")
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("game.wren", "class Game {}")
        assert result.startswith("// File: game.wren")


class TestAngelScript:
    def test_comment_style(self):
        f = TEST_DIR / "script.as"
        f.write_text("void main() {}")
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("script.as", "void main() {}")
        assert result.startswith("// File: script.as")


# ---------------------------------------------------------------------------
# Smart contracts
# ---------------------------------------------------------------------------


class TestSolidity:
    def test_comment_style(self):
        f = TEST_DIR / "Token.sol"
        f.write_text("pragma solidity ^0.8.0;")
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("Token.sol", "pragma solidity ^0.8.0;\ncontract Token {}")
        assert result.startswith("// File: Token.sol")


# ---------------------------------------------------------------------------
# Functional / research languages
# ---------------------------------------------------------------------------


class TestPureScript:
    def test_comment_style(self):
        f = TEST_DIR / "Main.purs"
        f.write_text("module Main where")
        assert _get_comment_style(f) == ("--", "")

    def test_header_added(self):
        result = _write_process_read("Main.purs", "module Main where\nmain = pure unit")
        assert result.startswith("-- File: Main.purs")


class TestDhall:
    def test_comment_style(self):
        f = TEST_DIR / "config.dhall"
        f.write_text('{ name = "example" }')
        assert _get_comment_style(f) == ("--", "")

    def test_header_added(self):
        result = _write_process_read("config.dhall", '{ name = "example" }')
        assert result.startswith("-- File: config.dhall")


class TestIdris:
    def test_idr_comment_style(self):
        f = TEST_DIR / "Main.idr"
        f.write_text("module Main\nmain : IO ()")
        assert _get_comment_style(f) == ("--", "")

    def test_idr_header_added(self):
        result = _write_process_read("Main.idr", "module Main\nmain : IO ()")
        assert result.startswith("-- File: Main.idr")

    def test_lidr_comment_style(self):
        f = TEST_DIR / "Proof.lidr"
        f.write_text("> module Proof")
        assert _get_comment_style(f) == ("--", "")


# ---------------------------------------------------------------------------
# Markup
# ---------------------------------------------------------------------------


class TestAsciiDoc:
    def test_comment_style(self):
        f = TEST_DIR / "guide.adoc"
        f.write_text("= My Guide\n== Section")
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("guide.adoc", "= My Guide\n== Section")
        assert result.startswith("// File: guide.adoc")

    def test_asciidoc_extension(self):
        f = TEST_DIR / "manual.asciidoc"
        f.write_text("= Manual")
        assert _get_comment_style(f) == ("//", "")


class TestLaTeX:
    def test_tex_comment_style(self):
        f = TEST_DIR / "paper.tex"
        f.write_text("\\documentclass{article}\n\\begin{document}\n\\end{document}")
        assert _get_comment_style(f) == ("%", "")

    def test_tex_header_added(self):
        result = _write_process_read(
            "paper.tex", "\\documentclass{article}\n\\begin{document}\n\\end{document}"
        )
        assert result.startswith("% File: paper.tex")

    def test_sty_comment_style(self):
        f = TEST_DIR / "mystyle.sty"
        f.write_text("\\ProvidesPackage{mystyle}")
        assert _get_comment_style(f) == ("%", "")

    def test_cls_comment_style(self):
        f = TEST_DIR / "myclass.cls"
        f.write_text("\\ProvidesClass{myclass}")
        assert _get_comment_style(f) == ("%", "")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class TestJSONC:
    def test_comment_style(self):
        f = TEST_DIR / "settings.jsonc"
        f.write_text('{ "key": "value" }')
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("settings.jsonc", '{\n  "key": "value"\n}')
        assert result.startswith("// File: settings.jsonc")


# ---------------------------------------------------------------------------
# Template engines
# ---------------------------------------------------------------------------


class TestNunjucks:
    def test_comment_style(self):
        f = TEST_DIR / "index.njk"
        f.write_text("{% block content %}\n{% endblock %}")
        assert _get_comment_style(f) == ("{#", "#}")

    def test_header_added(self):
        result = _write_process_read("index.njk", "{% block content %}\n{% endblock %}")
        assert result.startswith("{# File: index.njk #}")


# ---------------------------------------------------------------------------
# Idempotency (regression: new extensions must not double-header)
# ---------------------------------------------------------------------------


class TestNewExtensionsIdempotent:
    @pytest.mark.parametrize(
        "filename,content,expected_prefix",
        [
            ("idem.cu", "__global__ void k() {}", "// File:"),
            ("idem.sv", "module m;", "// File:"),
            ("idem.gd", "extends Node", "# File:"),
            ("idem.sol", "contract C {}", "// File:"),
            ("idem.tex", "\\begin{document}", "% File:"),
            ("idem.adoc", "= Doc", "// File:"),
            ("idem.njk", "{% block %}", "{# File:"),
        ],
    )
    def test_idempotent(self, filename: str, content: str, expected_prefix: str):
        f = TEST_DIR / filename
        f.write_text(content)
        process_file(f, TEST_DIR)
        first = f.read_text()
        assert first.startswith(expected_prefix), f"{filename}: missing header"
        process_file(f, TEST_DIR)
        second = f.read_text()
        assert first == second, f"{filename}: second run mutated the file"


# ---------------------------------------------------------------------------
# PowerShell modules / data files (previously unreachable via dead duplicate)
# ---------------------------------------------------------------------------


class TestPowerShellModules:
    def test_psm1_comment_style(self):
        f = TEST_DIR / "MyModule.psm1"
        f.write_text("Export-ModuleMember -Function *")
        assert _get_comment_style(f) == ("#", "")

    def test_psm1_header_added(self):
        result = _write_process_read("MyModule.psm1", "Export-ModuleMember -Function *")
        assert result.startswith("# File: MyModule.psm1")

    def test_psd1_comment_style(self):
        f = TEST_DIR / "MyModule.psd1"
        f.write_text("@{ ModuleVersion = '1.0' }")
        assert _get_comment_style(f) == ("#", "")

    def test_psd1_header_added(self):
        result = _write_process_read("MyModule.psd1", "@{ ModuleVersion = '1.0' }")
        assert result.startswith("# File: MyModule.psd1")


# ---------------------------------------------------------------------------
# AWK
# ---------------------------------------------------------------------------


class TestAWK:
    def test_comment_style(self):
        f = TEST_DIR / "process.awk"
        f.write_text("{ print $1 }")
        assert _get_comment_style(f) == ("#", "")

    def test_header_added(self):
        result = _write_process_read("process.awk", "{ print $1 }")
        assert result.startswith("# File: process.awk")


# ---------------------------------------------------------------------------
# Gradle
# ---------------------------------------------------------------------------


class TestGradle:
    def test_comment_style(self):
        f = TEST_DIR / "build.gradle"
        f.write_text("apply plugin: 'java'")
        assert _get_comment_style(f) == ("//", "")

    def test_header_added(self):
        result = _write_process_read("build.gradle", "apply plugin: 'java'")
        assert result.startswith("// File: build.gradle")
