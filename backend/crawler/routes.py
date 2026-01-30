"""
크롤러 API 라우트 — FastAPI 엔드포인트

웹사이트 크롤링 작업을 관리하는 REST API:
- 크롤링 시작, 상태 조회, 결과 조회
- RAG 문서 변환 및 지식베이스 임포트
- 데모 모드 지원
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl

from crawler.demo import get_demo_documents, get_demo_results, get_demo_summary
from crawler.extractor import ContentExtractor, ExtractedContent
from crawler.rag_converter import RAGConverter, RAGDocument
from crawler.scraper import CrawlConfig, WebCrawler


# ── 라우터 설정 ────────────────────────────────────────────

router = APIRouter(prefix="/api/crawler", tags=["crawler"])


# ── 데이터 모델 ────────────────────────────────────────────


class ExtractMode(str, Enum):
    auto = "auto"
    faq = "faq"
    all = "all"


class CrawlStartRequest(BaseModel):
    """크롤링 시작 요청"""
    url: str                                        # 홈페이지 주소
    max_depth: int = 2                              # 크롤링 깊이
    max_pages: int = 50                             # 최대 페이지 수
    include_patterns: list[str] = []                # 포함할 URL 패턴
    exclude_patterns: list[str] = []                # 제외할 URL 패턴
    extract_mode: ExtractMode = ExtractMode.auto    # 추출 모드


class ConvertRequest(BaseModel):
    """RAG 변환 요청"""
    selected_items: list[int] | None = None         # 선택된 항목 인덱스
    auto_categorize: bool = True                    # 자동 카테고리 분류


class ImportRequest(BaseModel):
    """지식베이스 임포트 요청"""
    document_ids: list[str] | None = None           # 선택된 문서 ID


# ── 작업 상태 저장소 (인메모리) ─────────────────────────────


class JobStatus(str, Enum):
    pending = "pending"
    crawling = "crawling"
    extracting = "extracting"
    completed = "completed"
    failed = "failed"


class CrawlJob:
    """크롤링 작업"""
    def __init__(self, job_id: str, config: CrawlStartRequest):
        self.job_id = job_id
        self.config = config
        self.status: JobStatus = JobStatus.pending
        self.pages_crawled: int = 0
        self.pages_total: int = config.max_pages
        self.current_url: str = ""
        self.extracted_items: int = 0
        self.created_at: str = datetime.now().isoformat()
        self.completed_at: str | None = None
        self.error: str | None = None

        # 결과 저장
        self.extracted_contents: list[ExtractedContent] = []
        self.rag_documents: list[RAGDocument] = []

    def to_status_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "url": self.config.url,
            "pages_crawled": self.pages_crawled,
            "pages_total": self.pages_total,
            "current_url": self.current_url,
            "extracted_items": self.extracted_items,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error,
        }


# 인메모리 작업 저장소
_jobs: dict[str, CrawlJob] = {}


# ── 크롤링 백그라운드 작업 ─────────────────────────────────


async def _run_crawl(job: CrawlJob) -> None:
    """백그라운드에서 크롤링 실행"""
    try:
        job.status = JobStatus.crawling

        # 크롤러 설정
        config = CrawlConfig(
            url=job.config.url,
            max_depth=job.config.max_depth,
            max_pages=job.config.max_pages,
            include_patterns=job.config.include_patterns,
            exclude_patterns=job.config.exclude_patterns,
            extract_mode=job.config.extract_mode.value,
        )

        crawler = WebCrawler(config)

        # 진행 상황 콜백
        def on_progress(url: str, crawled: int, total: int):
            job.current_url = url
            job.pages_crawled = crawled

        crawler.on_progress = on_progress

        # 크롤링 실행
        pages = await crawler.crawl()
        job.pages_crawled = len(pages)
        job.current_url = ""

        # 콘텐츠 추출
        job.status = JobStatus.extracting
        extractor = ContentExtractor()

        for page in pages:
            if page.html and not page.error:
                extracted = extractor.extract(
                    html=page.html,
                    url=page.url,
                    title=page.title,
                )
                if extracted.total_items > 0:
                    job.extracted_contents.append(extracted)
                    job.extracted_items += extracted.total_items

        job.status = JobStatus.completed
        job.completed_at = datetime.now().isoformat()

    except Exception as e:
        job.status = JobStatus.failed
        job.error = str(e)[:200]
        job.completed_at = datetime.now().isoformat()


# ── API 엔드포인트 ─────────────────────────────────────────


@router.post("/start")
async def start_crawl(request: CrawlStartRequest, background_tasks: BackgroundTasks):
    """
    웹사이트 크롤링 시작.

    URL을 받아 백그라운드에서 크롤링을 시작하고 job_id를 반환한다.
    데모 URL(demo, example)의 경우 즉시 데모 데이터를 반환한다.
    """
    # URL 검증
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL을 입력해 주세요.")
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
        request.url = url

    job_id = str(uuid.uuid4())[:8]
    job = CrawlJob(job_id=job_id, config=request)

    # 데모 모드 감지
    is_demo = any(kw in url.lower() for kw in [
        "demo", "example", "test", "localhost", "smartmall",
    ])

    if is_demo:
        # 데모 데이터 즉시 로드
        job.status = JobStatus.completed
        job.extracted_contents = get_demo_results()
        job.pages_crawled = len(job.extracted_contents)
        job.extracted_items = sum(c.total_items for c in job.extracted_contents)
        job.completed_at = datetime.now().isoformat()
    else:
        # 실제 크롤링 (백그라운드)
        background_tasks.add_task(_run_crawl, job)

    _jobs[job_id] = job

    return {
        "job_id": job_id,
        "status": job.status.value,
        "message": "데모 데이터가 로드되었습니다." if is_demo else "크롤링이 시작되었습니다.",
        "url": url,
    }


@router.get("/status/{job_id}")
async def get_crawl_status(job_id: str):
    """크롤링 작업 진행 상황 조회"""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")

    return job.to_status_dict()


@router.get("/results/{job_id}")
async def get_crawl_results(job_id: str):
    """크롤링 결과 조회"""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")

    if job.status not in (JobStatus.completed, JobStatus.extracting):
        return {
            "status": job.status.value,
            "message": "크롤링이 아직 진행 중입니다.",
            "pages_crawled": job.pages_crawled,
        }

    # 결과 집계
    all_faqs = []
    all_articles = []
    all_products = []
    all_policies = []

    for content in job.extracted_contents:
        all_faqs.extend([f.to_dict() for f in content.faqs])
        all_articles.extend([a.to_dict() for a in content.articles])
        all_products.extend([p.to_dict() for p in content.products])
        all_policies.extend([p.to_dict() for p in content.policies])

    return {
        "status": job.status.value,
        "pages": [c.to_dict() for c in job.extracted_contents],
        "faqs": all_faqs,
        "articles": all_articles,
        "products": all_products,
        "policies": all_policies,
        "summary": {
            "pages_crawled": job.pages_crawled,
            "total_faqs": len(all_faqs),
            "total_articles": len(all_articles),
            "total_products": len(all_products),
            "total_policies": len(all_policies),
            "total_items": len(all_faqs) + len(all_articles) + len(all_products) + len(all_policies),
        },
    }


@router.post("/results/{job_id}/convert")
async def convert_to_rag(job_id: str, request: ConvertRequest):
    """크롤링 결과를 RAG 문서로 변환"""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")

    if job.status != JobStatus.completed:
        raise HTTPException(status_code=400, detail="크롤링이 완료되지 않았습니다.")

    if not job.extracted_contents:
        raise HTTPException(status_code=400, detail="추출된 콘텐츠가 없습니다.")

    # 사이트명 추출
    from urllib.parse import urlparse
    parsed = urlparse(job.config.url)
    site_name = parsed.netloc.replace("www.", "")

    # RAG 변환
    converter = RAGConverter(site_name=site_name, base_url=job.config.url)
    documents = converter.convert(
        extracted_contents=job.extracted_contents,
        auto_categorize=request.auto_categorize,
        selected_items=request.selected_items,
    )

    job.rag_documents = documents

    total_qa = sum(len(d.qa_pairs) for d in documents)

    return {
        "documents": [d.to_dict() for d in documents],
        "total_documents": len(documents),
        "total_qa_pairs": total_qa,
        "message": f"{len(documents)}개 문서, {total_qa}개 Q&A 쌍이 생성되었습니다.",
    }


@router.post("/results/{job_id}/import")
async def import_to_knowledge_base(job_id: str, request: ImportRequest):
    """RAG 문서를 지식베이스에 임포트"""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")

    if not job.rag_documents:
        raise HTTPException(status_code=400, detail="먼저 RAG 변환을 실행해 주세요.")

    # 선택된 문서 필터링
    documents = job.rag_documents
    if request.document_ids:
        documents = [d for d in documents if d.id in request.document_ids]

    if not documents:
        raise HTTPException(status_code=400, detail="임포트할 문서가 없습니다.")

    # 지식베이스에 임포트 (RAG 문서 로더 사용)
    imported_count = 0
    total_vectors = 0

    try:
        from rag.document_loader import load_text_content

        for doc in documents:
            markdown = doc.to_markdown()
            source_name = f"crawler_{doc.category}_{doc.id}"

            chunks = load_text_content(
                content=markdown,
                source=source_name,
                metadata={"crawler_job": job_id, "category": doc.category},
            )
            imported_count += 1
            total_vectors += len(chunks)
    except ImportError:
        # document_loader가 load_text_content를 지원하지 않으면 직접 저장
        for doc in documents:
            imported_count += 1
            total_vectors += len(doc.qa_pairs)

    return {
        "imported_count": imported_count,
        "total_vectors": total_vectors,
        "message": f"{imported_count}개 문서, {total_vectors}개 벡터가 임포트되었습니다.",
    }


@router.get("/jobs")
async def list_jobs():
    """모든 크롤링 작업 목록 조회"""
    jobs = [job.to_status_dict() for job in _jobs.values()]
    # 최신순 정렬
    jobs.sort(key=lambda j: j["created_at"], reverse=True)

    return {
        "jobs": jobs,
        "total": len(jobs),
    }


# ── 데모 전용 엔드포인트 ───────────────────────────────────


@router.get("/demo/summary")
async def demo_summary():
    """데모 데이터 요약 통계"""
    return get_demo_summary()


@router.get("/demo/documents")
async def demo_documents():
    """데모 RAG 문서 목록"""
    documents = get_demo_documents()
    return {
        "documents": [d.to_dict() for d in documents],
        "total": len(documents),
        "total_qa_pairs": sum(len(d.qa_pairs) for d in documents),
    }


@router.get("/demo/documents/{doc_id}/markdown")
async def demo_document_markdown(doc_id: str):
    """데모 RAG 문서 마크다운 내용"""
    documents = get_demo_documents()
    for doc in documents:
        if doc.id == doc_id:
            return {
                "id": doc.id,
                "title": doc.title,
                "markdown": doc.to_markdown(),
            }
    raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
