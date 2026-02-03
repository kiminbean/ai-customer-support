"""
Database backup module - SQLite automated backup
Daily backups, retention period management
"""

from __future__ import annotations

import gzip
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)

# -- Configuration ----------------------------------------------------------

BACKUP_DIR = config.DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

BACKUP_RETENTION_DAYS = int(
    os.getenv("BACKUP_RETENTION_DAYS", "30")
)  # Retention period in days
COMPRESS_BACKUPS = os.getenv("COMPRESS_BACKUPS", "true").lower() == "true"


# -- Backup Functions ---------------------------------------------------

def create_backup() -> bool:
    """
    Create database backup.
    Returns True on success, False on failure.
    """
    try:
        if not config.DATABASE_PATH.exists():
            logger.warning("Database file does not exist: %s", config.DATABASE_PATH)
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"app_db_{timestamp}.db"
        backup_path = BACKUP_DIR / backup_name

        # Create backup file
        shutil.copy2(config.DATABASE_PATH, backup_path)

        # Compression option
        if COMPRESS_BACKUPS:
            compressed_path = BACKUP_DIR / f"{backup_name}.gz"
            with open(backup_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Delete original
            backup_path.unlink()
            backup_path = compressed_path

        logger.info("Backup created: %s", backup_path.name)

        # Clean up old backups
        cleanup_old_backups()

        return True

    except Exception as e:
        logger.error("Backup creation failed: %s", e, exc_info=True)
        return False


def cleanup_old_backups() -> int:
    """
    Delete backup files older than retention period.
    Returns number of deleted files.
    """
    try:
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (BACKUP_RETENTION_DAYS * 86400)

        for backup_file in BACKUP_DIR.glob("app_db_*.db*"):
            # Check for old files by modification time
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                deleted_count += 1
                logger.info("Deleted old backup: %s", backup_file.name)

        if deleted_count > 0:
            logger.info("Deleted %d old backup files", deleted_count)

        return deleted_count

    except Exception as e:
        logger.error("Backup cleanup failed: %s", e, exc_info=True)
        return 0


def restore_backup(backup_name: str) -> bool:
    """
    Restore database from specified backup.
    Returns True on success, False on failure.
    """
    try:
        backup_path = BACKUP_DIR / backup_name

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_name}")

        # Check if compressed file
        if backup_path.suffix == ".gz":
            # Backup current database
            if config.DATABASE_PATH.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_before = BACKUP_DIR / f"app_db_before_restore_{timestamp}.db"
                shutil.copy2(config.DATABASE_PATH, backup_before)
                logger.info("Backed up current database: %s", backup_before.name)

            # Uncompress
            with gzip.open(backup_path, "rb") as f_in:
                with open(config.DATABASE_PATH, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            # Backup current database
            if config.DATABASE_PATH.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_before = BACKUP_DIR / f"app_db_before_restore_{timestamp}.db"
                shutil.copy2(config.DATABASE_PATH, backup_before)
                logger.info("Backed up current database: %s", backup_before.name)

            shutil.copy2(backup_path, config.DATABASE_PATH)

        logger.info("Backup restored: %s", backup_name)
        return True

    except Exception as e:
        logger.error("Backup restoration failed: %s", e, exc_info=True)
        return False


def list_backups() -> list[dict]:
    """
    List available backups.
    Each backup includes filename, size, modification time.
    """
    backups = []
    for backup_file in BACKUP_DIR.glob("app_db_*.db*"):
        stat = backup_file.stat()
        # Check if compressed
        is_compressed = backup_file.suffix == ".gz"

        # Extract timestamp
        try:
            if is_compressed:
                timestamp_str = backup_file.stem.replace("app_db_", "").replace(".db", "")
            else:
                timestamp_str = backup_file.stem.replace("app_db_", "")
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_time = "Unknown"
            timestamp = datetime.fromtimestamp(stat.st_mtime)

        backups.append({
            "filename": backup_file.name,
            "size_bytes": stat.st_size,
            "size_human": _format_size(stat.st_size),
            "created_at": formatted_time,
            "timestamp": timestamp.isoformat(),
            "is_compressed": is_compressed,
        })

    # Sort by newest
    backups.sort(key=lambda b: b["timestamp"], reverse=True)

    return backups


def _format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# -- Backup Scheduler -------------------------------------------------

def start_backup_scheduler():
    """
    Start backup scheduler (run as daemon thread for demo purposes).
    In production, use systemd/cron instead.
    """
    import threading
    import time

    def _backup_loop():
        while True:
            try:
                create_backup()
            except Exception as e:
                logger.error("Scheduled backup failed: %s", e, exc_info=True)

            # Wait 24 hours
            time.sleep(86400)

    thread = threading.Thread(target=_backup_loop, daemon=True, name="BackupScheduler")
    thread.start()
    logger.info("Backup scheduler started (24 hourly schedule)")


# -- Initialization -------------------------------------------------------

def init_backup() -> None:
    """Initialize backup directory and create first backup if needed"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Create first backup if no backups exist
    if not list(BACKUP_DIR.glob("app_db_*.db*")):
        logger.info("Creating first backup...")
        create_backup()
