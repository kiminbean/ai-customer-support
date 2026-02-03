"""
Job persistence module - Persist in-memory job state to file
Restores job state on app restart
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import config

logger = logging.getLogger(__name__)

# -- Configuration ----------------------------------------------------------

JOB_STORAGE_PATH = config.DATA_DIR / "jobs.json"
JOB_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Storage for all job types
_job_stores: Dict[str, Dict[str, Any]] = {
    "crawler": {},
    "datahub": {},
    "voice": {},
}

# Lock file path (duplicate check prevention)
_LOCK_FILE = config.DATA_DIR / "jobs.lock"


# -- Storage Functions -------------------------------------------------------

def _with_lock(func):
    """Use file lock for safe concurrent writes"""
    import fcntl

    def wrapper(*args, **kwargs):
        try:
            # Create lock file (blocking)
            lock_fd = os.open(_LOCK_FILE, os.O_CREAT | os.O_WRONLY, 0o644)
            fcntl.flock(lock_fd, fcntl.LOCK_EX)

            try:
                result = func(*args, **kwargs)
            finally:
                # Release lock
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)

            return result
        except (ImportError, AttributeError):
            # Unix fcntl not available, execute directly (Windows etc.)
            return func(*args, **kwargs)

    return wrapper


@_with_lock
def _save_jobs() -> bool:
    """Save all job stores to file"""
    try:
        with open(JOB_STORAGE_PATH, "w", encoding="utf-8") as f:
            json.dump(_job_stores, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error("Failed to save jobs: %s", e, exc_info=True)
        return False


def _load_jobs() -> None:
    """Load job stores from file"""
    global _job_stores
    try:
        if JOB_STORAGE_PATH.exists():
            with open(JOB_STORAGE_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge with existing data
                for key, value in loaded.items():
                    if key in _job_stores:
                        _job_stores[key].update(value)
            logger.info("Restored %d job items", sum(len(v) for v in loaded.values()))
    except Exception as e:
        logger.warning("Failed to load jobs: %s", e, exc_info=True)


# -- Initialization ---------------------------------------------------------

def init_job_persistence() -> None:
    """Initialize job persistence (call on app startup)"""
    _load_jobs()


# -- Crawler Jobs ---------------------------------------------------------

def save_crawl_job(job_id: str, job_data: Dict[str, Any]) -> bool:
    """Save crawler job"""
    _job_stores["crawler"][job_id] = job_data
    return _save_jobs()


def get_crawl_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get crawler job"""
    return _job_stores["crawler"].get(job_id)


def delete_crawl_job(job_id: str) -> bool:
    """Delete crawler job"""
    _job_stores["crawler"].pop(job_id, None)
    return _save_jobs()


def list_crawl_jobs() -> list[Dict[str, Any]]:
    """List all crawler jobs"""
    return list(_job_stores["crawler"].values())


# -- Datahub Jobs ---------------------------------------------------------

def save_datahub_job(job_id: str, job_data: Dict[str, Any]) -> bool:
    """Save datahub job"""
    _job_stores["datahub"][job_id] = job_data
    return _save_jobs()


def get_datahub_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get datahub job"""
    return _job_stores["datahub"].get(job_id)


def delete_datahub_job(job_id: str) -> bool:
    """Delete datahub job"""
    _job_stores["datahub"].pop(job_id, None)
    return _save_jobs()


def list_datahub_jobs() -> list[Dict[str, Any]]:
    """List all datahub jobs"""
    return list(_job_stores["datahub"].values())


# -- Voice Jobs -----------------------------------------------------------

def save_voice_job(job_id: str, job_data: Dict[str, Any]) -> bool:
    """Save voice job"""
    _job_stores["voice"][job_id] = job_data
    return _save_jobs()


def get_voice_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get voice job"""
    return _job_stores["voice"].get(job_id)


def delete_voice_job(job_id: str) -> bool:
    """Delete voice job"""
    _job_stores["voice"].pop(job_id, None)
    return _save_jobs()


def list_voice_jobs() -> list[Dict[str, Any]]:
    """List all voice jobs"""
    return list(_job_stores["voice"].values())


# -- Utility Functions -------------------------------------------------

def get_all_jobs() -> Dict[str, Any]:
    """Get all job stores"""
    return {
        "crawler": list(_job_stores["crawler"].values()),
        "datahub": list(_job_stores["datahub"].values()),
        "voice": list(_job_stores["voice"].values()),
    }


def clear_old_jobs(max_age_hours: int = 24) -> int:
    """
    Clean up old jobs
    max_age_hours: Maximum retention time in hours
    Returns: Number of deleted jobs
    """
    import time
    from datetime import datetime

    cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
    deleted = 0

    for store_name, store in _job_stores.items():
        to_delete = []
        for job_id, job_data in store.items():
            created_at = job_data.get("created_at")
            if created_at:
                try:
                    # Parse ISO format timestamp
                    created_ts = datetime.fromisoformat(created_at).timestamp()
                    if created_ts < cutoff_time:
                        to_delete.append(job_id)
                        deleted += 1
                except (ValueError, TypeError):
                    continue

        for job_id in to_delete:
            store.pop(job_id)

    if deleted > 0:
        _save_jobs()
        logger.info("Cleaned up %d old jobs", deleted)

    return deleted
