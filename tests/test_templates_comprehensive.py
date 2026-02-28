# File: tests/test_templates_comprehensive.py

"""Comprehensive tests for template system covering every edge case and feature."""

import json
import re
import tempfile
from pathlib import Path

import pytest

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from annot8.annotate_headers import process_file, walk_directory
from annot8.config import load_config


class TestTemplateVariables:
    """Test all template variables work correctly."""

    def test_file_path_variable(self):
        """Test {file_path} variable renders correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sub_dir = temp_path / "src" / "components"
            sub_dir.mkdir(parents=True)

            config_file = temp_path / ".annot8.json"
            config_file.write_text('{"header": {"template": "Path: {file_path}"}}')

            test_file = sub_dir / "Button.tsx"
            test_file.write_text("export const Button = () => {}")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// Path: src/components/Button.tsx" in content

    def test_file_name_variable(self):
        """Test {file_name} variable renders correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_file.write_text('{"header": {"template": "Name: {file_name}"}}')

            test_file = temp_path / "helper.py"
            test_file.write_text("def help(): pass")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# Name: helper.py" in content

    def test_file_stem_variable(self):
        """Test {file_stem} variable renders correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_file.write_text('{"header": {"template": "Stem: {file_stem}"}}')

            test_file = temp_path / "MyComponent.tsx"
            test_file.write_text("export default MyComponent")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// Stem: MyComponent" in content

    def test_file_suffix_variable(self):
        """Test {file_suffix} variable renders correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_file.write_text('{"header": {"template": "Ext: {file_suffix}"}}')

            test_file = temp_path / "app.py"
            test_file.write_text("print('test')")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# Ext: .py" in content

    def test_file_dir_variable(self):
        """Test {file_dir} variable renders correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sub_dir = temp_path / "lib" / "utils"
            sub_dir.mkdir(parents=True)

            config_file = temp_path / ".annot8.json"
            config_file.write_text('{"header": {"template": "Dir: {file_dir}"}}')

            test_file = sub_dir / "parse.js"
            test_file.write_text("module.exports = {}")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// Dir: lib/utils" in content

    def test_author_variable(self):
        """Test {author} variable from config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"author": "Jane Doe", "template": "By: {author}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "main.py"
            test_file.write_text("def main(): pass")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# By: Jane Doe" in content

    def test_author_email_variable(self):
        """Test {author_email} variable from config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {
                "header": {"author_email": "jane@example.com", "template": "Email: {author_email}"}
            }
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.js"
            test_file.write_text("console.log('test')")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// Email: jane@example.com" in content

    def test_version_variable(self):
        """Test {version} variable from config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"version": "2.1.0", "template": "Ver: {version}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "lib.rb"
            test_file.write_text("class Lib; end")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# Ver: 2.1.0" in content

    def test_date_variable_with_include_date(self):
        """Test {date} variable when include_date is True."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {
                "header": {
                    "include_date": True,
                    "date_format": "%Y-%m-%d",
                    "template": "Date: {date}",
                }
            }
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "util.go"
            test_file.write_text("package util")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// Date: " in content
            # Should have date in YYYY-MM-DD format
            assert re.search(r"// Date: \d{4}-\d{2}-\d{2}", content)


class TestTemplateFallbackValues:
    """Test fallback values in templates."""

    def test_simple_fallback(self):
        """Test {variable|default} syntax with missing variable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "Author: {author|Anonymous}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.py"
            test_file.write_text("print('test')")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# Author: Anonymous" in content

    def test_fallback_with_present_variable(self):
        """Test fallback is not used when variable is present."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"author": "Bob", "template": "Author: {author|Anonymous}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.py"
            test_file.write_text("print('test')")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# Author: Bob" in content
            assert "Anonymous" not in content

    def test_multiple_fallbacks_in_template(self):
        """Test multiple fallback values in same template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {
                "header": {
                    "template": (
                        "Author: {author|Unknown}\n"
                        "Version: {version|1.0.0}\n"
                        "License: {license|MIT}"
                    )
                }
            }
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "lib.js"
            test_file.write_text("export default {}")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// Author: Unknown" in content
            assert "// Version: 1.0.0" in content
            assert "// License: MIT" in content

    def test_fallback_with_spaces(self):
        """Test fallback values containing spaces."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "Author: {author|Development Team}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "main.rs"
            test_file.write_text("fn main() {}")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// Author: Development Team" in content

    def test_fallback_with_special_characters(self):
        """Test fallback values with special characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "Copyright: {copyright|(c) 2026 ACME Corp.}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "util.swift"
            test_file.write_text("import Foundation")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// Copyright: (c) 2026 ACME Corp." in content


class TestMultiLineTemplates:
    """Test multi-line template rendering."""

    def test_two_line_template(self):
        """Test simple two-line template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nAuthor: {author|Unknown}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.py"
            test_file.write_text("print('test')")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            lines = content.splitlines()
            assert "# File: app.py" in lines[0]
            assert "# Author: Unknown" in lines[1]

    def test_many_line_template(self):
        """Test template with many lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {
                "header": {
                    "author": "Team",
                    "version": "1.0",
                    "template": (
                        "File: {file_path}\n"
                        "Author: {author}\n"
                        "Version: {version}\n"
                        "License: MIT\n"
                        "Copyright: 2026"
                    ),
                }
            }
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "main.kt"
            test_file.write_text("fun main() {}")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// File: main.kt" in content
            assert "// Author: Team" in content
            assert "// Version: 1.0" in content
            assert "// License: MIT" in content
            assert "// Copyright: 2026" in content

    def test_template_with_blank_lines(self):
        """Test template with intentional blank lines for spacing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\n\nDescription: Test file"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.scala"
            test_file.write_text("object App")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            lines = content.splitlines()
            # Should have blank lines preserving spacing in template
            assert "// File: app.scala" in content
            # Blank line in template creates empty line in output
            assert lines[1] == "//" or lines[1] == ""
            assert "// Description: Test file" in content


class TestTemplateCommentStyles:
    """Test templates adapt to different comment styles."""

    def test_python_hash_comments(self):
        """Test template with Python # comments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nAuthor: Test"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "script.py"
            test_file.write_text("x = 1")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# File: script.py" in content
            assert "# Author: Test" in content

    def test_javascript_slash_comments(self):
        """Test template with JavaScript // comments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nAuthor: Test"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.js"
            test_file.write_text("const x = 1")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// File: app.js" in content
            assert "// Author: Test" in content

    def test_css_block_comments(self):
        """Test template with CSS /* */ comments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nAuthor: Test"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "style.css"
            test_file.write_text("body { margin: 0; }")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "/* File: style.css */" in content
            assert "/* Author: Test */" in content

    def test_html_xml_comments(self):
        """Test template with HTML <!-- --> comments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "page.html"
            test_file.write_text("<html><body>Test</body></html>")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "<!-- File: page.html -->" in content

    def test_sql_comments(self):
        """Test template with SQL -- comments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nQuery: Test"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "query.sql"
            test_file.write_text("SELECT * FROM users;")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "-- File: query.sql" in content
            assert "-- Query: Test" in content

    def test_lua_comments(self):
        """Test template with Lua -- comments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "config.lua"
            test_file.write_text("local x = 1")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "-- File: config.lua" in content

    def test_shell_script_comments(self):
        """Test template with shell # comments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nPurpose: Build"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "build.sh"
            test_file.write_text("echo 'build'")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# File: build.sh" in content
            assert "# Purpose: Build" in content


class TestTemplateWithSpecialCases:
    """Test templates with special file scenarios."""

    def test_template_with_shebang(self):
        """Test template preserves shebang on line 1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nPurpose: Script"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "deploy.sh"
            test_file.write_text("#!/bin/bash\necho 'deploy'")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            lines = content.splitlines()
            assert lines[0] == "#!/bin/bash"
            assert "# File: deploy.sh" in lines[1]
            assert "# Purpose: Script" in lines[2]

    def test_template_with_xml_declaration(self):
        """Test template preserves XML declaration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "data.xml"
            test_file.write_text('<?xml version="1.0"?>\n<root></root>')

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            lines = content.splitlines()
            assert '<?xml version="1.0"?>' in lines[0]
            assert "<!-- File: data.xml -->" in lines[1]

    def test_template_with_doctype(self):
        """Test template preserves DOCTYPE."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "index.html"
            test_file.write_text("<!DOCTYPE html>\n<html></html>")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            lines = content.splitlines()
            assert "<!DOCTYPE html>" in lines[0]
            assert "<!-- File: index.html -->" in lines[1]

    def test_template_with_empty_file(self):
        """Test template on empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nEmpty: True"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "__init__.py"
            test_file.write_text("")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# File: __init__.py" in content
            assert "# Empty: True" in content


class TestTemplateConfigFormats:
    """Test templates in different config formats."""

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_yaml_template(self):
        """Test template in YAML config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.yaml"
            config_data = {"header": {"template": "File: {file_path}\nFormat: YAML"}}
            config_file.write_text(yaml.dump(config_data))

            test_file = temp_path / "app.py"
            test_file.write_text("x = 1")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# File: app.py" in content
            assert "# Format: YAML" in content

    def test_json_template(self):
        """Test template in JSON config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nFormat: JSON"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.js"
            test_file.write_text("const x = 1")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// File: app.js" in content
            assert "// Format: JSON" in content

    @pytest.mark.skipif(not YAML_AVAILABLE, reason="PyYAML not installed")
    def test_multiline_yaml_template(self):
        """Test multi-line template using YAML literal block scalar."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.yaml"
            # Use literal block scalar for multi-line
            config_text = """header:
  author: "Test Author"
  template: |
    File: {file_path}
    Author: {author}
    Description: Multi-line YAML template
"""
            config_file.write_text(config_text)

            test_file = temp_path / "lib.go"
            test_file.write_text("package lib")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// File: lib.go" in content
            assert "// Author: Test Author" in content
            assert "// Description: Multi-line YAML template" in content


class TestTemplateEdgeCases:
    """Test edge cases and error handling."""

    def test_template_with_no_variables(self):
        """Test template without any variables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "This is a static header\nNo variables here"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "static.py"
            test_file.write_text("x = 1")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# This is a static header" in content
            assert "# No variables here" in content

    def test_template_with_undefined_variable_no_fallback(self):
        """Test template with undefined variable and no fallback."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "Custom: {custom_var}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.py"
            test_file.write_text("x = 1")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            # Should render with empty value
            assert "# Custom:" in content or "# Custom: " in content

    def test_template_idempotent(self):
        """Test template application is idempotent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {
                "header": {"author": "Alice", "template": "File: {file_path}\nBy: {author}"}
            }
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "test.rb"
            test_file.write_text("class Test; end")

            config = load_config(temp_path)

            # First run
            process_file(test_file, temp_path, config=config)
            first_content = test_file.read_text()

            # Second run
            process_file(test_file, temp_path, config=config)
            second_content = test_file.read_text()

            # Should be identical
            assert first_content == second_content
            assert first_content.count("# File: test.rb") == 1
            assert first_content.count("# By: Alice") == 1

    def test_template_with_very_long_lines(self):
        """Test template with very long content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            long_text = "This is a very long description that goes on and on " * 10
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": f"File: {{file_path}}\nDesc: {long_text}"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "app.dart"
            test_file.write_text("void main() {}")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "// File: app.dart" in content
            assert long_text in content


class TestTemplateIntegration:
    """Integration tests for templates with other features."""

    def test_template_with_directory_walk(self):
        """Test template applies to all files in directory walk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "Project File: {file_path}"}}
            config_file.write_text(json.dumps(config_data))

            # Create multiple files
            (temp_path / "app.py").write_text("x = 1")
            (temp_path / "lib.js").write_text("const x = 1")
            sub = temp_path / "utils"
            sub.mkdir()
            (sub / "helper.go").write_text("package utils")

            config = load_config(temp_path)
            stats = walk_directory(temp_path, temp_path, config=config)

            # Check all files processed
            assert stats["modified"] == 3

            # Check template applied correctly
            assert "# Project File: app.py" in (temp_path / "app.py").read_text()
            assert "// Project File: lib.js" in (temp_path / "lib.js").read_text()
            assert "// Project File: utils/helper.go" in (sub / "helper.go").read_text()

    def test_template_replaces_existing_header(self):
        """Test template replaces old non-template header."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {
                "header": {
                    "author": "New Author",
                    "template": "File: {file_path}\nAuthor: {author}",
                }
            }
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "old.py"
            test_file.write_text("# File: old.py\n\nprint('test')")

            config = load_config(temp_path)
            process_file(test_file, temp_path, config=config)

            content = test_file.read_text()
            assert "# File: old.py" in content
            assert "# Author: New Author" in content
            assert "print('test')" in content

    def test_template_with_dry_run(self):
        """Test template respects dry-run mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / ".annot8.json"
            config_data = {"header": {"template": "File: {file_path}\nDry: Run"}}
            config_file.write_text(json.dumps(config_data))

            test_file = temp_path / "test.zig"
            original = 'const std = @import("std");'
            test_file.write_text(original)

            config = load_config(temp_path)
            result = process_file(test_file, temp_path, config=config, dry_run=True)

            # File should not be modified
            assert test_file.read_text() == original
            # But result should show it would be modified
            assert result["status"] == "modified"
