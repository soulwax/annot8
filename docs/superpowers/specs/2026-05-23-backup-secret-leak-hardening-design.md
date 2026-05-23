# Backup Secret-Leak Hardening — Design

**Date:** 2026-05-23
**Target release:** 0.12.5 (security patch, ship to PyPI immediately after merge)
**Status:** Approved

## Problem

`annot8` writes `.annot8_backup.json` to the project root before modifying files. The backup contains the **full original contents** of every modified file, keyed by relative path. Two failure modes leak secrets:

1. `.annot8_backup.json` is **not** in any default `.gitignore`. A user who runs `annot8` and then `git add .` commits the backup; if any modified file contained secrets, those secrets are now in git history.
2. Annot8 **processes `.env` files** today (`.env` is listed in `SPECIAL_FILE_COMMENTS` with `("#", "")`). The act of adding a header to `.env` causes its full contents — including API keys, DB passwords, OAuth secrets — to be copied into `.annot8_backup.json`.

Combined, these mean a routine `annot8 -d .` followed by `git commit -am "headers"` can publish production credentials to a public repository.

## Goals

- A user who runs `annot8` against a project containing secrets cannot accidentally publish those secrets via the backup mechanism, even with no extra configuration and no awareness of the risk.
- Defense in depth: multiple independent layers must each fail before a secret can leak.
- Zero impact on the existing revert workflow for non-sensitive files.
- No new runtime dependencies.

## Non-goals

- Encrypting the backup file. (Adds key-management complexity; not requested.)
- Moving backups outside the project root. (Breaks `--revert` discoverability.)
- Content-based scanning of files for secret patterns (regex for `AWS_SECRET_ACCESS_KEY=`, etc.). Name-based filtering is sufficient, predictable, and avoids false positives.
- Retroactively cleaning up backups created by older versions. (Documented in release notes; user action.)

## Design

Four independent layers. Each closes a different hole.

### Layer 1 — Skip sensitive files entirely

New constants in `src/annot8/annotate_headers.py`:

```python
# Exact filenames that must never be read or modified.
SENSITIVE_FILENAMES: Set[str] = {
    ".env",
    ".netrc", ".pgpass", ".htpasswd",
    "secrets.json", "secrets.yaml", "secrets.yml",
    "credentials.json", "credentials.yaml", "credentials.yml",
    "auth.json",
    ".npmrc", ".pypirc",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "known_hosts",
}

# Glob patterns matched against file name (not full path).
SENSITIVE_GLOBS: Tuple[str, ...] = (
    ".env.*",          # .env.production, .env.local, .env.staging, etc.
    "*.pem", "*.key", "*.crt", "*.cer", "*.csr",
    "*.p12", "*.pfx", "*.jks", "*.keystore",
    "*.kdbx",
    "*_rsa", "*_dsa", "*_ecdsa", "*_ed25519",
)
```

Helper function:

```python
def _is_sensitive_file(file_path: Path) -> bool:
    name = file_path.name
    if name in SENSITIVE_FILENAMES:
        return True
    return any(fnmatch.fnmatchcase(name, pat) for pat in SENSITIVE_GLOBS)
```

Wire into `_should_skip_path` **before** the comment-style lookup and **before** any file read:

```python
def _should_skip_path(file_path, config=None):
    if not file_path.is_file():
        ...
    if _is_sensitive_file(file_path):
        logging.debug("Skipping sensitive file: %s", file_path)
        return True
    # ... existing checks
```

**Remove `.env` from `SPECIAL_FILE_COMMENTS`** — it has no business being there. (The `.env.example` / `.env.local` / `.env.development` / `.env.production` entries in `IGNORED_FILES` become redundant once `SENSITIVE_GLOBS` covers `.env.*`, but leave them in place — duplicate protection is fine and removing them would be a behavioral subtlety to litigate.)

`process_file` returns `{"status": "skipped", "reason": "sensitive_file"}` for these files. Because the skip happens before `_read_text_best_effort`, the contents never enter memory, so they cannot enter the backup.

### Layer 2 — Auto-protect the backup file

Modify `src/annot8/backup.py::save_backup` to call a new helper `_ensure_gitignored(project_root, backup_path)` after a successful write.

```python
def _ensure_gitignored(project_root: Path, backup_path: Path) -> None:
    """Append .annot8_backup.json to .gitignore if not already present.

    No-op outside git repositories. Creates .gitignore if missing.
    """
    # Reuse existing helper; walks up from project_root to find .git
    git_root = get_git_root(project_root)
    if git_root is None:
        return  # not a git repo; nothing to gitignore

    gitignore = git_root / ".gitignore"
    entry = backup_path.name  # ".annot8_backup.json"

    try:
        if gitignore.exists():
            existing = gitignore.read_text(encoding="utf-8")
            stripped = {line.strip() for line in existing.splitlines()}
            if entry in stripped or f"/{entry}" in stripped:
                return
            # splitlines() drops the trailing newline, so check raw text
            needs_leading_newline = bool(existing) and not existing.endswith("\n")
            with gitignore.open("a", encoding="utf-8") as fp:
                if needs_leading_newline:
                    fp.write("\n")
                fp.write("# Added by annot8 to prevent committing local backups\n")
                fp.write(f"{entry}\n")
        else:
            gitignore.write_text(
                "# Created by annot8 to prevent committing local backups\n"
                f"{entry}\n",
                encoding="utf-8",
            )
    except OSError as e:
        logging.warning("Could not update .gitignore to protect %s: %s", entry, e)
```

Import `get_git_root` from `.git_integration` to avoid duplication.

### Layer 3 — Restrictive file permissions

In `save_backup`, after the write:

```python
try:
    os.chmod(backup_path, 0o600)
except OSError:
    pass  # Windows or filesystem without POSIX perms — chmod is best-effort
```

On Windows, `os.chmod` only toggles the read-only bit; this is acceptable. The intent is to make the file unreadable to other local users on multi-user POSIX systems.

### Layer 4 — Loud warning on first backup write

In `save_backup`, gate a one-time warning on whether the backup file already existed:

```python
backup_existed = backup_path.exists()
backup_path.write_text(...)
if not backup_existed:
    logging.warning(
        "annot8 wrote a backup containing original file contents to %s. "
        "This file has been added to .gitignore and chmod'd to 0600. "
        "Do NOT commit it.",
        backup_path,
    )
```

`logging.warning` (not `debug`) so it surfaces with default CLI verbosity.

## File-by-file changes

| File | Change |
|------|--------|
| `src/annot8/annotate_headers.py` | Add `SENSITIVE_FILENAMES`, `SENSITIVE_GLOBS`, `_is_sensitive_file`. Wire into `_should_skip_path`. Remove `.env` entry from `SPECIAL_FILE_COMMENTS`. Add `import fnmatch`. |
| `src/annot8/backup.py` | Add `_ensure_gitignored`, `_find_git_root` (or import). Modify `save_backup` for chmod, warning, and gitignore. Add `import os`. |
| `tests/test_backup_security.py` | New file. See test plan below. |
| `pyproject.toml` | Version bump 0.12.4 → 0.12.5. |
| `CHANGELOG.md` | New `[0.12.5] - 2026-05-23` section under `### Security`. |
| `README.md` | One paragraph in a new "Security" section noting sensitive-file skip list and backup protection. |

## Test plan

`tests/test_backup_security.py` — new file, isolated tmp_path fixtures.

1. **`.env` is skipped end-to-end** — create tmp project with `.env` containing `SECRET=abc123`; run `process_file`; assert `.env` content unchanged AND `SECRET=abc123` does not appear anywhere in the backup file (read backup as raw bytes, grep).
2. **`.env.production`, `.env.local` skipped** — parametrized over `SENSITIVE_GLOBS` patterns.
3. **`secrets.yaml`, `id_rsa`, `cert.pem`, `keystore.jks` skipped** — parametrized.
4. **Non-sensitive `.py` file with the word "secret" in it is NOT skipped** — guards against false positives.
5. **`.gitignore` auto-added on first backup** — fresh git repo, no `.gitignore`; run annot8; assert `.gitignore` exists at git root and contains `.annot8_backup.json`.
6. **`.gitignore` appended, not duplicated** — existing `.gitignore` with unrelated entries; run annot8 twice; assert `.annot8_backup.json` appears exactly once.
7. **No-op outside git repo** — tmp dir, no `.git`; run annot8; assert no `.gitignore` created and no error raised.
8. **Backup file permissions are 0o600** — POSIX only (skip on `sys.platform == "win32"`); assert `stat.S_IMODE(os.stat(backup_path).st_mode) == 0o600`.
9. **Warning emitted on first backup, not on second** — use `caplog`; assert WARNING level message matching "Do NOT commit" appears exactly once across two runs.
10. **Revert still works** — full round trip: process a `.py` file, revert, confirm original content restored. Regression guard.

All existing tests must continue to pass — particularly anything in `test_annotate_headers.py` or `test_revert.py` that touches `.env` (search and update if any).

## Release process

This is a security patch and ships immediately after merge to `main`:

1. All green: `black --check . && pylint src/annot8 tests && pytest --cov=annot8 tests/`
2. Commit with message: `fix(security): prevent secret leakage via backup file`
3. Tag: `git tag v0.12.5 && git push --tags`
4. GitHub Actions `publish.yml` (per `CLAUDE.md`) publishes to PyPI on release tag.
5. Verify on PyPI: `pip index versions annot8` shows 0.12.5.
6. (Optional follow-up, not in this patch) Add a `SECURITY.md` and CVE-style advisory if the project warrants one.

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Breaks workflows where users deliberately want headers in `.env` files. | Vanishingly small population; security trumps convenience. Documented in CHANGELOG. Users can override via custom `config.files.ignored_files` exclusion in a future enhancement if requested. |
| Modifying user's `.gitignore` is intrusive. | Append with a clear comment line so the user sees why. No-op if entry already present. Skipped entirely outside git repos. |
| `fnmatch` false positives for unusual filenames (e.g., a legitimate file ending in `.key`). | Acceptable: these patterns target widely-known secret extensions. Affected users will see a "skipped" log and can rename or annotate manually. |
| Existing backups (from 0.12.4 and earlier) already contain secrets. | Out of scope to clean up. Release notes will explicitly tell users to inspect and delete pre-0.12.5 backups. |
