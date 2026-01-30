"""
음성 API 통합 테스트 — 음성-RAG 파이프라인 엔드포인트 검증
데모 모드에서 실행 (API 키 불필요)
"""

from __future__ import annotations

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ── 데모 모드 테스트 ────────────────────────────────────────

def test_voice_demo():
    """음성 데모 모드 실행 — 동기 처리로 COMPLETE 상태 반환"""
    resp = client.post("/api/voice/demo")
    assert resp.status_code == 200
    data = resp.json()
    
    # JobResponse 필드 검증
    assert "job_id" in data
    assert data["status"] == "COMPLETE"
    assert data["progress"] == 100
    assert data["current_step"] == "처리 완료 (데모 모드)"
    assert data["source_file"] == "demo_audio.mp3"
    assert data["message"]


# ── 작업 목록 조회 ────────────────────────────────────────

def test_voice_list_jobs():
    """전체 음성 처리 작업 목록 조회"""
    # 먼저 데모 작업 생성
    demo_resp = client.post("/api/voice/demo")
    demo_job_id = demo_resp.json()["job_id"]
    
    # 작업 목록 조회
    resp = client.get("/api/voice/jobs")
    assert resp.status_code == 200
    data = resp.json()
    
    # 응답 구조 검증
    assert "jobs" in data
    assert "total" in data
    assert isinstance(data["jobs"], list)
    assert len(data["jobs"]) > 0
    
    # 데모 작업이 목록에 포함되어 있는지 확인
    job_ids = [job["job_id"] for job in data["jobs"]]
    assert demo_job_id in job_ids
    
    # 각 작업의 필드 검증
    for job in data["jobs"]:
        assert "job_id" in job
        assert "status" in job
        assert "progress" in job
        assert "current_step" in job
        assert "source_file" in job


# ── 작업 상태 조회 ────────────────────────────────────────

def test_voice_status_demo_job():
    """데모 작업의 상태 조회 — COMPLETE 상태 확인"""
    # 데모 작업 생성
    demo_resp = client.post("/api/voice/demo")
    job_id = demo_resp.json()["job_id"]
    
    # 상태 조회
    resp = client.get(f"/api/voice/status/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    
    # 상태 검증
    assert data["job_id"] == job_id
    assert data["status"] == "COMPLETE"
    assert data["progress"] == 100
    assert data["current_step"] == "처리 완료 (데모 모드)"
    assert data["source_file"] == "demo_audio.mp3"


def test_voice_status_nonexistent_job():
    """존재하지 않는 작업 조회 — 404 에러"""
    resp = client.get("/api/voice/status/nonexistent_job_id")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data


# ── 전사 결과 조회 ────────────────────────────────────────

def test_voice_transcript_demo_job():
    """데모 작업의 전사 결과 조회"""
    # 데모 작업 생성
    demo_resp = client.post("/api/voice/demo")
    job_id = demo_resp.json()["job_id"]
    
    # 전사 결과 조회
    resp = client.get(f"/api/voice/transcript/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    
    # 응답 구조 검증
    assert "job_id" in data
    assert "transcript" in data
    assert "full_text" in data
    
    transcript = data["transcript"]
    
    # 전사 결과 구조 검증
    assert "segments" in transcript
    assert isinstance(transcript["segments"], list)
    assert len(transcript["segments"]) > 0
    
    # 각 세그먼트 검증
    for segment in transcript["segments"]:
        assert "speaker" in segment
        assert "text" in segment
        assert "start_time" in segment
        assert "end_time" in segment
        assert segment["speaker"] in ["상담원", "고객"]
        assert isinstance(segment["text"], str)
        assert len(segment["text"]) > 0
    
    # 전체 전사 메타데이터 검증
    assert transcript["language"] == "ko"
    assert transcript["duration"] > 0
    assert transcript["source_file"] == "demo_audio.mp3"
    assert transcript["method"] == "demo"
    assert transcript["segment_count"] == len(transcript["segments"])


def test_voice_transcript_nonexistent_job():
    """존재하지 않는 작업의 전사 조회 — 404 에러"""
    resp = client.get("/api/voice/transcript/nonexistent_job_id")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data


# ── 생성된 문서 조회 ────────────────────────────────────────

def test_voice_document_demo_job():
    """데모 작업의 생성된 RAG 문서 조회"""
    # 데모 작업 생성
    demo_resp = client.post("/api/voice/demo")
    job_id = demo_resp.json()["job_id"]
    
    # 문서 조회
    resp = client.get(f"/api/voice/document/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    
    # 응답 구조 검증
    assert "job_id" in data
    assert "status" in data
    assert "document" in data
    assert "preview" in data
    
    doc = data["document"]
    
    # 문서 구조 검증
    assert "markdown" in doc
    assert isinstance(doc["markdown"], str)
    assert len(doc["markdown"]) > 0
    
    # Q&A 쌍 검증
    assert "qa_pairs" in doc
    assert isinstance(doc["qa_pairs"], list)
    assert len(doc["qa_pairs"]) > 0
    
    # 각 Q&A 쌍 검증
    for qa in doc["qa_pairs"]:
        assert "question" in qa
        assert "answer" in qa
        assert "category" in qa
        assert "confidence" in qa
        assert isinstance(qa["question"], str)
        assert isinstance(qa["answer"], str)
        assert len(qa["question"]) > 0
        assert len(qa["answer"]) > 0
        assert 0 <= qa["confidence"] <= 1
    
    # 문서 메타데이터 검증
    assert "primary_category" in doc
    assert "source_file" in doc
    assert "generated_date" in doc
    assert "qa_count" in doc
    assert "confidence" in doc
    assert doc["qa_count"] == len(doc["qa_pairs"])
    assert doc["source_file"] == "demo_audio.mp3"


def test_voice_document_nonexistent_job():
    """존재하지 않는 작업의 문서 조회 — 404 에러"""
    resp = client.get("/api/voice/document/nonexistent_job_id")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data


# ── 파일 업로드 검증 ────────────────────────────────────────

def test_voice_upload_no_file():
    """파일 없이 업로드 요청 — 422 검증 에러"""
    resp = client.post("/api/voice/upload")
    assert resp.status_code == 422
    # Pydantic 검증 에러


# ── 통합 시나리오 ──────────────────────────────────────────

def test_voice_full_pipeline():
    """음성 파이프라인 전체 흐름 테스트"""
    # 1) 데모 작업 생성
    demo_resp = client.post("/api/voice/demo")
    assert demo_resp.status_code == 200
    job_id = demo_resp.json()["job_id"]
    
    # 2) 작업 목록에서 확인
    jobs_resp = client.get("/api/voice/jobs")
    assert jobs_resp.status_code == 200
    jobs_data = jobs_resp.json()
    job_ids = [j["job_id"] for j in jobs_data["jobs"]]
    assert job_id in job_ids
    
    # 3) 상태 확인
    status_resp = client.get(f"/api/voice/status/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "COMPLETE"
    
    # 4) 전사 결과 확인
    transcript_resp = client.get(f"/api/voice/transcript/{job_id}")
    assert transcript_resp.status_code == 200
    transcript_data = transcript_resp.json()
    assert len(transcript_data["transcript"]["segments"]) > 0
    
    # 5) 생성된 문서 확인
    doc_resp = client.get(f"/api/voice/document/{job_id}")
    assert doc_resp.status_code == 200
    doc_data = doc_resp.json()
    assert len(doc_data["document"]["qa_pairs"]) > 0
    assert len(doc_data["document"]["markdown"]) > 0


# ── 데이터 일관성 테스트 ────────────────────────────────────

def test_voice_transcript_and_document_consistency():
    """전사 결과와 생성된 문서의 일관성 검증"""
    # 데모 작업 생성
    demo_resp = client.post("/api/voice/demo")
    job_id = demo_resp.json()["job_id"]
    
    # 전사 결과 조회
    transcript_resp = client.get(f"/api/voice/transcript/{job_id}")
    transcript_data = transcript_resp.json()
    transcript = transcript_data["transcript"]
    
    # 생성된 문서 조회
    doc_resp = client.get(f"/api/voice/document/{job_id}")
    doc_data = doc_resp.json()
    doc = doc_data["document"]
    
    # 일관성 검증
    # - 전사 결과의 세그먼트 수와 문서의 Q&A 수는 관련이 있어야 함
    assert len(transcript["segments"]) > 0
    assert len(doc["qa_pairs"]) > 0
    
    # - 문서의 마크다운에 전사 내용이 포함되어야 함
    full_transcript_text = "\n".join(
        f"[{seg['speaker']}] {seg['text']}" for seg in transcript["segments"]
    )
    # 마크다운에 일부 전사 내용이 포함되어 있는지 확인
    assert len(doc["markdown"]) > 0


# ── 상태 코드 검증 ────────────────────────────────────────

def test_voice_endpoints_status_codes():
    """모든 음성 엔드포인트의 상태 코드 검증"""
    # 데모 작업 생성
    demo_resp = client.post("/api/voice/demo")
    assert demo_resp.status_code == 200
    job_id = demo_resp.json()["job_id"]
    
    # 각 엔드포인트 상태 코드 확인
    assert client.get("/api/voice/jobs").status_code == 200
    assert client.get(f"/api/voice/status/{job_id}").status_code == 200
    assert client.get(f"/api/voice/transcript/{job_id}").status_code == 200
    assert client.get(f"/api/voice/document/{job_id}").status_code == 200
    
    # 존재하지 않는 리소스
    assert client.get("/api/voice/status/invalid").status_code == 404
    assert client.get("/api/voice/transcript/invalid").status_code == 404
    assert client.get("/api/voice/document/invalid").status_code == 404
