"""
데이터 허브 API 테스트 — 데이터셋 탐색/다운로드/처리/임포트 기능 검증
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


# ── 도메인 탐색 ────────────────────────────────────────────

def test_list_domains():
    """도메인 목록 조회"""
    resp = client.get("/api/datahub/domains")
    assert resp.status_code == 200
    data = resp.json()
    assert "domains" in data
    assert "total" in data
    assert data["total"] > 0
    
    # 도메인 구조 검증
    for domain in data["domains"]:
        assert "domain" in domain
        assert "dataset_count" in domain
        assert "avg_quality_score" in domain
        assert domain["dataset_count"] > 0


def test_domains_contain_expected_categories():
    """예상 도메인 카테고리 포함 확인"""
    resp = client.get("/api/datahub/domains")
    data = resp.json()
    domain_names = [d["domain"] for d in data["domains"]]
    
    expected_domains = ["이커머스", "금융/은행", "종합/멀티도메인", "SNS/소셜미디어", "의료/헬스케어", "IT/SaaS"]
    for expected in expected_domains:
        assert expected in domain_names, f"도메인 '{expected}'이 없습니다"


# ── 데이터셋 탐색 ──────────────────────────────────────────

def test_list_all_datasets():
    """전체 데이터셋 목록 조회"""
    resp = client.get("/api/datahub/datasets")
    assert resp.status_code == 200
    data = resp.json()
    assert "datasets" in data
    assert "total" in data
    assert data["total"] > 0
    
    # 데이터셋 구조 검증
    for ds in data["datasets"]:
        assert "id" in ds
        assert "name" in ds
        assert "domain" in ds
        assert "format" in ds


def test_list_datasets_by_domain():
    """도메인별 데이터셋 필터링"""
    resp = client.get("/api/datahub/datasets?domain=이커머스")
    assert resp.status_code == 200
    data = resp.json()
    assert "datasets" in data
    assert "domain_filter" in data
    assert data["domain_filter"] == "이커머스"
    assert data["total"] > 0
    
    # 데이터셋 구조 검증
    for ds in data["datasets"]:
        assert "id" in ds
        assert "name" in ds
        assert "format" in ds


def test_list_datasets_by_nonexistent_domain():
    """존재하지 않는 도메인으로 필터링"""
    resp = client.get("/api/datahub/datasets?domain=존재하지않는도메인")
    assert resp.status_code == 200
    data = resp.json()
    # 도메인이 없으면 검색 결과로 빈 리스트 반환
    assert data["total"] == 0


# ── 데이터셋 상세 조회 ────────────────────────────────────

def test_get_dataset_detail_known_dataset():
    """알려진 데이터셋 상세 정보 조회"""
    dataset_id = "rjac/e-commerce-customer-support-qa"
    resp = client.get(f"/api/datahub/datasets/{dataset_id}")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["id"] == dataset_id
    assert "name" in data
    assert "description" in data
    assert "domain" in data
    assert "format" in data
    assert "quality_score" in data
    assert "download_status" in data
    assert "process_status" in data
    assert "imported" in data


def test_get_dataset_detail_another_known_dataset():
    """다른 알려진 데이터셋 상세 정보 조회"""
    dataset_id = "bitext/Bitext-customer-support-llm-chatbot-training-dataset"
    resp = client.get(f"/api/datahub/datasets/{dataset_id}")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["id"] == dataset_id
    assert data["domain"] == "종합/멀티도메인"
    assert data["quality_score"] == 5.0


def test_get_dataset_detail_nonexistent():
    """존재하지 않는 데이터셋 조회 — 404"""
    resp = client.get("/api/datahub/datasets/nonexistent/dataset")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data


def test_get_dataset_detail_with_path_parameter():
    """경로 파라미터 형식의 데이터셋 ID 처리"""
    # 슬래시가 포함된 ID도 올바르게 처리되는지 확인
    dataset_id = "NebulaByte/E-Commerce_Customer_Support_Conversations"
    resp = client.get(f"/api/datahub/datasets/{dataset_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == dataset_id


# ── 데이터셋 검색 ──────────────────────────────────────────

def test_search_datasets_by_keyword():
    """키워드로 데이터셋 검색"""
    resp = client.get("/api/datahub/search?q=FAQ")
    assert resp.status_code == 200
    data = resp.json()
    assert "query" in data
    assert "results" in data
    assert "total" in data
    assert data["query"] == "FAQ"
    assert data["total"] > 0
    
    # 검색 결과 구조 검증
    for result in data["results"]:
        assert "id" in result
        assert "name" in result
        assert "domain" in result


def test_search_datasets_by_domain_keyword():
    """도메인 키워드로 검색"""
    resp = client.get("/api/datahub/search?q=이커머스")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0


def test_search_datasets_by_format():
    """포맷 키워드로 검색"""
    resp = client.get("/api/datahub/search?q=qa")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0


def test_search_datasets_empty_query():
    """빈 검색어 — 400 에러"""
    resp = client.get("/api/datahub/search?q=")
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data


def test_search_datasets_whitespace_only():
    """공백만 있는 검색어 — 400 에러"""
    resp = client.get("/api/datahub/search?q=   ")
    assert resp.status_code == 400


def test_search_datasets_no_results():
    """검색 결과 없음"""
    resp = client.get("/api/datahub/search?q=xyzabc123notfound")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["results"] == []


# ── 다운로드 API ───────────────────────────────────────────

def test_download_nonexistent_dataset():
    """존재하지 않는 데이터셋 다운로드 요청 — 404"""
    resp = client.post("/api/datahub/download", json={
        "dataset_id": "nonexistent/dataset"
    })
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data


def test_download_known_dataset_returns_job_id():
    """알려진 데이터셋 다운로드 요청 — job_id 반환"""
    resp = client.post("/api/datahub/download", json={
        "dataset_id": "rjac/e-commerce-customer-support-qa"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert "dataset_id" in data
    assert data["dataset_id"] == "rjac/e-commerce-customer-support-qa"
    assert "status" in data
    assert data["status"] == "started"


def test_download_job_status_tracking():
    """다운로드 작업 상태 추적"""
    # 다운로드 시작
    resp1 = client.post("/api/datahub/download", json={
        "dataset_id": "rjac/e-commerce-customer-support-qa"
    })
    job_id = resp1.json()["job_id"]
    
    # 작업 상태 조회
    resp2 = client.get(f"/api/datahub/download/{job_id}/status")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "progress" in data
    assert "message" in data
    assert "created_at" in data


def test_download_job_status_nonexistent():
    """존재하지 않는 작업 상태 조회 — 404"""
    resp = client.get("/api/datahub/download/nonexistent-job-id/status")
    assert resp.status_code == 404


# ── 처리 API ───────────────────────────────────────────────

def test_process_nonexistent_dataset():
    """존재하지 않는 데이터셋 처리 요청 — 404"""
    resp = client.post("/api/datahub/process", json={
        "dataset_id": "nonexistent/dataset"
    })
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data


def test_process_known_dataset_returns_job_id():
    """알려진 데이터셋 처리 요청 — job_id 반환"""
    resp = client.post("/api/datahub/process", json={
        "dataset_id": "rjac/e-commerce-customer-support-qa",
        "translate": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert "dataset_id" in data
    assert "translate" in data
    assert data["status"] == "started"


def test_process_with_translation_flag():
    """번역 플래그를 포함한 처리 요청"""
    resp = client.post("/api/datahub/process", json={
        "dataset_id": "bitext/Bitext-customer-support-llm-chatbot-training-dataset",
        "translate": True,
        "max_entries": 100
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["translate"] is True


def test_process_job_status_tracking():
    """처리 작업 상태 추적"""
    # 처리 시작
    resp1 = client.post("/api/datahub/process", json={
        "dataset_id": "rjac/e-commerce-customer-support-qa"
    })
    job_id = resp1.json()["job_id"]
    
    # 작업 상태 조회
    resp2 = client.get(f"/api/datahub/process/{job_id}/status")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "progress" in data
    assert "created_at" in data


def test_process_job_status_nonexistent():
    """존재하지 않는 처리 작업 상태 조회 — 404"""
    resp = client.get("/api/datahub/process/nonexistent-job-id/status")
    assert resp.status_code == 404


# ── 임포트 API ────────────────────────────────────────────

def test_list_imported_datasets_initially_empty():
    """초기 임포트 데이터셋 목록 (비어있음)"""
    resp = client.get("/api/datahub/imported")
    assert resp.status_code == 200
    data = resp.json()
    assert "imported_datasets" in data
    assert "total_datasets" in data
    assert "total_qa_pairs" in data
    # 초기 상태에서는 비어있을 수 있음
    assert isinstance(data["imported_datasets"], list)


# ── 작업 목록 API ──────────────────────────────────────────

def test_list_jobs():
    """전체 작업 목록 조회"""
    resp = client.get("/api/datahub/jobs")
    assert resp.status_code == 200
    data = resp.json()
    assert "jobs" in data
    assert "total" in data
    assert isinstance(data["jobs"], list)


def test_list_jobs_after_download_request():
    """다운로드 요청 후 작업 목록에 포함"""
    # 다운로드 요청
    resp1 = client.post("/api/datahub/download", json={
        "dataset_id": "rjac/e-commerce-customer-support-qa"
    })
    job_id = resp1.json()["job_id"]
    
    # 작업 목록 조회
    resp2 = client.get("/api/datahub/jobs")
    assert resp2.status_code == 200
    data = resp2.json()
    
    # 생성한 작업이 목록에 있는지 확인
    job_ids = [job["job_id"] for job in data["jobs"]]
    assert job_id in job_ids


def test_list_jobs_contains_job_details():
    """작업 목록의 각 항목이 필요한 필드를 포함"""
    resp = client.get("/api/datahub/jobs")
    data = resp.json()
    
    if data["total"] > 0:
        for job in data["jobs"]:
            assert "job_id" in job
            assert "type" in job
            assert "dataset_id" in job
            assert "status" in job
            assert "created_at" in job


# ── 캐시 관리 API ──────────────────────────────────────────

def test_clear_cache():
    """캐시 삭제"""
    resp = client.delete("/api/datahub/cache")
    assert resp.status_code == 200
    data = resp.json()
    assert "cleared" in data
    assert "message" in data


def test_clear_cache_specific_dataset():
    """특정 데이터셋 캐시 삭제"""
    resp = client.delete("/api/datahub/cache?dataset_id=rjac/e-commerce-customer-support-qa")
    assert resp.status_code == 200
    data = resp.json()
    assert "cleared" in data
    assert "message" in data


# ── 통합 시나리오 ──────────────────────────────────────────

def test_full_workflow_domain_to_dataset():
    """도메인 탐색 → 데이터셋 조회 → 상세 정보 조회"""
    # 1. 도메인 목록 조회
    resp1 = client.get("/api/datahub/domains")
    domains = resp1.json()["domains"]
    assert len(domains) > 0
    
    # 2. 첫 번째 도메인의 데이터셋 조회
    first_domain = domains[0]["domain"]
    resp2 = client.get(f"/api/datahub/datasets?domain={first_domain}")
    datasets = resp2.json()["datasets"]
    assert len(datasets) > 0
    
    # 3. 첫 번째 데이터셋의 상세 정보 조회
    first_dataset_id = datasets[0]["id"]
    resp3 = client.get(f"/api/datahub/datasets/{first_dataset_id}")
    assert resp3.status_code == 200
    detail = resp3.json()
    assert detail["id"] == first_dataset_id
    assert detail["domain"] == first_domain


def test_search_and_get_detail():
    """검색 → 상세 정보 조회"""
    # 1. 검색
    resp1 = client.get("/api/datahub/search?q=customer")
    results = resp1.json()["results"]
    assert len(results) > 0
    
    # 2. 첫 번째 결과의 상세 정보 조회
    first_result_id = results[0]["id"]
    resp2 = client.get(f"/api/datahub/datasets/{first_result_id}")
    assert resp2.status_code == 200
    detail = resp2.json()
    assert detail["id"] == first_result_id


def test_multiple_job_tracking():
    """여러 작업 동시 추적"""
    job_ids = []
    
    # 3개의 다운로드 작업 생성
    for i in range(3):
        resp = client.post("/api/datahub/download", json={
            "dataset_id": "rjac/e-commerce-customer-support-qa"
        })
        if resp.status_code == 200:
            job_ids.append(resp.json()["job_id"])
    
    # 각 작업의 상태 확인
    for job_id in job_ids:
        resp = client.get(f"/api/datahub/download/{job_id}/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == job_id
        assert "status" in data
