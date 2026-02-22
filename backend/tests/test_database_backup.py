"""
Tests for database_backup module
Target: Increase coverage from 18% to 80%+
"""

from __future__ import annotations

import gzip
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import database_backup
import config


class TestCreateBackup:
    """create_backup 함수 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path, monkeypatch):
        """테스트 환경 설정"""
        # 임시 디렉토리 사용
        self.tmp_dir = tmp_path
        self.backup_dir = self.tmp_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # config 모킹
        self.original_db_path = config.DATABASE_PATH
        self.test_db_path = self.tmp_dir / "test.db"

        monkeypatch.setattr(config, "DATABASE_PATH", self.test_db_path)
        monkeypatch.setattr(database_backup, "BACKUP_DIR", self.backup_dir)

    def test_create_backup_no_database(self):
        """데이터베이스 파일이 없을 때 False 반환"""
        result = database_backup.create_backup()
        assert result is False

    def test_create_backup_success(self, monkeypatch):
        """정상적인 백업 생성"""
        # 데이터베이스 파일 생성
        config.DATABASE_PATH.write_text("test data")

        # 압축 비활성화
        monkeypatch.setenv("COMPRESS_BACKUPS", "false")
        monkeypatch.setattr(database_backup, "COMPRESS_BACKUPS", False)

        result = database_backup.create_backup()

        assert result is True
        # 백업 파일 존재 확인
        backups = list(self.backup_dir.glob("app_db_*.db"))
        assert len(backups) >= 1

    def test_create_backup_with_compression(self, monkeypatch):
        """압축 백업 생성"""
        # 데이터베이스 파일 생성
        config.DATABASE_PATH.write_text("test data for compression")

        # 압축 활성화
        monkeypatch.setenv("COMPRESS_BACKUPS", "true")
        monkeypatch.setattr(database_backup, "COMPRESS_BACKUPS", True)

        result = database_backup.create_backup()

        assert result is True
        # 압축된 백업 파일 존재 확인
        backups = list(self.backup_dir.glob("app_db_*.db.gz"))
        assert len(backups) >= 1


class TestCleanupOldBackups:
    """cleanup_old_backups 함수 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path, monkeypatch):
        """테스트 환경 설정"""
        self.tmp_dir = tmp_path
        self.backup_dir = self.tmp_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(database_backup, "BACKUP_DIR", self.backup_dir)
        monkeypatch.setattr(database_backup, "BACKUP_RETENTION_DAYS", 1)

    def test_cleanup_no_files(self):
        """파일이 없을 때 0 반환"""
        result = database_backup.cleanup_old_backups()
        assert result == 0

    def test_cleanup_keeps_recent_files(self):
        """최근 파일은 유지"""
        # 최근 파일 생성
        recent_file = self.backup_dir / "app_db_20260101_120000.db"
        recent_file.write_text("recent backup")

        result = database_backup.cleanup_old_backups()

        assert result == 0
        assert recent_file.exists()

    def test_cleanup_deletes_old_files(self, monkeypatch):
        """오래된 파일 삭제"""
        # 오래된 파일 생성 (수정 시간 조작)
        old_file = self.backup_dir / "app_db_20200101_120000.db"
        old_file.write_text("old backup")

        # 파일 수정 시간을 2일 전으로 설정
        import time
        old_time = time.time() - (2 * 86400)
        os.utime(old_file, (old_time, old_time))

        result = database_backup.cleanup_old_backups()

        assert result == 1
        assert not old_file.exists()


class TestRestoreBackup:
    """restore_backup 함수 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path, monkeypatch):
        """테스트 환경 설정"""
        self.tmp_dir = tmp_path
        self.backup_dir = self.tmp_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.test_db_path = self.tmp_dir / "test.db"
        monkeypatch.setattr(config, "DATABASE_PATH", self.test_db_path)
        monkeypatch.setattr(database_backup, "BACKUP_DIR", self.backup_dir)

    def test_restore_nonexistent_backup(self):
        """존재하지 않는 백업 복구 시 False 반환"""
        result = database_backup.restore_backup("nonexistent.db")
        assert result is False

    def test_restore_uncompressed_backup(self):
        """압축되지 않은 백업 복구"""
        # 백업 파일 생성
        backup_content = "backup database content"
        backup_file = self.backup_dir / "app_db_20260101_120000.db"
        backup_file.write_text(backup_content)

        result = database_backup.restore_backup("app_db_20260101_120000.db")

        assert result is True
        assert config.DATABASE_PATH.read_text() == backup_content

    def test_restore_compressed_backup(self):
        """압축된 백업 복구"""
        # 압축 백업 파일 생성
        backup_content = b"compressed backup content"
        backup_file = self.backup_dir / "app_db_20260101_120000.db.gz"

        with gzip.open(backup_file, "wb") as f:
            f.write(backup_content)

        result = database_backup.restore_backup("app_db_20260101_120000.db.gz")

        assert result is True
        assert config.DATABASE_PATH.read_bytes() == backup_content


class TestListBackups:
    """list_backups 함수 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path, monkeypatch):
        """테스트 환경 설정"""
        self.tmp_dir = tmp_path
        self.backup_dir = self.tmp_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(database_backup, "BACKUP_DIR", self.backup_dir)

    def test_list_backups_empty(self):
        """백업이 없을 때 빈 리스트 반환"""
        result = database_backup.list_backups()
        assert result == []

    def test_list_backups_with_files(self):
        """백업 파일 목록 반환"""
        # 백업 파일들 생성
        backup1 = self.backup_dir / "app_db_20260101_120000.db"
        backup2 = self.backup_dir / "app_db_20260102_130000.db.gz"
        backup1.write_text("backup1")
        backup2.write_text("backup2")

        result = database_backup.list_backups()

        assert len(result) == 2
        # 최신 파일이 먼저
        assert result[0]["filename"] == "app_db_20260102_130000.db.gz"
        assert result[1]["filename"] == "app_db_20260101_120000.db"

    def test_list_backups_includes_metadata(self):
        """백업 메타데이터 포함"""
        backup_file = self.backup_dir / "app_db_20260101_120000.db"
        backup_file.write_text("backup content")

        result = database_backup.list_backups()

        assert len(result) == 1
        assert "filename" in result[0]
        assert "size_bytes" in result[0]
        assert "size_human" in result[0]
        assert "created_at" in result[0]
        assert "is_compressed" in result[0]
        assert result[0]["is_compressed"] is False


class TestFormatSize:
    """_format_size 함수 테스트"""

    def test_format_bytes(self):
        """바이트 단위"""
        result = database_backup._format_size(512)
        assert "B" in result

    def test_format_kilobytes(self):
        """킬로바이트 단위"""
        result = database_backup._format_size(1024)
        assert "KB" in result

    def test_format_megabytes(self):
        """메가바이트 단위"""
        result = database_backup._format_size(1024 * 1024)
        assert "MB" in result

    def test_format_gigabytes(self):
        """기가바이트 단위"""
        result = database_backup._format_size(1024 * 1024 * 1024)
        assert "GB" in result


class TestInitBackup:
    """init_backup 함수 테스트"""

    def test_init_creates_directory(self, tmp_path: Path, monkeypatch):
        """백업 디렉토리 생성"""
        backup_dir = tmp_path / "new_backups"
        monkeypatch.setattr(database_backup, "BACKUP_DIR", backup_dir)
        monkeypatch.setattr(config, "DATABASE_PATH", tmp_path / "test.db")

        # 데이터베이스 파일 생성
        config.DATABASE_PATH.write_text("test")

        database_backup.init_backup()

        assert backup_dir.exists()


class TestBackupScheduler:
    """start_backup_scheduler 함수 테스트"""

    def test_scheduler_starts_thread(self, monkeypatch):
        """스케줄러 스레드 시작"""
        import threading

        started = []

        def fake_backup():
            started.append(True)

        monkeypatch.setattr(database_backup, "create_backup", fake_backup)

        # sleep을 즉시 반환하도록 설정
        with patch("time.sleep") as mock_sleep:
            mock_sleep.side_effect = lambda x: None

            database_backup.start_backup_scheduler()

            # 스레드가 시작되었는지 확인
            threads = [t for t in threading.enumerate() if t.name == "BackupScheduler"]
            assert len(threads) >= 1
