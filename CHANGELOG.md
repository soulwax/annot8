# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.2] - 2026-02-28

### Changed
- **Release documentation update**: Documented recent maintenance and compatibility work for this patch release.
- **Version bump**: Prepared and published a new PyPI patch release for `annot8`.

---

## [0.12.1] - 2026-02-28

### Added
- **Legacy package compatibility alias**: Added `src/pyannotate` as a compatibility shim that proxies to `annot8`.
  - Enables legacy lint/test commands such as `pylint src/pyannotate tests`
  - Preserves behavior through lazy proxy functions (`process_file`, `walk_directory`, `main`)

- **Pytest startup hook**: Added `tests/conftest.py` to centralize test marker registration and ensure compatibility imports for coverage workflows.

### Changed
- **Development dependencies**: Added `PyYAML` to `requirements-dev.txt` so YAML template tests run by default in the dev environment.
- **Template test maintenance**: Refactored duplicated setup logic in template tests into shared utilities (`tests/test_utils.py`), reducing duplication and keeping lint score at `10.00/10`.

### Fixed
- **Pylint fatal target mismatch**: Removed `F0001` failure when linting `src/pyannotate`.
- **Template test skip behavior in standard dev setup**: YAML-specific tests now run instead of being skipped once dev dependencies are installed.

---

## [0.12.0] - 2026-02-28

### Added

#### Documentation
- **Comprehensive Template System Documentation**: Added extensive "Template System" section to README.md with 15+ practical examples
  - Complete variable reference table with all 9 template variables
  - Examples for YAML, JSON, and TOML configuration formats
  - Comment style adaptation examples for Python, JavaScript, CSS, HTML, SQL
  - Git metadata integration guide
  - Best practices and advanced scenarios (corporate, open source templates)
  - Different templates for different projects guide

- **Enhanced README**: Completely restructured Key Features section with categorized capabilities
  - 🎯 Intelligent Header Management
  - 🌍 Comprehensive Language Support (70+ Languages)
  - 🛡️ Smart File Protection
  - 🔧 Git Integration
  - ⚙️ Flexible Configuration
  - 🔒 Safety & Reliability
  - 💻 Developer Experience
  - Added Quick Start section for new users
  - Enhanced Python API examples with all available options
  - Expanded Protected Files & Directories section with detailed categorization

- **Development Guide**: Created CLAUDE.md with comprehensive development instructions
  - Core architecture overview
  - Module organization details
  - Key design patterns (header detection, special declaration preservation, idempotent operations)
  - Development commands (testing, linting, building)
  - Testing patterns and organization
  - Configuration system explanation
  - CI/CD and code style guidelines

#### Testing
- **Comprehensive Template Test Suite**: Added 38 new tests in test_templates_comprehensive.py
  - TestTemplateVariables (9 tests): All template variables
  - TestTemplateFallbackValues (5 tests): Fallback syntax with various scenarios
  - TestMultiLineTemplates (3 tests): Multi-line template rendering
  - TestTemplateCommentStyles (7 tests): Adaptation to different comment styles
  - TestTemplateWithSpecialCases (4 tests): Shebang, XML, DOCTYPE preservation
  - TestTemplateConfigFormats (3 tests): YAML, JSON, TOML configurations
  - TestTemplateEdgeCases (4 tests): Edge cases and error handling
  - TestTemplateIntegration (3 tests): Integration with other features

- **Test Coverage**: Template system now has 100% test coverage
  - 36 tests passing, 2 skipped (YAML tests when PyYAML not installed)
  - Total project tests: 236+ tests

### Fixed
- **Code Quality**: Resolved all pylint issues (10.00/10)
  - Fixed implicit string concatenation
  - Moved imports to module level
  - Fixed long lines (>100 characters)

### Changed
- Reorganized README.md structure for better user experience
- Enhanced Python API documentation with comprehensive examples
- Improved categorization of ignored files and directories

---

## [0.11.1] - Previous Release

### Features
- Enhanced CommonJS and ES Module support
- Improved header detection and merging
- Git integration with pre-commit hooks

---

[0.12.2]: https://github.com/soulwax/annot8/compare/v0.12.1...v0.12.2
[0.12.1]: https://github.com/soulwax/annot8/compare/v0.12.0...v0.12.1
[0.12.0]: https://github.com/soulwax/annot8/compare/v0.11.1...v0.12.0
[0.11.1]: https://github.com/soulwax/annot8/releases/tag/v0.11.1
