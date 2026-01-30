"""
Voice-to-RAG FastAPI 라우트

엔드포인트:
- POST   /api/voice/upload              — 오디오 파일 업로드 + 처리 시작
- POST   /api/voice/demo                — 데모 모드 실행
- GET    /api/voice/status/{job_id}     — 처리 상태 조회
- GET    /api/voice/transcript/{job_id} — 전사 결과 조회
- GET    /api/voice/document/{job_id}   — 생성된 RAG 문서 조회
- POST   /api/voice/document/{job_id}/approve — 문서 승인 + 지식베이스 저장
- GET    /api/voice/jobs                — 전체 작업 목록
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pydantic import BaseModel

from voice.processor import VoiceProcessor, ProcessingStatus

# ── 설정 ───────────────────────────────────────────────────

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".webm", ".ogg"}

# 업로드 디렉토리
try:
    import config as _cfg
    UPLOAD_DIR = _cfg.UPLOAD_DIR / "voice"
except Exception:
    UPLOAD_DIR = Path("data/uploads/voice")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 프로세서 싱글턴
_processor = VoiceProcessor(upload_dir=UPLOAD_DIR)

router = APIRouter(prefix="/api/voice", tags=["Voice-to-RAG"])


# ── Pydantic 모델 ─────────────────────────────────────────

class QAPairEdit(BaseModel):
    question: str
    answer: str
    category: str = "기타"
    confidence: float = 0.8


class ApproveRequest(BaseModel):
    qa_pairs: Optional[List[QAPairEdit]] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    current_step: str
    source_file: str
    message: str = ""


# ── 라우트 ─────────────────────────────────────────────────

@router.post("/upload", response_model=JobResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    오디오 파일 업로드 및 처리 시작.
    
    지원 형식: MP3, WAV, M4A, WebM, OGG
    최대 크기: 50MB
    """
    # 파일 확장자 검증
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 없습니다.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다: {ext}. "
                   f"지원 형식: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 파일 크기 확인 (Content-Length 헤더 기반)
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기가 너무 큽니다. 최대 {MAX_FILE_SIZE // (1024*1024)}MB까지 허용됩니다.",
        )

    # 작업 생성
    job = _processor.create_job(source_file=file.filename)

    # 파일명 sanitize (경로 순회 방지)
    safe_filename = Path(file.filename).name  # 디렉토리 성분 제거
    save_path = UPLOAD_DIR / f"{job.job_id}_{safe_filename}"
    if not save_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=400, detail="잘못된 파일명입니다.")
    try:
        with open(save_path, "wb") as f:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                save_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"파일 크기가 너무 큽니다. 최대 {MAX_FILE_SIZE // (1024*1024)}MB까지 허용됩니다.",
                )
            f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")

    job.file_path = str(save_path)

    # 백그라운드 처리 시작
    background_tasks.add_task(_process_uploaded_file, job.job_id, save_path)

    return JobResponse(
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        current_step="파일 업로드 완료, 처리 대기 중",
        source_file=file.filename,
        message=f"작업이 생성되었습니다. job_id: {job.job_id}",
    )


async def _process_uploaded_file(job_id: str, file_path: Path):
    """백그라운드에서 오디오 파일 처리"""
    job = _processor.get_job(job_id)
    if not job:
        return

    try:
        from voice.transcriber import Transcriber
        from voice.document_generator import DocumentGenerator

        # 1) 전사
        job._update(ProcessingStatus.TRANSCRIBING, "음성을 텍스트로 변환 중...")
        transcriber = Transcriber()
        job.transcript = transcriber.transcribe(file_path)

        # 2) 문서 생성
        job._update(ProcessingStatus.PROCESSING, "Q&A를 추출하는 중...")
        job._update(ProcessingStatus.GENERATING, "RAG 문서를 생성하는 중...")
        generator = DocumentGenerator()
        job.document = generator.generate(job.transcript)

        # 3) 완료
        job._update(ProcessingStatus.COMPLETE, "처리 완료")

    except Exception as e:
        job.status = ProcessingStatus.FAILED
        job.current_step = "처리 실패"
        job.error_message = str(e)


@router.post("/demo", response_model=JobResponse)
async def run_demo():
    """
    데모 모드 실행.
    오디오 파일이나 API 키 없이 전체 파이프라인을 테스트합니다.
    """
    job = _processor.process_demo()

    return JobResponse(
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        current_step=job.current_step,
        source_file=job.source_file,
        message="데모 처리가 완료되었습니다.",
    )


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """처리 상태 조회"""
    job = _processor.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"작업을 찾을 수 없습니다: {job_id}")

    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress": job.progress,
        "current_step": job.current_step,
        "source_file": job.source_file,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "error_message": job.error_message,
    }


@router.get("/transcript/{job_id}")
async def get_transcript(job_id: str):
    """전사 결과 조회"""
    job = _processor.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"작업을 찾을 수 없습니다: {job_id}")

    if not job.transcript:
        if job.status == ProcessingStatus.FAILED:
            raise HTTPException(
                status_code=400,
                detail=f"처리 실패: {job.error_message}",
            )
        raise HTTPException(
            status_code=202,
            detail=f"아직 처리 중입니다. 현재 상태: {job.current_step}",
        )

    return {
        "job_id": job.job_id,
        "transcript": job.transcript.to_dict(),
        "full_text": job.transcript.full_text,
    }


@router.get("/document/{job_id}")
async def get_document(job_id: str):
    """생성된 RAG 문서 조회"""
    job = _processor.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"작업을 찾을 수 없습니다: {job_id}")

    if not job.document:
        if job.status == ProcessingStatus.FAILED:
            raise HTTPException(
                status_code=400,
                detail=f"처리 실패: {job.error_message}",
            )
        raise HTTPException(
            status_code=202,
            detail=f"아직 처리 중입니다. 현재 상태: {job.current_step}",
        )

    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "document": job.document.to_dict(),
        "preview": job.document.markdown,
    }


@router.post("/document/{job_id}/approve")
async def approve_document(job_id: str, request: ApproveRequest = ApproveRequest()):
    """
    문서 승인 및 지식베이스 저장.
    
    수정된 Q&A 쌍을 포함할 수 있습니다.
    승인 시 ChromaDB 벡터 스토어에 저장됩니다.
    """
    try:
        edited_pairs = None
        if request.qa_pairs:
            edited_pairs = [qa.model_dump() for qa in request.qa_pairs]

        result = _processor.approve_document(
            job_id=job_id,
            edited_qa_pairs=edited_pairs,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def list_jobs():
    """전체 작업 목록 조회 (최신순)"""
    return {
        "jobs": _processor.list_jobs(),
        "total": len(_processor.jobs),
    }


# ── 프로세서 접근 (다른 모듈에서 사용) ────────────────────

def get_processor() -> VoiceProcessor:
    """싱글턴 프로세서 반환"""
    return _processor
