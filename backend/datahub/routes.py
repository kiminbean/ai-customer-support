"""
데이터 허브 FastAPI 라우트 — 데이터셋 탐색/다운로드/처리/임포트 API

비동기 작업(다운로드, 처리)은 메모리 기반 잡 큐로 관리하며,
job_id를 통해 진행 상태를 추적한다.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from datahub.downloader import download_dataset, clear_cache, get_download_info
from datahub.processor import (
    get_process_metadata,
    get_processed_data,
    process_dataset,
)
from datahub.registry import (
    get_all_datasets,
    get_dataset_info,
    get_datasets_by_domain,
    get_domains,
    search_datasets,
)

# ── 라우터 ─────────────────────────────────────────────────

router = APIRouter(prefix="/api/datahub", tags=["데이터 허브"])

# ── 인메모리 잡 스토어 ────────────────────────────────────

_MAX_JOBS = 500
_jobs: Dict[str, Dict[str, Any]] = OrderedDict()
_jobs_lock = threading.Lock()


def _create_job(job_type: str, dataset_id: str) -> str:
    """새로운 비동기 작업을 생성한다."""
    job_id = str(uuid.uuid4())
    with _jobs_lock:
        if len(_jobs) >= _MAX_JOBS:
            _jobs.popitem(last=False)
        _jobs[job_id] = {
            "job_id": job_id,
            "type": job_type,
            "dataset_id": dataset_id,
            "status": "pending",
            "progress": 0.0,
            "message": "대기 중...",
            "result": None,
            "error": None,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None,
        }
    return job_id


def _update_job(job_id: str, message: str, progress: float) -> None:
    """작업 진행 상태를 업데이트한다."""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["status"] = "running"
            _jobs[job_id]["message"] = message
            _jobs[job_id]["progress"] = min(progress, 1.0)


def _complete_job(job_id: str, result: Dict) -> None:
    """작업을 완료 처리한다."""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["status"] = "completed"
            _jobs[job_id]["progress"] = 1.0
            _jobs[job_id]["message"] = "완료"
            _jobs[job_id]["result"] = result
            _jobs[job_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")


def _fail_job(job_id: str, error: str) -> None:
    """작업을 실패 처리한다."""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["error"] = error
            _jobs[job_id]["message"] = f"실패: {error}"
            _jobs[job_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")


# ── Pydantic 요청/응답 모델 ───────────────────────────────


class DownloadRequest(BaseModel):
    """데이터셋 다운로드 요청"""
    dataset_id: str


class ProcessRequest(BaseModel):
    """데이터셋 처리 요청"""
    dataset_id: str
    translate: bool = False
    max_entries: Optional[int] = None


class ImportRequest(BaseModel):
    """데이터셋 임포트 요청"""
    dataset_id: str
    selected_entries: Optional[List[int]] = None


# ── 임포트된 데이터셋 스토어 ──────────────────────────────

_imported_datasets: Dict[str, Dict[str, Any]] = {}


# ── 도메인/데이터셋 탐색 API ──────────────────────────────


@router.get("/domains")
async def list_domains():
    """
    전체 도메인 목록과 각 도메인의 데이터셋 개수를 반환한다.
    """
    domains = get_domains()
    return {
        "domains": domains,
        "total": len(domains),
    }


@router.get("/datasets")
async def list_datasets(domain: Optional[str] = Query(None, description="도메인 필터")):
    """
    데이터셋 목록을 반환한다.
    domain 파라미터가 있으면 해당 도메인만 필터링.
    """
    if domain:
        datasets = get_datasets_by_domain(domain)
        if not datasets:
            # 도메인 이름을 검색어로도 시도
            datasets = search_datasets(domain)
    else:
        datasets = get_all_datasets()

    return {
        "datasets": datasets,
        "total": len(datasets),
        "domain_filter": domain,
    }


@router.get("/datasets/{dataset_id:path}")
async def get_dataset_detail(dataset_id: str):
    """
    특정 데이터셋의 상세 정보를 반환한다.
    다운로드/처리 상태도 포함.
    """
    info = get_dataset_info(dataset_id)
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"데이터셋을 찾을 수 없습니다: {dataset_id}",
        )

    # 다운로드 상태 확인
    download_info = get_download_info(dataset_id)
    info["download_status"] = download_info if download_info else None

    # 처리 상태 확인
    process_meta = get_process_metadata(dataset_id)
    info["process_status"] = process_meta if process_meta else None

    # 임포트 상태 확인
    info["imported"] = dataset_id in _imported_datasets

    return info


@router.get("/search")
async def search(q: str = Query(..., description="검색어")):
    """
    데이터셋을 검색한다.
    이름, 설명, 용도, ID에서 키워드를 매칭.
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="검색어를 입력해 주세요.")

    results = search_datasets(q)
    return {
        "query": q,
        "results": results,
        "total": len(results),
    }


# ── 다운로드 API ──────────────────────────────────────────


@router.post("/download")
async def start_download(request: DownloadRequest):
    """
    데이터셋 다운로드를 시작한다.
    비동기로 실행되며 job_id를 반환.
    """
    # 데이터셋 존재 확인
    ds_info = get_dataset_info(request.dataset_id)
    if not ds_info:
        raise HTTPException(
            status_code=404,
            detail=f"레지스트리에 없는 데이터셋입니다: {request.dataset_id}",
        )

    job_id = _create_job("download", request.dataset_id)

    # 백그라운드 스레드에서 다운로드 실행
    def _run_download():
        try:
            _update_job(job_id, "다운로드 시작...", 0.1)

            def progress_cb(message: str, progress: float):
                _update_job(job_id, message, progress)

            result = download_dataset(
                dataset_id=request.dataset_id,
                data_format=ds_info.get("format", "qa"),
                progress_callback=progress_cb,
            )

            if result.get("status") in ("completed", "cached"):
                _complete_job(job_id, result)
            else:
                _fail_job(job_id, result.get("error", "알 수 없는 오류"))

        except Exception as e:
            _fail_job(job_id, str(e))

    thread = threading.Thread(target=_run_download, daemon=True)
    thread.start()

    return {
        "job_id": job_id,
        "dataset_id": request.dataset_id,
        "status": "started",
        "message": "다운로드가 시작되었습니다.",
    }


@router.get("/download/{job_id}/status")
async def download_status(job_id: str):
    """다운로드 작업의 진행 상태를 확인한다."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"작업을 찾을 수 없습니다: {job_id}",
        )

    return {
        "job_id": job["job_id"],
        "type": job["type"],
        "dataset_id": job["dataset_id"],
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "result": job["result"],
        "error": job["error"],
        "created_at": job["created_at"],
        "completed_at": job["completed_at"],
    }


# ── 처리 API ──────────────────────────────────────────────


@router.post("/process")
async def start_processing(request: ProcessRequest):
    """
    다운로드된 데이터셋을 RAG 형식으로 처리한다.
    비동기로 실행되며 job_id를 반환.
    """
    # 데이터셋 존재 확인
    ds_info = get_dataset_info(request.dataset_id)
    if not ds_info:
        raise HTTPException(
            status_code=404,
            detail=f"레지스트리에 없는 데이터셋입니다: {request.dataset_id}",
        )

    job_id = _create_job("process", request.dataset_id)

    def _run_process():
        try:
            _update_job(job_id, "처리 시작...", 0.1)

            def progress_cb(message: str, progress: float):
                _update_job(job_id, message, progress)

            result = process_dataset(
                dataset_id=request.dataset_id,
                translate=request.translate,
                max_entries=request.max_entries,
                progress_callback=progress_cb,
            )

            if result.get("status") == "completed":
                _complete_job(job_id, result)
            else:
                _fail_job(job_id, result.get("error", "처리 실패"))

        except Exception as e:
            _fail_job(job_id, str(e))

    thread = threading.Thread(target=_run_process, daemon=True)
    thread.start()

    return {
        "job_id": job_id,
        "dataset_id": request.dataset_id,
        "translate": request.translate,
        "status": "started",
        "message": "데이터 처리가 시작되었습니다.",
    }


@router.get("/process/{job_id}/status")
async def process_status(job_id: str):
    """처리 작업의 진행 상태를 확인한다."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"작업을 찾을 수 없습니다: {job_id}",
        )

    return {
        "job_id": job["job_id"],
        "type": job["type"],
        "dataset_id": job["dataset_id"],
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "result": job["result"],
        "error": job["error"],
        "created_at": job["created_at"],
        "completed_at": job["completed_at"],
    }


# ── 임포트 API ────────────────────────────────────────────


@router.post("/import")
async def import_to_knowledge_base(request: ImportRequest):
    """
    처리된 데이터셋을 지식 베이스(벡터 스토어)로 임포트한다.

    selected_entries를 지정하면 특정 Q&A 항목만 임포트.
    """
    # 처리된 데이터 확인
    qa_data = get_processed_data(request.dataset_id)
    if not qa_data:
        raise HTTPException(
            status_code=404,
            detail="처리된 데이터를 찾을 수 없습니다. 먼저 다운로드 후 처리하세요.",
        )

    # 데이터셋 정보
    ds_info = get_dataset_info(request.dataset_id) or {}
    domain = ds_info.get("domain", "알 수 없음")
    ds_name = ds_info.get("name", request.dataset_id)

    # 선택된 항목만 필터링
    if request.selected_entries:
        selected = []
        for idx in request.selected_entries:
            if 0 <= idx < len(qa_data):
                selected.append(qa_data[idx])
        qa_data = selected

    if not qa_data:
        raise HTTPException(
            status_code=400,
            detail="임포트할 Q&A 항목이 없습니다.",
        )

    # 벡터 스토어에 추가
    try:
        from rag.vector_store import get_store

        store = get_store()
        texts: list[str] = []
        metadatas: list[dict] = []

        for idx, qa in enumerate(qa_data):
            question = qa.get("question", "")
            answer = qa.get("answer", "")
            category = qa.get("category", "")

            # RAG 문서 형식으로 텍스트 구성
            doc_text = f"[{domain}] {ds_name}\n카테고리: {category}\n\n질문: {question}\n답변: {answer}"

            texts.append(doc_text)
            metadatas.append({
                "source": f"datahub:{request.dataset_id}",
                "doc_type": "datahub_qa",
                "domain": domain,
                "dataset_name": ds_name,
                "category": category,
                "qa_index": idx,
            })

        doc_ids = store.add(texts=texts, metadatas=metadatas)

        # 임포트 기록 저장
        _imported_datasets[request.dataset_id] = {
            "dataset_id": request.dataset_id,
            "domain": domain,
            "dataset_name": ds_name,
            "imported_count": len(qa_data),
            "doc_ids": doc_ids,
            "imported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return {
            "status": "success",
            "dataset_id": request.dataset_id,
            "imported_count": len(qa_data),
            "message": f"'{ds_name}'에서 {len(qa_data)}개 Q&A가 지식 베이스에 추가되었습니다.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"임포트 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("/imported")
async def list_imported():
    """임포트된 데이터셋 목록과 통계를 반환한다."""
    imported_list = list(_imported_datasets.values())
    total_qa = sum(item["imported_count"] for item in imported_list)

    return {
        "imported_datasets": imported_list,
        "total_datasets": len(imported_list),
        "total_qa_pairs": total_qa,
    }


# ── 캐시 관리 API ─────────────────────────────────────────


@router.delete("/cache")
async def clear_download_cache(dataset_id: Optional[str] = Query(None)):
    """다운로드 캐시를 삭제한다."""
    result = clear_cache(dataset_id)
    return result


@router.get("/jobs")
async def list_jobs():
    """전체 작업 목록을 반환한다."""
    jobs_list = sorted(
        _jobs.values(),
        key=lambda j: j.get("created_at", ""),
        reverse=True,
    )
    return {
        "jobs": jobs_list,
        "total": len(jobs_list),
    }
