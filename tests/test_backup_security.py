# File: tests/test_backup_security.py

"""Security tests for backup behavior.

Verifies that sensitive files are never processed (and thus never backed up),
that .annot8_backup.json is auto-protected via .gitignore + 0600 perms,
and that the user is warned on first backup creation.

Regression coverage for the 0.12.5 secret-leak hardening.
"""

import logging
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from annot8.annotate_headers import process_file
from annot8.backup import BACKUP_FILENAME, revert_files, save_backup

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _init_git_repo(path: Path) -> None:
    """Initialize a bare-bones git repo so get_git_root succeeds."""
    subprocess.run(["git", "init", "-q"], cwd=path, check=True, capture_output=True, timeout=10)


def _backup_contains(backup_path: Path, needle: str) -> bool:
    """Return True if needle appears anywhere in the raw backup file bytes."""
    if not backup_path.exists():
        return False
    return needle in backup_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Layer 1: Sensitive files are never read or modified
# ---------------------------------------------------------------------------


def test_dotenv_file_is_skipped_and_content_never_backed_up(tmp_path: Path) -> None:
    """A .env file with secrets must not be processed and must not appear in backup."""
    env_file = tmp_path / ".env"
    secret_value = "SECRET_API_KEY=sk_live_abc123_DO_NOT_LEAK"
    env_file.write_text(secret_value, encoding="utf-8")

    backup_content: dict = {}
    result = process_file(env_file, tmp_path, backup_content=backup_content)

    assert result["status"] == "skipped"
    assert env_file.read_text(encoding="utf-8") == secret_value, ".env must not be modified"
    assert not backup_content, "Backup dict must not contain .env contents"

    # If a backup were written, it must not contain the secret either
    if backup_content:
        save_backup(tmp_path, backup_content)
        assert not _backup_contains(
            tmp_path / BACKUP_FILENAME, "sk_live_abc123"
        ), "Backup must not contain .env secrets"


@pytest.mark.parametrize(
    "filename",
    [
        ".env.production",
        ".env.local",
        ".env.staging",
        ".env.development.local",
        "secrets.json",
        "secrets.yaml",
        "secrets.yml",
        "credentials.json",
        "credentials.yaml",
        "auth.json",
        ".netrc",
        ".pgpass",
        ".htpasswd",
        "id_rsa",
        "id_ed25519",
        "id_ecdsa",
        "known_hosts",
        "server.pem",
        "private.key",
        "cert.crt",
        "request.csr",
        "store.p12",
        "vault.pfx",
        "android.jks",
        "passwords.kdbx",
        "my_key_rsa",
    ],
)
def test_sensitive_filenames_are_skipped(tmp_path: Path, filename: str) -> None:
    """Each sensitive filename pattern must short-circuit before any read."""
    secret = f"SECRET_FOR_{filename}=value_xyz_789"
    target = tmp_path / filename
    target.write_text(secret, encoding="utf-8")

    backup_content: dict = {}
    result = process_file(target, tmp_path, backup_content=backup_content)

    assert result["status"] == "skipped", f"{filename} must be skipped"
    assert target.read_text(encoding="utf-8") == secret, f"{filename} must not be modified"
    assert not backup_content, f"{filename} content must not enter backup dict"


def test_non_sensitive_python_file_with_word_secret_is_not_skipped(tmp_path: Path) -> None:
    """Filename matching is what triggers skip — the word 'secret' in code is fine."""
    target = tmp_path / "config_module.py"
    target.write_text("SECRET = 'this is just code'\n", encoding="utf-8")

    backup_content: dict = {}
    result = process_file(target, tmp_path, backup_content=backup_content)

    assert result["status"] in {"modified", "unchanged"}
    # File should have been modified to include a header (it had no header before)
    assert result["status"] == "modified"
    assert target.read_text(encoding="utf-8").startswith("# File: config_module.py")


# ---------------------------------------------------------------------------
# Layer 2: Auto-gitignore the backup file
# ---------------------------------------------------------------------------


def test_save_backup_adds_entry_to_existing_gitignore(tmp_path: Path) -> None:
    """When .gitignore exists in git root, append BACKUP_FILENAME to it."""
    _init_git_repo(tmp_path)
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("node_modules/\n*.log\n", encoding="utf-8")

    save_backup(tmp_path, {"foo.py": "print('x')"})

    contents = gitignore.read_text(encoding="utf-8")
    assert BACKUP_FILENAME in contents
    # Existing entries preserved
    assert "node_modules/" in contents
    assert "*.log" in contents


def test_save_backup_creates_gitignore_if_missing(tmp_path: Path) -> None:
    """If git repo has no .gitignore, create one with just our entry."""
    _init_git_repo(tmp_path)
    gitignore = tmp_path / ".gitignore"
    assert not gitignore.exists()

    save_backup(tmp_path, {"foo.py": "print('x')"})

    assert gitignore.exists()
    assert BACKUP_FILENAME in gitignore.read_text(encoding="utf-8")


def test_save_backup_does_not_duplicate_gitignore_entry(tmp_path: Path) -> None:
    """Running save_backup twice must not add the entry twice."""
    _init_git_repo(tmp_path)

    save_backup(tmp_path, {"foo.py": "a"})
    save_backup(tmp_path, {"foo.py": "b"})

    contents = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert contents.count(BACKUP_FILENAME) == 1


def test_save_backup_respects_existing_entry(tmp_path: Path) -> None:
    """If user already gitignored the backup file, don't add a duplicate."""
    _init_git_repo(tmp_path)
    (tmp_path / ".gitignore").write_text(f"{BACKUP_FILENAME}\n", encoding="utf-8")

    save_backup(tmp_path, {"foo.py": "a"})

    contents = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert contents.count(BACKUP_FILENAME) == 1


def test_save_backup_is_noop_for_gitignore_outside_git_repo(tmp_path: Path) -> None:
    """Outside a git repo, do not create a .gitignore."""
    # No git init — tmp_path is just a plain directory
    save_backup(tmp_path, {"foo.py": "print('x')"})

    assert not (tmp_path / ".gitignore").exists()
    # Backup itself still gets written
    assert (tmp_path / BACKUP_FILENAME).exists()


def test_save_backup_handles_gitignore_without_trailing_newline(tmp_path: Path) -> None:
    """An existing .gitignore without trailing newline should still get a clean append."""
    _init_git_repo(tmp_path)
    (tmp_path / ".gitignore").write_text("node_modules/", encoding="utf-8")  # no \n

    save_backup(tmp_path, {"foo.py": "print('x')"})

    contents = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    # The new entry must be on its own line, not glued to the previous one
    assert "node_modules/\n" in contents or "node_modules/" + os.linesep in contents
    assert BACKUP_FILENAME in contents
    # Make sure they're on separate lines
    lines = [line.strip() for line in contents.splitlines() if line.strip()]
    assert "node_modules/" in lines
    assert BACKUP_FILENAME in lines


# ---------------------------------------------------------------------------
# Layer 3: Restrictive file permissions
# ---------------------------------------------------------------------------


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file permissions only")
def test_backup_file_has_restrictive_permissions(tmp_path: Path) -> None:
    """On POSIX, the backup file must be chmod 0600."""
    save_backup(tmp_path, {"foo.py": "print('x')"})
    backup_path = tmp_path / BACKUP_FILENAME

    assert backup_path.exists()
    mode = stat.S_IMODE(os.stat(backup_path).st_mode)
    assert mode == 0o600, f"Expected 0o600, got {oct(mode)}"


# ---------------------------------------------------------------------------
# Layer 4: Warning emitted on first backup creation
# ---------------------------------------------------------------------------


def test_warning_emitted_on_first_backup_creation(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """First backup write must log a WARNING about the security implications."""
    caplog.set_level(logging.WARNING)

    save_backup(tmp_path, {"foo.py": "print('x')"})

    warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert any(
        "Do NOT commit" in r.getMessage() for r in warnings
    ), f"Expected a 'Do NOT commit' WARNING, got: {[r.getMessage() for r in warnings]}"


def test_warning_not_repeated_on_subsequent_backup(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Warning should only fire on first creation, not on overwrite."""
    caplog.set_level(logging.WARNING)

    save_backup(tmp_path, {"foo.py": "a"})
    # Clear and run again
    caplog.clear()
    save_backup(tmp_path, {"foo.py": "b"})

    warnings = [
        r
        for r in caplog.records
        if r.levelno >= logging.WARNING and "Do NOT commit" in r.getMessage()
    ]
    assert warnings == [], "Warning must not repeat on subsequent backup writes"


# ---------------------------------------------------------------------------
# Layer 5: Revert still works end-to-end (regression guard)
# ---------------------------------------------------------------------------


def test_revert_workflow_still_works_for_non_sensitive_files(tmp_path: Path) -> None:
    """Round trip: process .py file, revert, content restored. Guards against regressions."""
    src = tmp_path / "module.py"
    original = "print('original')\n"
    src.write_text(original, encoding="utf-8")

    backup_content: dict = {}
    process_file(src, tmp_path, backup_content=backup_content)
    assert "module.py" in backup_content
    save_backup(tmp_path, backup_content)

    # File now has a header
    assert src.read_text(encoding="utf-8") != original

    # Revert
    stats = revert_files(tmp_path)
    assert stats["reverted"] == 1
    assert src.read_text(encoding="utf-8") == original
