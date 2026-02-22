"""
Tests for job_persistence module
Target: Increase coverage from 33% to 80%+
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import job_persistence
import config


class TestJobPersistenceSetup:
    """초기화 및 설정 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path, monkeypatch):
        """테스트 환경 설정"""
        self.tmp_dir = tmp_path
        self.storage_path = self.tmp_dir / "jobs.json"
        self.lock_file = self.tmp_dir / "jobs.lock"

        # config 모킹
        monkeypatch.setattr(config, "DATA_DIR", self.tmp_dir)
        monkeypatch.setattr(job_persistence, "JOB_STORAGE_PATH", self.storage_path)
        monkeypatch.setattr(job_persistence, "_LOCK_FILE", self.lock_file)

        # 저장소 초기화
        job_persistence._job_stores = {
            "crawler": {},
            "datahub": {},
            "voice": {},
        }


class TestSaveLoadJobs(TestJobPersistenceSetup):
    """저장/로드 테스트"""

    def test_save_jobs_creates_file(self):
        """_save_jobs가 파일 생성"""
        job_persistence._job_stores["crawler"]["test_id"] = {"status": "running"}

        result = job_persistence._save_jobs()

        assert result is True
        assert self.storage_path.exists()

    def test_save_jobs_content(self):
        """저장된 내용 확인"""
        job_persistence._job_stores["crawler"]["job1"] = {"url": "https://example.com"}
        job_persistence._job_stores["datahub"]["job2"] = {"dataset": "test"}

        job_persistence._save_jobs()

        with open(self.storage_path, "r") as f:
            data = json.load(f)

        assert data["crawler"]["job1"]["url"] == "https://example.com"
        assert data["datahub"]["job2"]["dataset"] == "test"

    def test_load_jobs_restores_data(self, monkeypatch):
        """_load_jobs가 데이터 복구"""
        # 저장 파일 생성
        saved_data = {
            "crawler": {"restored_job": {"status": "completed"}},
            "datahub": {},
            "voice": {},
        }
        with open(self.storage_path, "w") as f:
            json.dump(saved_data, f)

        job_persistence._load_jobs()

        assert "restored_job" in job_persistence._job_stores["crawler"]

    def test_load_jobs_missing_file(self, monkeypatch):
        """파일이 없을 때 조용히 무시"""
        # 파일 없이 로드
        job_persistence._load_jobs()

        # 기본 저장소 유지
        assert job_persistence._job_stores == {
            "crawler": {},
            "datahub": {},
            "voice": {},
        }

    def test_load_jobs_invalid_json(self, monkeypatch):
        """잘못된 JSON 파일 처리"""
        # 잘못된 JSON 파일 생성
        with open(self.storage_path, "w") as f:
            f.write("not valid json{")

        job_persistence._load_jobs()

        # 기본 저장소 유지
        assert job_persistence._job_stores == {
            "crawler": {},
            "datahub": {},
            "voice": {},
        }


class TestInitJobPersistence(TestJobPersistenceSetup):
    """초기화 함수 테스트"""

    @patch("job_persistence._load_jobs")
    def test_init_calls_load(self, mock_load):
        """init_job_persistence가 _load_jobs 호출"""
        job_persistence.init_job_persistence()
        mock_load.assert_called_once()


class TestCrawlerJobs(TestJobPersistenceSetup):
    """크롤러 작업 테스트"""

    def test_save_crawl_job(self):
        """크롤러 작업 저장"""
        result = job_persistence.save_crawl_job("crawl-1", {
            "url": "https://example.com",
            "status": "running",
        })

        assert result is True
        assert "crawl-1" in job_persistence._job_stores["crawler"]

    def test_get_crawl_job(self):
        """크롤러 작업 조회"""
        job_persistence._job_stores["crawler"]["crawl-1"] = {"url": "https://test.com"}

        result = job_persistence.get_crawl_job("crawl-1")

        assert result["url"] == "https://test.com"

    def test_get_crawl_job_not_found(self):
        """존재하지 않는 작업 조회"""
        result = job_persistence.get_crawl_job("nonexistent")

        assert result is None

    def test_delete_crawl_job(self):
        """크롤러 작업 삭제"""
        job_persistence._job_stores["crawler"]["crawl-1"] = {"status": "done"}

        result = job_persistence.delete_crawl_job("crawl-1")

        assert result is True
        assert "crawl-1" not in job_persistence._job_stores["crawler"]

    def test_delete_crawl_job_not_found(self):
        """존재하지 않는 작업 삭제"""
        result = job_persistence.delete_crawl_job("nonexistent")

        assert result is True  # pop으로 안전하게 처리

    def test_list_crawl_jobs(self):
        """크롤러 작업 목록"""
        job_persistence._job_stores["crawler"] = {
            "job1": {"url": "a.com"},
            "job2": {"url": "b.com"},
        }

        result = job_persistence.list_crawl_jobs()

        assert len(result) == 2


class TestDatahubJobs(TestJobPersistenceSetup):
    """데이터허브 작업 테스트"""

    def test_save_datahub_job(self):
        """데이터허브 작업 저장"""
        result = job_persistence.save_datahub_job("dh-1", {
            "dataset": "test-dataset",
            "status": "processing",
        })

        assert result is True
        assert "dh-1" in job_persistence._job_stores["datahub"]

    def test_get_datahub_job(self):
        """데이터허브 작업 조회"""
        job_persistence._job_stores["datahub"]["dh-1"] = {"dataset": "test"}

        result = job_persistence.get_datahub_job("dh-1")

        assert result["dataset"] == "test"

    def test_delete_datahub_job(self):
        """데이터허브 작업 삭제"""
        job_persistence._job_stores["datahub"]["dh-1"] = {"status": "done"}

        result = job_persistence.delete_datahub_job("dh-1")

        assert result is True
        assert "dh-1" not in job_persistence._job_stores["datahub"]

    def test_list_datahub_jobs(self):
        """데이터허브 작업 목록"""
        job_persistence._job_stores["datahub"] = {
            "job1": {"dataset": "a"},
            "job2": {"dataset": "b"},
        }

        result = job_persistence.list_datahub_jobs()

        assert len(result) == 2


class TestVoiceJobs(TestJobPersistenceSetup):
    """음성 작업 테스트"""

    def test_save_voice_job(self):
        """음성 작업 저장"""
        result = job_persistence.save_voice_job("voice-1", {
            "file": "audio.mp3",
            "status": "transcribing",
        })

        assert result is True
        assert "voice-1" in job_persistence._job_stores["voice"]

    def test_get_voice_job(self):
        """음성 작업 조회"""
        job_persistence._job_stores["voice"]["voice-1"] = {"file": "test.mp3"}

        result = job_persistence.get_voice_job("voice-1")

        assert result["file"] == "test.mp3"

    def test_delete_voice_job(self):
        """음성 작업 삭제"""
        job_persistence._job_stores["voice"]["voice-1"] = {"status": "done"}

        result = job_persistence.delete_voice_job("voice-1")

        assert result is True
        assert "voice-1" not in job_persistence._job_stores["voice"]

    def test_list_voice_jobs(self):
        """음성 작업 목록"""
        job_persistence._job_stores["voice"] = {
            "job1": {"file": "a.mp3"},
            "job2": {"file": "b.mp3"},
        }

        result = job_persistence.list_voice_jobs()

        assert len(result) == 2


class TestGetAllJobs(TestJobPersistenceSetup):
    """전체 작업 조회 테스트"""

    def test_get_all_jobs(self):
        """모든 작업 조회"""
        job_persistence._job_stores = {
            "crawler": {"c1": {"url": "a.com"}},
            "datahub": {"d1": {"dataset": "test"}},
            "voice": {"v1": {"file": "audio.mp3"}},
        }

        result = job_persistence.get_all_jobs()

        assert len(result["crawler"]) == 1
        assert len(result["datahub"]) == 1
        assert len(result["voice"]) == 1


class TestClearOldJobs(TestJobPersistenceSetup):
    """오래된 작업 정리 테스트"""

    def test_clear_old_jobs_removes_expired(self, monkeypatch):
        """만료된 작업 삭제"""
        # 25시간 전 타임스탬프
        old_time = datetime.now().isoformat()
        from datetime import timedelta
        old_datetime = datetime.now() - timedelta(hours=25)
        old_time = old_datetime.isoformat()

        job_persistence._job_stores["crawler"] = {
            "old_job": {"created_at": old_time, "status": "done"},
            "new_job": {"created_at": datetime.now().isoformat(), "status": "running"},
        }

        result = job_persistence.clear_old_jobs(max_age_hours=24)

        assert result == 1
        assert "old_job" not in job_persistence._job_stores["crawler"]
        assert "new_job" in job_persistence._job_stores["crawler"]

    def test_clear_old_jobs_keeps_recent(self):
        """최근 작업 유지"""
        job_persistence._job_stores["crawler"] = {
            "recent_job": {"created_at": datetime.now().isoformat()},
        }

        result = job_persistence.clear_old_jobs(max_age_hours=24)

        assert result == 0
        assert "recent_job" in job_persistence._job_stores["crawler"]

    def test_clear_old_jobs_no_created_at(self):
        """created_at 없는 작업 유지"""
        job_persistence._job_stores["crawler"] = {
            "no_timestamp": {"status": "done"},
        }

        result = job_persistence.clear_old_jobs(max_age_hours=24)

        assert result == 0
        assert "no_timestamp" in job_persistence._job_stores["crawler"]

    def test_clear_old_jobs_invalid_timestamp(self):
        """잘못된 타임스탬프 처리"""
        job_persistence._job_stores["crawler"] = {
            "invalid_ts": {"created_at": "not-a-date"},
        }

        result = job_persistence.clear_old_jobs(max_age_hours=24)

        assert result == 0
        assert "invalid_ts" in job_persistence._job_stores["crawler"]

    def test_clear_old_jobs_all_stores(self):
        """모든 저장소에서 정리"""
        from datetime import timedelta
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()

        job_persistence._job_stores = {
            "crawler": {"old1": {"created_at": old_time}},
            "datahub": {"old2": {"created_at": old_time}},
            "voice": {"old3": {"created_at": old_time}},
        }

        result = job_persistence.clear_old_jobs(max_age_hours=24)

        assert result == 3
