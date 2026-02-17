# Annot8

A comprehensive Python tool for automating the creation and maintenance of file headers across diverse programming languages and frameworks.

---

## Key Features

- Automatically updates and creates file headers with intelligent detection and merging
- Supports 70+ programming languages and file formats
- Advanced web framework support (Vue, Svelte, Astro, React, Handlebars, EJS, Pug, Twig, Jinja2)
- Qt framework integration (.pro, .ui, .ts translation files)
- Preserves special declarations (shebang, DOCTYPE, XML declarations)
- Smart header detection and merging - preserves existing metadata
- Intelligent file filtering with comprehensive ignore patterns
- Configuration-aware processing with special handling for config files
- CLI interface and Python API for versatile usage
- Git integration with pre-commit hooks, staged-file processing, and metadata extraction
- Backup and revert functionality to undo changes
- Dry-run mode to preview changes before applying

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
from annot8.annotate_headers import process_file, walk_directory

# Process a single file
result = process_file(Path("example.py"), Path.cwd())
print(result["status"])  # "modified", "skipped", or "unchanged"

# Process an entire directory
stats = walk_directory(Path.cwd(), Path.cwd())

# Dry-run mode
stats = walk_directory(Path.cwd(), Path.cwd(), dry_run=True)
print(f"Would modify: {stats['modified']} files")
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
`.prettierrc`, `.eslintrc`, `.babelrc`, `.stylelintrc`, `.browserslistrc`, `.nvmrc`, `.npmrc`, `.yarnrc`, `.env.example`, `.env.local`, `.env.development`, `.env.production`

**Auto-Generated / Lock Files:**
`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Pipfile.lock`, `poetry.lock`, `Cargo.lock`, `go.sum`

**Documentation & Legal:**
`LICENSE`, `COPYING`, `NOTICE`, `AUTHORS`, `CONTRIBUTORS`, `README.md`, `CHANGELOG.md`, all `.md` files, all standard `.json` files (only JSON5 gets headers)

**Shader Files:**
`.vert`, `.frag`, `.geom`, `.comp`, `.tesc`, `.tese`, `.glsl`, `.hlsl`, `.wgsl`, `.shader` - these require `#version` as the first line; headers would break compilation.

**Binary Files:**
Images, audio/video, archives, executables, compiled files, and more.

### Ignored Directories

`__pycache__`, `node_modules`, `build`, `dist`, `.cache`, `.git`, `.hg`, `.svn`, `venv`, `.venv`, `.next`, `.nuxt`, `.output`, `.parcel-cache`, `.yarn`, `.pnpm-store`, `vendor`, `bower_components`, `coverage`, and more.

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
