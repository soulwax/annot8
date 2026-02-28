# Annot8

[![PyPI version](https://img.shields.io/pypi/v/annot8.svg)](https://pypi.org/project/annot8/)
[![PyPI status](https://img.shields.io/pypi/status/annot8.svg)](https://pypi.org/project/annot8/)

**We are openly published on PyPI:** <https://pypi.org/project/annot8/>

```bash
pip install annot8
```

You're ready to go.

A comprehensive Python tool for automating the creation and maintenance of file headers across diverse programming languages and frameworks. Keep your codebase consistently documented with zero manual effort.

---

## Key Features

### 🎯 Intelligent Header Management

- **Idempotent Operations**: Run annot8 multiple times safely—never creates duplicate headers
- **Smart Header Detection**: Automatically detects existing headers in first 20 lines
- **Intelligent Merging**: Preserves valuable metadata (Author, Version, Copyright, Date) when updating
- **Wrong-Style Correction**: Detects and fixes headers with incorrect comment syntax from buggy runs
- **Special Declaration Preservation**: Keeps shebang (`#!/...`), DOCTYPE, and XML declarations (`<?xml...?>`) on line 1

### 🌍 Comprehensive Language Support (70+ Languages)

- **Web Frameworks**: Vue, Svelte, Astro, React/JSX, Handlebars, EJS, Pug, Twig, Jinja2, MDX, Mustache
- **Modern JavaScript**: CommonJS (.cjs), ES Modules (.mjs) with automatic style detection
- **Systems Programming**: C, C++, Rust, Go, Zig, Swift, Kotlin, Objective-C, C#, Assembly
- **Functional Languages**: Haskell, OCaml, Lisp, Clojure, Elixir, Erlang, F#
- **Scripting**: Python, Ruby, Perl, Shell (bash/zsh/fish), PowerShell, Lua, Tcl
- **Data Science**: R, Julia, Python
- **JVM Languages**: Java, Scala, Groovy, Kotlin
- **Qt Framework**: .pro, .ui, .qrc, .ts (intelligent translation vs TypeScript detection)
- **Infrastructure**: Terraform, HCL, Nix, SQL, Dockerfile
- **Legacy/Specialized**: Fortran, COBOL, VHDL, Ada, Pascal, VB.NET

### 🛡️ Smart File Protection

- **Binary Detection**: Automatically skips binary files via content analysis (null byte detection)
- **Build Output**: Ignores `node_modules`, `__pycache__`, `build`, `dist`, `.next`, `.nuxt`, caches
- **Lock Files**: Skips `package-lock.json`, `yarn.lock`, `Cargo.lock`, `poetry.lock`, `go.sum`
- **Shader Protection**: Never touches `.glsl`, `.hlsl`, `.wgsl` (require `#version` directive at top)
- **Markdown & Documentation**: Skips all `.md` files, `LICENSE`, `README`, `CHANGELOG`
- **Gitignore Integration**: Respects `.gitignore` patterns when using `--git` flag (requires `pathspec`)
- **Custom Ignore Lists**: Extend default patterns via configuration files

### 🔧 Git Integration

- **Pre-commit Hooks**: Install with `annot8 --install-hook` for automatic staged file updates
- **Staged Files**: `annot8 --staged` processes only git staging area
- **Git Metadata**: `--use-git-metadata` populates headers with author, email, dates from git history
- **Git-Tracked Mode**: `annot8 --git` processes only tracked files, respecting `.gitignore`
- **Repository Detection**: Automatically finds git root for consistent relative paths

### ⚙️ Flexible Configuration

- **Multiple Formats**: YAML (`.annot8.yaml`), JSON (`.annot8.json`), TOML (`pyproject.toml`)
- **Template Customization**: Full template support with variable substitution
- **Rich Variables**: `{file_path}`, `{author}`, `{version}`, `{date}`, `{file_name}`, `{file_stem}`, etc.
- **Fallback Syntax**: `{variable|default_value}` for optional values
- **Upward Search**: Config discovery searches from current dir to project root
- **Per-Project Settings**: Different configs for different projects automatically detected

### 🔒 Safety & Reliability

- **Automatic Backups**: Saves original content to `.annot8_backup.json` before any modifications
- **One-Command Revert**: `annot8 --revert` restores all files to pre-annot8 state
- **Dry-Run Mode**: `annot8 --dry-run` previews all changes without touching files
- **UTF-8 Handling**: Proper encoding support for international characters
- **Atomic Operations**: Each file processed independently—failures isolated, never cascade
- **Permission Handling**: Graceful handling of read-only files and permission errors

### 💻 Developer Experience

- **Simple CLI**: Intuitive commands with comprehensive options and helpful output
- **Python API**: Full programmatic access for custom workflows and integrations
- **Verbose Logging**: `--verbose` flag provides detailed operation insights for debugging
- **Statistics**: Summary reports show modified, skipped, unchanged file counts
- **Combine Options**: Chain multiple flags like `annot8 --git --staged --dry-run -v`
- **Fast Performance**: Efficiently processes large codebases with thousands of files

---

## Installation

### Install from PyPI (Recommended)

```bash
pip install annot8
```

Optional dependencies for enhanced functionality:

```bash
# For YAML configuration file support
pip install annot8[yaml]

# For .gitignore support (pathspec)
pip install annot8[gitignore]

# For TOML support on Python < 3.11
pip install annot8[toml]

# Install all optional dependencies
pip install annot8[yaml,gitignore,toml]
```

### Install from Source (Development)

```bash
git clone https://github.com/soulwax/annot8.git
cd annot8
pip install -r requirements.txt
pip install -e .
```

---

## Quick Start

```bash
# Install
pip install annot8

# Add headers to all files in current directory
annot8

# Preview changes first (recommended)
annot8 --dry-run

# Process only git-tracked files
annot8 --git

# Install pre-commit hook for automatic updates
annot8 --install-hook

# Made a mistake? Revert all changes
annot8 --revert
```

---

## Usage

### Command-Line Interface

```bash
# Annotate files in the current directory
annot8

# Annotate files in a specific directory
annot8 -d /path/to/project

# Preview changes without modifying files
annot8 --dry-run

# Process only git-tracked files
annot8 --git

# Process only staged files (perfect for pre-commit)
annot8 --staged

# Use git metadata in headers (author, email, date)
annot8 --use-git-metadata

# Install a pre-commit hook
annot8 --install-hook

# Revert the last run
annot8 --revert

# Combine options
annot8 -d /path/to/project --dry-run -v
```

### Python API

```python
from pathlib import Path
from annot8.annotate_headers import process_file, walk_directory, PATTERNS, FilePattern
from annot8.config import load_config

# Process a single file
result = process_file(Path("example.py"), Path.cwd())
print(result["status"])  # "modified", "skipped", or "unchanged"

# Process an entire directory
stats = walk_directory(Path.cwd(), Path.cwd())
print(f"Modified: {stats['modified']}, Skipped: {stats['skipped']}, Unchanged: {stats['unchanged']}")

# Dry-run mode (preview changes)
stats = walk_directory(Path.cwd(), Path.cwd(), dry_run=True)
print(f"Would modify: {stats['modified']} files")

# With custom configuration
config = load_config(Path.cwd())
stats = walk_directory(Path.cwd(), Path.cwd(), config=config)

# Git-only mode (process tracked files only)
stats = walk_directory(Path.cwd(), Path.cwd(), git_only=True)

# Staged files only (perfect for pre-commit hooks)
stats = walk_directory(Path.cwd(), Path.cwd(), staged_only=True)

# With git metadata in headers
stats = walk_directory(Path.cwd(), Path.cwd(), use_git_metadata=True)

# Add custom file type support
PATTERNS.append(FilePattern([".custom"], "//", ""))

# Programmatic backup and revert
from annot8.backup import save_backup, revert_files

file_backups = {"src/file.py": "original content"}
save_backup(Path.cwd(), file_backups)
revert_stats = revert_files(Path.cwd(), dry_run=False)
```

---

## Before & After Examples

These examples show exactly what annot8 does to your files, including edge cases.

### Basic files

**Python file:**

```python
# BEFORE                              # AFTER
print("Hello, World!")                 # File: src/hello.py

                                       print("Hello, World!")
```

**JavaScript file:**

```javascript
// BEFORE                              // AFTER
console.log("Hello, World!");          // File: src/hello.js

                                       console.log("Hello, World!");
```

**CSS file:**

```css
/* BEFORE */                           /* AFTER */
body { margin: 0; }                    /* File: src/styles.css */

                                       body { margin: 0; }
```

### Shebang preservation

The shebang line always stays on line 1. The header goes on line 2.

```bash
# BEFORE                              # AFTER
#!/bin/bash                            #!/bin/bash
echo "hello"                           # File: scripts/deploy.sh

                                       echo "hello"
```

```javascript
// BEFORE                              // AFTER
#!/usr/bin/env node                    #!/usr/bin/env node
console.log("cli tool");              // File: bin/cli.cjs

                                       console.log("cli tool");
```

### CommonJS and ES Modules (.cjs / .mjs)

These use `//` comment style, just like regular `.js` files.

```javascript
// BEFORE: ecosystem.docker.cjs       // AFTER: ecosystem.docker.cjs
/**                                    // File: ecosystem.docker.cjs
 * PM2 config for Docker.
 */                                    /**
module.exports = {                      * PM2 config for Docker.
  apps: [{ name: 'app' }]              */
};                                     module.exports = {
                                         apps: [{ name: 'app' }]
                                       };
```

```javascript
// BEFORE: utils.mjs                   // AFTER: utils.mjs
export function greet(name) {          // File: lib/utils.mjs
  return `Hello, ${name}`;
}                                      export function greet(name) {
                                         return `Hello, ${name}`;
                                       }
```

### XML / HTML declaration preservation

Declarations like `<?xml ...?>` and `<!DOCTYPE ...>` stay on line 1. The header goes on line 2.

```html
<!-- BEFORE -->                        <!-- AFTER -->
<!DOCTYPE html>                        <!DOCTYPE html>
<html lang="en">                       <!-- File: public/index.html -->
<head>                                 <html lang="en">
  <title>Test</title>                  <head>
</head>                                  <title>Test</title>
</html>                                </head>
                                       </html>
```

```xml
<!-- BEFORE -->                        <!-- AFTER -->
<?xml version="1.0" encoding="UTF-8"?><?xml version="1.0" encoding="UTF-8"?>
<root>                                 <!-- File: data/config.xml -->
  <item>Test</item>                    <root>
</root>                                  <item>Test</item>
                                       </root>
```

### Existing header detection (idempotent)

Running annot8 multiple times on the same file does not create duplicate headers.

```python
# BEFORE (already annotated)           # AFTER (unchanged)
# File: src/hello.py                   # File: src/hello.py

print("Hello, World!")                 print("Hello, World!")
```

### Existing header with metadata (merge)

Annot8 preserves useful metadata lines (Author, Version, Copyright, etc.) from existing headers while standardizing the format.

```python
# BEFORE                              # AFTER
# Filename: old_name.py               # File: src/utils.py
# Author: Jane Doe                    # Author: Jane Doe
# Copyright: 2024 ACME                # Copyright: 2024 ACME

def helper():                          def helper():
    pass                                   pass
```

### Wrong comment style correction

If a previous buggy run (or manual edit) used the wrong comment style, annot8 detects and corrects it.

```javascript
// BEFORE: broken.cjs (wrong # style) // AFTER: broken.cjs (fixed)
# File: broken.cjs                    // File: broken.cjs
module.exports = {};
                                       module.exports = {};
```

```javascript
// BEFORE: cli.cjs (wrong # + shebang)// AFTER: cli.cjs (fixed)
#!/usr/bin/env node                    #!/usr/bin/env node
# File: cli.cjs                       // File: cli.cjs
const x = 1;
                                       const x = 1;
```

### Web framework files

```html
<!-- BEFORE: App.vue -->               <!-- AFTER: App.vue -->
<template>                             <!-- File: src/App.vue -->
  <div>Hello</div>                     <template>
</template>                              <div>Hello</div>
<script setup>                         </template>
const msg = "hi";                      <script setup>
</script>                              const msg = "hi";
                                       </script>
```

### Custom header templates

With a `.annot8.yaml` config:

```yaml
header:
  author: "Jane Doe"
  version: "2.0.0"
  include_date: true
  template: |
    File: {file_path}
    Author: {author|Unknown}
    Version: {version|1.0.0}
```

Result:

```python
# File: src/app.py
# Author: Jane Doe
# Version: 2.0.0

def main():
    pass
```

### Git metadata headers

With `annot8 --use-git-metadata`:

```python
# File: src/app.py
# Author: Jane Doe
# Email: jane@example.com
# Date: 2026-02-17

def main():
    pass
```

### Empty files

Empty files get just the header:

```python
# BEFORE: (empty file)                # AFTER:
                                       # File: src/__init__.py
```

---

## Comprehensive File Support

Annot8 automatically recognizes a vast array of file types and applies appropriate comment styles:

### Programming Languages

| Language | Extensions | Comment Style |
|----------|------------|---------------|
| **Python** | `.py` | `#` |
| **JavaScript** | `.js`, `.cjs`, `.mjs` | `//` |
| **TypeScript** | `.ts`, `.tsx` | `//` |
| **React JSX** | `.jsx`, `.tsx` | `//` |
| **C/C++/C#** | `.c`, `.cpp`, `.h`, `.hpp`, `.cs` | `//` |
| **Java** | `.java` | `//` |
| **Go** | `.go` | `//` |
| **Rust** | `.rs` | `//` |
| **Swift** | `.swift` | `//` |
| **Kotlin** | `.kt` | `//` |
| **Scala** | `.scala` | `//` |
| **Zig** | `.zig` | `//` |
| **Dart** | `.dart` | `//` |
| **PHP** | `.php` | `//` |
| **Objective-C** | `.m`, `.mm` | `//` |
| **Groovy** | `.groovy` | `//` |
| **F#** | `.fs`, `.fsx`, `.fsi` | `//` |
| **V** | `.v` | `//` |

### Systems & Scripting

| Category | Extensions | Comment Style |
|----------|------------|---------------|
| **Shell Scripts** | `.sh`, `.bash`, `.zsh`, `.fish` | `#` |
| **PowerShell** | `.ps1`, `.psm1`, `.psd1` | `#` |
| **Batch Files** | `.cmd`, `.bat` | `REM` |
| **Ruby** | `.rb` | `#` |
| **Perl** | `.pl`, `.pm` | `#` |
| **Lua** | `.lua` | `--` |
| **Tcl** | `.tcl` | `#` |
| **VHDL** | `.vhd`, `.vhdl` | `--` |
| **Ada** | `.adb`, `.ads` | `--` |

### Functional & Data Science

| Category | Extensions | Comment Style |
|----------|------------|---------------|
| **Haskell** | `.hs` | `--` |
| **Lisp Family** | `.lisp`, `.cl`, `.el` | `;;` |
| **Clojure** | `.clj`, `.cljs`, `.cljc` | `;;` |
| **Elixir** | `.ex`, `.exs` | `#` |
| **Erlang** | `.erl`, `.hrl` | `%` |
| **OCaml** | `.ml`, `.mli` | `(* *)` |
| **R** | `.r`, `.R` | `#` |
| **Julia** | `.jl` | `#` |
| **Nim** | `.nim` | `#` |
| **Crystal** | `.cr` | `#` |
| **Nix** | `.nix` | `#` |
| **Terraform** | `.tf`, `.tfvars` | `#` |
| **HCL** | `.hcl` | `#` |
| **Pascal/Delphi** | `.pas`, `.pp` | `//` |
| **Assembly** | `.asm`, `.s` | `;` |
| **VB.NET** | `.vb` | `'` |
| **Fortran** | `.f`, `.f90`, `.f95`, `.f03`, `.f08` | `!` |
| **COBOL** | `.cob`, `.cbl` | `*` |

### Web Technologies

| Category | Extensions | Comment Style | Special Handling |
|----------|------------|---------------|------------------|
| **HTML/XML** | `.html`, `.htm`, `.xml` | `<!-- -->` | Preserves DOCTYPE |
| **CSS/Styling** | `.css`, `.scss`, `.sass`, `.less` | `/* */` | - |
| **Vue.js** | `.vue` | `<!-- -->` | Template preservation |
| **Svelte** | `.svelte` | `<!-- -->` | Component structure |
| **Astro** | `.astro` | `<!-- -->` | Frontmatter preservation |
| **MDX** | `.mdx` | `<!-- -->` | Markdown + JSX |
| **Handlebars** | `.hbs`, `.handlebars` | `<!-- -->` | Template syntax |
| **EJS** | `.ejs` | `<!-- -->` | Embedded JavaScript |
| **Pug/Jade** | `.pug`, `.jade` | `//` | Indentation-based |
| **Mustache** | `.mustache`, `.mst` | `<!-- -->` | Logic-less templates |
| **Twig** | `.twig` | `{# #}` | PHP templating |
| **Jinja2** | `.jinja`, `.jinja2` | `{# #}` | Python templating |

### Configuration & Data

| Category | Extensions | Comment Style |
|----------|------------|---------------|
| **YAML** | `.yaml`, `.yml` | `#` |
| **TOML** | `.toml` | `#` |
| **INI/Config** | `.ini`, `.conf`, `.cfg` | `#` |
| **Properties** | `.properties` | `#` |
| **JSON5** | `.json5` | `//` |
| **SQL** | `.sql` | `--` |
| **reStructuredText** | `.rst` | `..` |

### Qt Framework

| File Type | Extensions | Comment Style | Special Features |
|-----------|------------|---------------|------------------|
| **Project Files** | `.pro`, `.pri` | `#` | - |
| **UI Files** | `.ui` | `<!-- -->` | XML declaration preservation |
| **Resource Files** | `.qrc` | `<!-- -->` | - |
| **Translation Files** | `.ts` | `<!-- -->` | Auto-detects vs TypeScript |

### Special Configuration Files

Annot8 intelligently handles configuration files with appropriate comment styles:

- **Git**: `.gitignore`, `.gitattributes`, `.gitmodules`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Build Systems**: `Makefile`, `CMakeLists.txt`
- **Package Managers**: `Pipfile`, `pyproject.toml`, `setup.py`
- **CI/CD**: `.travis.yml`, `.gitlab-ci.yml`, `.drone.yml`
- **JavaScript Ecosystem**: `package.json`, `tsconfig.json`, `webpack.config.js`
- And many more...

---

## Protected Files & Directories

### Completely Ignored Files

Annot8 automatically skips files that shouldn't be modified:

**Configuration Files:**
`.prettierrc`, `.eslintrc`, `.babelrc`, `.stylelintrc`, `.browserslistrc`, `.nvmrc`, `.npmrc`, `.yarnrc`, `.editorconfig`, `.env.example`, `.env.local`, `.env.development`, `.env.production`

**Auto-Generated / Lock Files:**
`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Pipfile.lock`, `poetry.lock`, `Cargo.lock`, `go.sum`, `composer.lock`

**Documentation & Legal:**
`LICENSE`, `COPYING`, `NOTICE`, `AUTHORS`, `CONTRIBUTORS`, `CHANGELOG`, `HISTORY`, all `.md` files (Markdown), all standard `.json` files (only JSON5 gets headers)

**Shader Files (Graphics):**
`.vert`, `.frag`, `.geom`, `.comp`, `.tesc`, `.tese`, `.glsl`, `.hlsl`, `.wgsl`, `.shader` - these require `#version` directive as the first line; adding headers would break shader compilation.

**Binary Files (Auto-detected):**

- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.ico`, `.bmp`, `.tiff`, `.webp`, `.avif`
- **Audio**: `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`, `.m4a`
- **Video**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`, `.wmv`
- **Archives**: `.zip`, `.tar`, `.gz`, `.bz2`, `.xz`, `.7z`, `.rar`
- **Executables**: `.exe`, `.dll`, `.so`, `.dylib`, `.bin`, `.a`, `.lib`, `.obj`, `.o`
- **Compiled**: `.pyc`, `.pyo`, `.pyd`, `.class`, `.jar`, `.war`, `.whl`, `.qm`
- **Documents**: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- **Databases**: `.db`, `.sqlite`, `.sqlite3`, `.mdb`
- **Fonts**: `.ttf`, `.otf`, `.woff`, `.woff2`, `.eot`

### Ignored Directories

Annot8 automatically skips these common build and dependency directories:

**Python:** `__pycache__`, `venv`, `.venv`, `build`, `dist`, `.eggs`, `.tox`

**JavaScript/Node:** `node_modules`, `.next`, `.nuxt`, `.output`, `bower_components`, `.yarn`, `.pnpm-store`, `.parcel-cache`, `.cache`

**Version Control:** `.git`, `.hg`, `.svn`, `.bzr`

**Build Outputs:** `build`, `dist`, `out`, `target`, `bin`, `obj`, `coverage`

**IDE/Editor:** `.idea`, `.vscode` (settings), `.vs`

**Other:** `vendor` (PHP/Composer), `icon`, `OtherPic`, `donate`

You can extend this list via the `files.ignored_directories` configuration option.

---

## Template System

Annot8 provides a powerful template system for customizing file headers. Templates support variable substitution, fallback values, multi-line headers, and automatic comment formatting for any file type.

### Template Basics

Templates are defined in configuration files using the `header.template` field. They support:

- **Variable Substitution**: `{variable_name}` - replaced with actual values
- **Fallback Values**: `{variable_name|default}` - uses default if variable is undefined
- **Multi-line Headers**: Use `\n` in JSON/TOML or literal newlines in YAML
- **Automatic Formatting**: Template lines automatically get the correct comment style for each file type

### Available Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{file_path}` | Relative path from project root | `src/utils/helper.py` |
| `{file_name}` | Filename with extension | `helper.py` |
| `{file_stem}` | Filename without extension | `helper` |
| `{file_suffix}` | File extension | `.py` |
| `{file_dir}` | Directory path relative to root | `src/utils` |
| `{author}` | Author name (from config or git) | `Jane Doe` |
| `{author_email}` | Author email (from config or git) | `jane@example.com` |
| `{version}` | Version string (from config) | `1.0.0` |
| `{date}` | Date (requires `include_date: true`) | `2026-02-28` |

**Note**: File variables (`file_path`, `file_name`, etc.) are always available. Metadata variables (`author`, `version`, etc.) require configuration or `--use-git-metadata` flag.

### Template Examples

#### Simple Single-Line Template

```yaml
# .annot8.yaml
header:
  template: "File: {file_path}"
```

Result for `src/app.py`:

```python
# File: src/app.py
```

#### Multi-Line Template with Metadata

```yaml
# .annot8.yaml
header:
  author: "Jane Doe"
  version: "2.0.0"
  include_date: true
  date_format: "%Y-%m-%d"
  template: |
    File: {file_path}
    Author: {author}
    Version: {version}
    Date: {date}
```

Result for `src/app.py`:

```python
# File: src/app.py
# Author: Jane Doe
# Version: 2.0.0
# Date: 2026-02-28
```

#### Template with Fallback Values

Fallback values are used when a variable is not defined:

```yaml
# .annot8.yaml
header:
  template: |
    File: {file_path}
    Author: {author|Unknown Author}
    Version: {version|1.0.0}
    License: {license|MIT}
```

Result (without author/version/license configured):

```python
# File: src/app.py
# Author: Unknown Author
# Version: 1.0.0
# License: MIT
```

#### Template with Spacing

Control spacing with empty lines:

```yaml
# .annot8.yaml
header:
  author: "Development Team"
  template: |
    File: {file_path}

    Author: {author}
    Description: Core application logic
```

Result:

```python
# File: src/app.py
#
# Author: Development Team
# Description: Core application logic
```

#### Using All File Variables

```yaml
# .annot8.yaml
header:
  template: |
    Path: {file_path}
    Name: {file_name}
    Stem: {file_stem}
    Ext: {file_suffix}
    Dir: {file_dir}
```

Result for `src/utils/helper.py`:

```python
# Path: src/utils/helper.py
# Name: helper.py
# Stem: helper
# Ext: .py
# Dir: src/utils
```

### Templates with Different Comment Styles

Templates automatically adapt to each file type's comment syntax:

**Python file** (`helper.py`):

```python
# File: helper.py
# Author: Jane Doe
```

**JavaScript file** (`helper.js`):

```javascript
// File: helper.js
// Author: Jane Doe
```

**CSS file** (`styles.css`):

```css
/* File: styles.css */
/* Author: Jane Doe */
```

**HTML file** (`index.html`):

```html
<!-- File: index.html -->
<!-- Author: Jane Doe -->
```

### Configuration Format Examples

#### YAML Format (Recommended)

```yaml
# .annot8.yaml
header:
  author: "Your Name"
  author_email: "your.email@example.com"
  version: "1.0.0"
  include_date: true
  date_format: "%Y-%m-%d %H:%M"
  template: |
    File: {file_path}
    Author: {author}
    Email: {author_email}
    Version: {version}
    Modified: {date}

files:
  ignored_files:
    - "local_config.py"
  ignored_directories:
    - "scratch"
```

#### JSON Format

```json
{
  "header": {
    "author": "Your Name",
    "author_email": "your.email@example.com",
    "version": "1.0.0",
    "include_date": true,
    "date_format": "%Y-%m-%d",
    "template": "File: {file_path}\nAuthor: {author}\nVersion: {version}\nDate: {date}"
  },
  "files": {
    "ignored_files": ["local_config.py"],
    "ignored_directories": ["scratch"]
  }
}
```

#### TOML Format (pyproject.toml)

```toml
[tool.annot8.header]
author = "Your Name"
author_email = "your.email@example.com"
version = "1.0.0"
include_date = true
date_format = "%Y-%m-%d"
template = """File: {file_path}
Author: {author}
Version: {version}
Date: {date}"""

[tool.annot8.files]
ignored_files = ["local_config.py"]
ignored_directories = ["scratch"]
```

### Using Git Metadata in Templates

Combine templates with git metadata extraction:

```bash
# Populate template variables from git history
annot8 --use-git-metadata
```

With this configuration:

```yaml
# .annot8.yaml
header:
  include_date: true
  template: |
    File: {file_path}
    Author: {author|Unknown}
    Email: {author_email|unknown@example.com}
    Date: {date}
```

Git metadata will automatically populate `{author}`, `{author_email}`, and `{date}` from the file's git history.

### Template Best Practices

1. **Use Fallback Values**: Always provide fallbacks for optional metadata with `{variable|default}`
2. **Keep Templates Consistent**: Use the same template across your project for uniformity
3. **Date Formats**: Choose appropriate `date_format` for your region and needs
4. **Minimal Templates**: Don't over-document—let your code speak for itself
5. **Version Control**: Commit your `.annot8.yaml` so all team members use the same template

### Advanced Template Scenarios

#### Different Templates for Different Projects

Place `.annot8.yaml` in each project root:

```
/project-a/.annot8.yaml  # Template for Project A
/project-b/.annot8.yaml  # Different template for Project B
```

Annot8 automatically discovers and uses the nearest configuration file.

#### Corporate/Open Source Templates

**Corporate Projects**:

```yaml
header:
  author: "ACME Corp Development Team"
  template: |
    File: {file_path}
    Copyright: (c) 2026 ACME Corporation
    Author: {author}
    Confidential: Internal Use Only
```

**Open Source Projects**:

```yaml
header:
  template: |
    File: {file_path}
    License: MIT
    Repository: https://github.com/org/repo

    Copyright (c) 2026 Contributors
    SPDX-License-Identifier: MIT
```

---

## Configuration

### Configuration Files

Place one of these files in your project root:

- `.annot8.yaml` or `.annot8.yml` (YAML format)
- `.annot8.json` (JSON format)
- `pyproject.toml` (with `[tool.annot8]` section)

#### YAML example

```yaml
# .annot8.yaml
header:
  author: "Your Name"
  author_email: "your.email@example.com"
  version: "1.0.0"
  include_date: true
  date_format: "%Y-%m-%d"
  template: |
    File: {file_path}
    Author: {author|Unknown}
    Version: {version|1.0.0}
    Date: {date}

files:
  ignored_files:
    - "custom_config.json"
    - "local_settings.py"
  ignored_directories:
    - "local_data"
    - "temp_files"
```

#### TOML example (pyproject.toml)

```toml
[tool.annot8.header]
author = "Your Name"
author_email = "your.email@example.com"
version = "1.0.0"
include_date = true

[tool.annot8.files]
ignored_files = ["custom_config.json"]
ignored_directories = ["local_data"]
```

#### Template Variables

| Variable | Description |
|----------|-------------|
| `{file_path}` | Relative path from project root |
| `{file_name}` | Filename only |
| `{file_stem}` | Filename without extension |
| `{file_suffix}` | File extension |
| `{file_dir}` | Directory path |
| `{author}` | From config or git |
| `{author_email}` | From config or git |
| `{version}` | From config |
| `{date}` | Current or git date |

Use `{variable|default}` syntax for fallback values, e.g. `{author|Unknown}`.

### Programmatic Configuration

```python
from annot8 import PATTERNS, FilePattern, IGNORED_DIRS, IGNORED_FILES

# Add custom file types
PATTERNS.append(FilePattern([".custom"], "//", ""))

# Extend ignore lists
IGNORED_DIRS.add("my_build_dir")
IGNORED_FILES.add("my-config.json")
```

---

## Contributing

Contributions are welcome! Please open a Pull Request for any improvements.

### Development Setup

```bash
git clone https://github.com/soulwax/annot8.git
cd annot8
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=annot8 tests/

# Run linting
pylint src/annot8 tests

# Format code
black .

# All-in-one
make check
```

### Test Coverage

The project maintains 200+ tests covering:

- Core file processing across all supported languages
- Shebang, DOCTYPE, and XML declaration preservation
- Web framework template handling (Vue, Svelte, Astro, etc.)
- Qt framework integration (.pro, .ui, .ts detection)
- CommonJS/ESM (.cjs/.mjs) annotation and edge cases
- Header detection, merging, deduplication, and wrong-style correction
- Git integration, configuration loading, backup/revert
- Dry-run mode, UTF-8 handling, binary detection

---

## License

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.
