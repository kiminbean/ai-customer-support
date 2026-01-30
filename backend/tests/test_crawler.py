"""
크롤러 API 테스트 — 웹 크롤링 엔드포인트 통합 테스트
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


# ── 크롤링 시작 ────────────────────────────────────────────

def test_start_crawl_demo_url():
    """데모 URL로 크롤링 시작 — 즉시 완료"""
    resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
        "max_depth": 2,
        "max_pages": 50,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "completed"
    assert "demo" in data["message"].lower() or "로드" in data["message"]
    assert "example.com" in data["url"]


def test_start_crawl_empty_url():
    """빈 URL로 크롤링 시작 — 400 에러"""
    resp = client.post("/api/crawler/start", json={
        "url": "   ",
        "max_depth": 2,
        "max_pages": 50,
    })
    assert resp.status_code == 400
    assert "URL" in resp.json()["detail"]


def test_start_crawl_url_without_scheme():
    """스킴 없는 URL — https:// 자동 추가"""
    resp = client.post("/api/crawler/start", json={
        "url": "www.example.com/demo",
        "max_depth": 2,
        "max_pages": 50,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["url"].startswith("https://")
    assert "example.com" in data["url"]


def test_start_crawl_example_keyword():
    """'example' 키워드 포함 URL — 데모 모드 감지"""
    resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/shop",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"


def test_start_crawl_test_keyword():
    """'test' 키워드 포함 URL — 데모 모드 감지"""
    resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/test",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"


def test_start_crawl_localhost_keyword():
    """'localhost' 키워드 포함 URL — 데모 모드 감지"""
    resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/localhost",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"


# ── 크롤링 상태 조회 ───────────────────────────────────────

def test_get_crawl_status_valid_job():
    """유효한 작업 ID로 상태 조회"""
    # 먼저 크롤링 시작
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    # 상태 조회
    resp = client.get(f"/api/crawler/status/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["job_id"] == job_id
    assert data["status"] in ("pending", "crawling", "extracting", "completed", "failed")
    assert "pages_crawled" in data
    assert "pages_total" in data
    assert "created_at" in data


def test_get_crawl_status_invalid_job():
    """존재하지 않는 작업 ID로 상태 조회 — 404"""
    resp = client.get("/api/crawler/status/nonexistent-job-id")
    assert resp.status_code == 404
    assert "찾을 수 없습니다" in resp.json()["detail"]


# ── 크롤링 결과 조회 ───────────────────────────────────────

def test_get_crawl_results_completed_demo_job():
    """완료된 데모 작업의 결과 조회"""
    # 데모 크롤링 시작
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    # 결과 조회
    resp = client.get(f"/api/crawler/results/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert "pages" in data
    assert "faqs" in data
    assert "articles" in data
    assert "products" in data
    assert "policies" in data
    assert "summary" in data

    # 데모 데이터 검증
    summary = data["summary"]
    assert summary["pages_crawled"] > 0
    assert summary["total_faqs"] > 0
    assert summary["total_items"] > 0


def test_get_crawl_results_invalid_job():
    """존재하지 않는 작업 ID로 결과 조회 — 404"""
    resp = client.get("/api/crawler/results/nonexistent-job-id")
    assert resp.status_code == 404


# ── RAG 변환 ──────────────────────────────────────────────

def test_convert_to_rag_demo_job():
    """데모 작업을 RAG 문서로 변환"""
    # 데모 크롤링 시작
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    # RAG 변환
    resp = client.post(f"/api/crawler/results/{job_id}/convert", json={
        "auto_categorize": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert "total_documents" in data
    assert "total_qa_pairs" in data
    assert data["total_documents"] > 0
    assert data["total_qa_pairs"] > 0

    # 문서 구조 검증
    for doc in data["documents"]:
        assert "id" in doc
        assert "title" in doc
        assert "category" in doc
        assert "qa_pairs" in doc


def test_convert_to_rag_invalid_job():
    """존재하지 않는 작업 ID로 RAG 변환 — 404"""
    resp = client.post("/api/crawler/results/nonexistent-job-id/convert", json={
        "auto_categorize": True,
    })
    assert resp.status_code == 404


def test_convert_to_rag_with_selected_items():
    """선택된 항목만 RAG 변환"""
    # 데모 크롤링 시작
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    # 선택된 항목만 변환
    resp = client.post(f"/api/crawler/results/{job_id}/convert", json={
        "selected_items": [0, 1],
        "auto_categorize": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert data["total_documents"] >= 0


# ── 지식베이스 임포트 ──────────────────────────────────────

def test_import_to_knowledge_base():
    """RAG 문서를 지식베이스에 임포트"""
    # 데모 크롤링 시작
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    # RAG 변환
    convert_resp = client.post(f"/api/crawler/results/{job_id}/convert", json={
        "auto_categorize": True,
    })
    assert convert_resp.status_code == 200

    # 지식베이스 임포트
    resp = client.post(f"/api/crawler/results/{job_id}/import", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert "imported_count" in data
    assert "total_vectors" in data
    assert data["imported_count"] > 0
    assert data["total_vectors"] > 0


def test_import_to_knowledge_base_invalid_job():
    """존재하지 않는 작업 ID로 임포트 — 404"""
    resp = client.post("/api/crawler/results/nonexistent-job-id/import", json={})
    assert resp.status_code == 404


def test_import_to_knowledge_base_without_convert():
    """변환 없이 임포트 시도 — 400"""
    # 데모 크롤링 시작 (변환 없음)
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    # 변환 없이 임포트 시도
    resp = client.post(f"/api/crawler/results/{job_id}/import", json={})
    assert resp.status_code == 400
    assert "변환" in resp.json()["detail"]


def test_import_with_selected_documents():
    """선택된 문서만 임포트"""
    # 데모 크롤링 시작
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    # RAG 변환
    convert_resp = client.post(f"/api/crawler/results/{job_id}/convert", json={
        "auto_categorize": True,
    })
    docs = convert_resp.json()["documents"]
    if docs:
        selected_ids = [docs[0]["id"]]

        # 선택된 문서만 임포트
        resp = client.post(f"/api/crawler/results/{job_id}/import", json={
            "document_ids": selected_ids,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["imported_count"] >= 0


# ── 작업 목록 조회 ────────────────────────────────────────

def test_list_jobs():
    """모든 크롤링 작업 목록 조회"""
    # 먼저 작업 생성
    client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })

    # 목록 조회
    resp = client.get("/api/crawler/jobs")
    assert resp.status_code == 200
    data = resp.json()
    assert "jobs" in data
    assert "total" in data
    assert data["total"] >= 1

    # 작업 구조 검증
    for job in data["jobs"]:
        assert "job_id" in job
        assert "status" in job
        assert "url" in job
        assert "created_at" in job


def test_list_jobs_empty():
    """작업이 없을 때 빈 목록 반환"""
    # 새로운 테스트 세션에서는 작업이 없을 수 있음
    resp = client.get("/api/crawler/jobs")
    assert resp.status_code == 200
    data = resp.json()
    assert "jobs" in data
    assert "total" in data
    assert isinstance(data["jobs"], list)


# ── 데모 전용 엔드포인트 ───────────────────────────────────

def test_demo_summary():
    """데모 데이터 요약 통계"""
    resp = client.get("/api/crawler/demo/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "site_name" in data
    assert "site_url" in data
    assert "pages_crawled" in data
    assert "total_faqs" in data
    assert "total_articles" in data
    assert "total_products" in data
    assert "total_policies" in data
    assert "total_extracted_items" in data
    assert "rag_documents" in data
    assert "total_qa_pairs" in data
    assert "categories" in data

    # 데이터 검증
    assert data["pages_crawled"] > 0
    assert data["total_faqs"] > 0
    assert data["total_qa_pairs"] > 0


def test_demo_documents():
    """데모 RAG 문서 목록"""
    resp = client.get("/api/crawler/demo/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert "total" in data
    assert "total_qa_pairs" in data
    assert data["total"] > 0
    assert data["total_qa_pairs"] > 0

    # 문서 구조 검증
    for doc in data["documents"]:
        assert "id" in doc
        assert "title" in doc
        assert "category" in doc
        assert "qa_pairs" in doc


def test_demo_document_markdown_endpoint_exists():
    """데모 RAG 문서 마크다운 엔드포인트 존재 확인"""
    resp = client.get("/api/crawler/demo/documents/test-doc-id/markdown")
    assert resp.status_code == 404
    assert "문서를 찾을 수 없습니다" in resp.json()["detail"]


def test_demo_document_markdown_invalid():
    """데모 RAG 문서 마크다운 내용 — 존재하지 않는 문서 ID"""
    resp = client.get("/api/crawler/demo/documents/nonexistent-doc-id/markdown")
    assert resp.status_code == 404
    assert "찾을 수 없습니다" in resp.json()["detail"]


# ── 통합 시나리오 ────────────────────────────────────────

def test_full_crawl_convert_import_flow():
    """전체 크롤링 → 변환 → 임포트 플로우"""
    # 1. 크롤링 시작
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
        "max_depth": 2,
        "max_pages": 50,
    })
    assert start_resp.status_code == 200
    job_id = start_resp.json()["job_id"]
    assert start_resp.json()["status"] == "completed"

    # 2. 상태 확인
    status_resp = client.get(f"/api/crawler/status/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "completed"

    # 3. 결과 조회
    results_resp = client.get(f"/api/crawler/results/{job_id}")
    assert results_resp.status_code == 200
    results = results_resp.json()
    assert results["status"] == "completed"
    assert results["summary"]["total_items"] > 0

    # 4. RAG 변환
    convert_resp = client.post(f"/api/crawler/results/{job_id}/convert", json={
        "auto_categorize": True,
    })
    assert convert_resp.status_code == 200
    convert_data = convert_resp.json()
    assert convert_data["total_documents"] > 0
    assert convert_data["total_qa_pairs"] > 0

    # 5. 지식베이스 임포트
    import_resp = client.post(f"/api/crawler/results/{job_id}/import", json={})
    assert import_resp.status_code == 200
    import_data = import_resp.json()
    assert import_data["imported_count"] > 0
    assert import_data["total_vectors"] > 0


def test_multiple_crawl_jobs():
    """여러 크롤링 작업 동시 관리"""
    job_ids = []

    # 3개의 크롤링 작업 시작
    for i in range(3):
        resp = client.post("/api/crawler/start", json={
            "url": f"https://www.example.com/demo-{i}",
        })
        assert resp.status_code == 200
        job_ids.append(resp.json()["job_id"])

    # 모든 작업 상태 확인
    for job_id in job_ids:
        resp = client.get(f"/api/crawler/status/{job_id}")
        assert resp.status_code == 200
        assert resp.json()["job_id"] == job_id

    # 작업 목록에서 모든 작업 확인
    list_resp = client.get("/api/crawler/jobs")
    assert list_resp.status_code == 200
    jobs = list_resp.json()["jobs"]
    assert len(jobs) >= 3


def test_crawl_with_custom_config():
    """커스텀 설정으로 크롤링"""
    resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
        "max_depth": 3,
        "max_pages": 100,
        "include_patterns": ["/faq", "/help"],
        "exclude_patterns": ["/admin"],
        "extract_mode": "faq",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "completed"


# ── 엣지 케이스 ────────────────────────────────────────────

def test_start_crawl_with_trailing_slash():
    """URL 끝에 슬래시 포함"""
    resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo/",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"


def test_start_crawl_case_insensitive_demo_detection():
    """데모 키워드 대소문자 무시"""
    resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/DEMO",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"


def test_convert_request_with_no_selected_items():
    """선택 항목 없이 변환 요청"""
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    resp = client.post(f"/api/crawler/results/{job_id}/convert", json={
        "selected_items": None,
        "auto_categorize": True,
    })
    assert resp.status_code == 200
    assert resp.json()["total_documents"] > 0


def test_import_request_with_no_document_ids():
    """선택 문서 없이 임포트 요청"""
    start_resp = client.post("/api/crawler/start", json={
        "url": "https://www.example.com/demo",
    })
    job_id = start_resp.json()["job_id"]

    # 변환
    client.post(f"/api/crawler/results/{job_id}/convert", json={
        "auto_categorize": True,
    })

    # 모든 문서 임포트
    resp = client.post(f"/api/crawler/results/{job_id}/import", json={
        "document_ids": None,
    })
    assert resp.status_code == 200
    assert resp.json()["imported_count"] > 0
