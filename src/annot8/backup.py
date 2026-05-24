# File: src/annot8/backup.py

"""Backup and revert functionality for Annot8."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .git_integration import get_git_root

BACKUP_FILENAME = ".annot8_backup.json"

_GITIGNORE_COMMENT = "# Added by annot8 to prevent committing local backups"


def _get_backup_path(project_root: Path) -> Path:
    """Get the path to the backup file."""
    return project_root / BACKUP_FILENAME


def _ensure_gitignored(project_root: Path) -> None:
    """Append BACKUP_FILENAME to .gitignore if inside a git repo and not already present.

    No-op outside git repositories. Creates .gitignore at the git root if missing.
    """
    git_root = get_git_root(project_root)
    if git_root is None:
        return

    gitignore = git_root / ".gitignore"
    try:
        if gitignore.exists():
            existing = gitignore.read_text(encoding="utf-8")
            stripped = {line.strip() for line in existing.splitlines()}
            if BACKUP_FILENAME in stripped or f"/{BACKUP_FILENAME}" in stripped:
                return
            # splitlines() drops the trailing newline, so check raw text
            needs_leading_newline = bool(existing) and not existing.endswith("\n")
            with gitignore.open("a", encoding="utf-8") as fp:
                if needs_leading_newline:
                    fp.write("\n")
                fp.write(f"{_GITIGNORE_COMMENT}\n")
                fp.write(f"{BACKUP_FILENAME}\n")
        else:
            gitignore.write_text(
                f"{_GITIGNORE_COMMENT}\n{BACKUP_FILENAME}\n",
                encoding="utf-8",
            )
    except OSError as e:
        logging.warning("Could not update .gitignore to protect %s: %s", BACKUP_FILENAME, e)


def _restrict_backup_permissions(backup_path: Path) -> None:
    """Best-effort chmod 0600 on the backup file (POSIX only; no-op on Windows)."""
    try:
        os.chmod(backup_path, 0o600)
    except OSError:
        # Windows or filesystem without POSIX perms; safe to ignore
        pass


def save_backup(project_root: Path, file_backups: Dict[str, str]) -> None:
    """
    Save file backups to the backup file.

    Also auto-adds the backup file to .gitignore (when in a git repo), sets
    restrictive POSIX permissions, and emits a one-time warning on first
    creation so the user is aware that the file contains original file
    contents and must not be committed.

    Args:
        project_root: Root directory of the project
        file_backups: Dictionary mapping relative file paths to their original content
    """
    if not file_backups:
        logging.debug("No files to backup")
        return

    backup_path = _get_backup_path(project_root)
    is_first_backup = not backup_path.exists()
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "files": file_backups,
    }

    try:
        backup_path.write_text(json.dumps(backup_data, indent=2), encoding="utf-8")
        logging.debug("Saved backup for %d files to %s", len(file_backups), backup_path)
    except (OSError, ValueError, TypeError) as e:
        logging.warning("Failed to save backup: %s", e)
        return

    _restrict_backup_permissions(backup_path)
    _ensure_gitignored(project_root)

    if is_first_backup:
        logging.warning(
            "annot8 wrote a backup containing original file contents to %s. "
            "Added to .gitignore and chmod'd to 0600 where supported. "
            "Do NOT commit this file.",
            backup_path,
        )


def load_backup(project_root: Path) -> Optional[Dict[str, str]]:
    """
    Load the most recent backup from the backup file.

    Args:
        project_root: Root directory of the project

    Returns:
        Dictionary mapping relative file paths to their original content,
        or None if no backup exists
    """
    backup_path = _get_backup_path(project_root)
    if not backup_path.exists():
        logging.debug("No backup file found at %s", backup_path)
        return None

    try:
        backup_data = json.loads(backup_path.read_text(encoding="utf-8"))
        files = backup_data.get("files", {})
        timestamp = backup_data.get("timestamp", "unknown")
        logging.debug(
            "Loaded backup from %s (timestamp: %s, %d files)", backup_path, timestamp, len(files)
        )
        return files
    except (OSError, json.JSONDecodeError) as e:
        logging.warning("Failed to load backup: %s", e)
        return None


def revert_files(project_root: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Revert files from the most recent backup.

    Args:
        project_root: Root directory of the project
        dry_run: If True, preview changes without modifying files

    Returns:
        Dictionary with statistics: {"reverted": int, "missing": int, "errors": int}
    """
    file_backups = load_backup(project_root)
    if not file_backups:
        logging.warning("No backup found to revert from")
        return {"reverted": 0, "missing": 0, "errors": 0}

    stats = {"reverted": 0, "missing": 0, "errors": 0}

    for relative_path, original_content in file_backups.items():
        file_path = project_root / relative_path

        if not file_path.exists():
            logging.warning("File no longer exists, cannot revert: %s", file_path)
            stats["missing"] += 1
            continue

        try:
            if dry_run:
                logging.info("[DRY-RUN] Would revert: %s", file_path)
            else:
                file_path.write_text(original_content, encoding="utf-8")
                logging.info("Reverted: %s", file_path)
            stats["reverted"] += 1
        except (OSError, UnicodeEncodeError) as e:
            logging.error("Failed to revert %s: %s", file_path, e)
            stats["errors"] += 1

    if not dry_run and stats["reverted"] > 0:
        # Optionally remove backup file after successful revert
        # For now, we'll keep it in case user wants to revert again
        logging.debug("Revert complete. Backup file kept at %s", _get_backup_path(project_root))

    return stats


def clear_backup(project_root: Path) -> bool:
    """
    Clear the backup file.

    Args:
        project_root: Root directory of the project

    Returns:
        True if backup was cleared, False if it didn't exist
    """
    backup_path = _get_backup_path(project_root)
    if backup_path.exists():
        try:
            backup_path.unlink()
            logging.debug("Cleared backup file: %s", backup_path)
            return True
        except OSError as e:
            logging.warning("Failed to clear backup file: %s", e)
            return False
    return False
