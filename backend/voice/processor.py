"""
Voice-to-RAG 전체 파이프라인 오케스트레이터

파이프라인: 오디오 파일 → 전사 → Q&A 추출 → 문서 생성 → 벡터 DB 저장
상태 추적: UPLOADING → TRANSCRIBING → PROCESSING → GENERATING → COMPLETE
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from voice.transcriber import Transcriber, TranscriptResult, create_demo_transcript
from voice.document_generator import DocumentGenerator, GeneratedDocument, QAPair


class ProcessingStatus(str, Enum):
    """처리 상태"""
    UPLOADING = "UPLOADING"
    TRANSCRIBING = "TRANSCRIBING"
    PROCESSING = "PROCESSING"
    GENERATING = "GENERATING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    APPROVED = "APPROVED"

    @property
    def progress(self) -> int:
        """상태별 진행률 (%)"""
        return {
            "UPLOADING": 10,
            "TRANSCRIBING": 30,
            "PROCESSING": 60,
            "GENERATING": 80,
            "COMPLETE": 100,
            "FAILED": 0,
            "APPROVED": 100,
        }.get(self.value, 0)


@dataclass
class VoiceJob:
    """음성 처리 작업"""
    job_id: str
    status: ProcessingStatus = ProcessingStatus.UPLOADING
    progress: int = 0
    current_step: str = "대기 중"
    source_file: str = ""
    file_path: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    error_message: Optional[str] = None
    transcript: Optional[TranscriptResult] = None
    document: Optional[GeneratedDocument] = None

    def to_dict(self) -> dict:
        """직렬화 (API 응답용)"""
        result = {
            "job_id": self.job_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "source_file": self.source_file,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error_message": self.error_message,
        }
        if self.transcript:
            result["transcript_summary"] = {
                "segment_count": len(self.transcript.segments),
                "duration": self.transcript.duration,
                "language": self.transcript.language,
                "method": self.transcript.method,
            }
        if self.document:
            result["document_summary"] = {
                "qa_count": self.document.qa_count,
                "primary_category": self.document.primary_category,
                "confidence": self.document.confidence,
            }
        return result

    def _update(self, status: ProcessingStatus, step: str) -> None:
        self.status = status
        self.progress = status.progress
        self.current_step = step
        self.updated_at = datetime.now().isoformat()


class VoiceProcessor:
    """
    Voice-to-RAG 파이프라인 오케스트레이터.
    
    작업을 생성하고, 비동기적으로 처리하며, 상태를 추적한다.
    """

    def __init__(
        self,
        upload_dir: Optional[Path] = None,
        language: str = "ko",
        whisper_model: str = "base",
    ):
        self._jobs: Dict[str, VoiceJob] = {}
        self._upload_dir = upload_dir
        self._language = language
        self._whisper_model = whisper_model
        self._transcriber = Transcriber(
            language=language,
            model_size=whisper_model,
        )
        self._generator = DocumentGenerator()

    # ── 작업 관리 ──────────────────────────────────────────

    @property
    def jobs(self) -> Dict[str, VoiceJob]:
        return self._jobs

    def get_job(self, job_id: str) -> Optional[VoiceJob]:
        return self._jobs.get(job_id)

    def list_jobs(self) -> List[dict]:
        """모든 작업 목록 반환 (최신순)"""
        sorted_jobs = sorted(
            self._jobs.values(),
            key=lambda j: j.created_at,
            reverse=True,
        )
        return [j.to_dict() for j in sorted_jobs]

    def create_job(self, source_file: str, file_path: Optional[str] = None) -> VoiceJob:
        """새 처리 작업 생성"""
        job_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        job = VoiceJob(
            job_id=job_id,
            source_file=source_file,
            file_path=file_path,
            created_at=now,
            updated_at=now,
        )
        self._jobs[job_id] = job
        return job

    # ── 동기 처리 ──────────────────────────────────────────

    def process_file(self, file_path: str | Path) -> VoiceJob:
        """
        오디오 파일을 동기적으로 처리.
        테스트, CLI, 단순 사용에 적합.
        """
        file_path = Path(file_path)
        job = self.create_job(
            source_file=file_path.name,
            file_path=str(file_path),
        )

        try:
            # 1) 전사
            job._update(ProcessingStatus.TRANSCRIBING, "음성을 텍스트로 변환 중...")
            job.transcript = self._transcriber.transcribe(file_path)

            # 2) Q&A 추출 + 문서 생성
            job._update(ProcessingStatus.PROCESSING, "Q&A를 추출하는 중...")
            job._update(ProcessingStatus.GENERATING, "RAG 문서를 생성하는 중...")
            job.document = self._generator.generate(job.transcript)

            # 3) 완료
            job._update(ProcessingStatus.COMPLETE, "처리 완료")

        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.current_step = "처리 실패"
            job.error_message = str(e)
            job.updated_at = datetime.now().isoformat()

        return job

    def process_demo(self) -> VoiceJob:
        """
        데모 모드: 미리 작성된 전사 결과로 파이프라인 실행.
        오디오 파일이나 API 키 없이 전체 흐름을 테스트할 수 있다.
        """
        job = self.create_job(source_file="demo_audio.mp3")

        try:
            # 1) 데모 전사 결과
            job._update(ProcessingStatus.TRANSCRIBING, "데모 전사 데이터 로딩 중...")
            job.transcript = create_demo_transcript()

            # 2) Q&A 추출 + 문서 생성
            job._update(ProcessingStatus.PROCESSING, "Q&A를 추출하는 중...")
            job._update(ProcessingStatus.GENERATING, "RAG 문서를 생성하는 중...")
            job.document = self._generator.generate(job.transcript)

            # 3) 완료
            job._update(ProcessingStatus.COMPLETE, "처리 완료 (데모 모드)")

        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.current_step = "처리 실패"
            job.error_message = str(e)
            job.updated_at = datetime.now().isoformat()

        return job

    # ── 비동기 처리 ────────────────────────────────────────

    async def process_file_async(self, file_path: str | Path) -> VoiceJob:
        """
        오디오 파일을 비동기적으로 처리.
        FastAPI 라우트에서 백그라운드 태스크로 사용.
        """
        file_path = Path(file_path)
        job = self.create_job(
            source_file=file_path.name,
            file_path=str(file_path),
        )

        try:
            # 1) 전사 (CPU-bound → run_in_executor)
            job._update(ProcessingStatus.TRANSCRIBING, "음성을 텍스트로 변환 중...")
            loop = asyncio.get_event_loop()
            job.transcript = await loop.run_in_executor(
                None, self._transcriber.transcribe, file_path
            )

            # 2) Q&A 추출 + 문서 생성
            job._update(ProcessingStatus.PROCESSING, "Q&A를 추출하는 중...")
            await asyncio.sleep(0)  # yield control
            job._update(ProcessingStatus.GENERATING, "RAG 문서를 생성하는 중...")
            job.document = await loop.run_in_executor(
                None, self._generator.generate, job.transcript
            )

            # 3) 완료
            job._update(ProcessingStatus.COMPLETE, "처리 완료")

        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.current_step = "처리 실패"
            job.error_message = str(e)
            job.updated_at = datetime.now().isoformat()

        return job

    async def process_demo_async(self) -> VoiceJob:
        """데모 모드 비동기 처리"""
        job = self.create_job(source_file="demo_audio.mp3")

        try:
            job._update(ProcessingStatus.TRANSCRIBING, "데모 전사 데이터 로딩 중...")
            await asyncio.sleep(0.1)  # 비동기 시뮬레이션
            job.transcript = create_demo_transcript()

            job._update(ProcessingStatus.PROCESSING, "Q&A를 추출하는 중...")
            await asyncio.sleep(0.1)
            job._update(ProcessingStatus.GENERATING, "RAG 문서를 생성하는 중...")
            loop = asyncio.get_event_loop()
            job.document = await loop.run_in_executor(
                None, self._generator.generate, job.transcript
            )

            job._update(ProcessingStatus.COMPLETE, "처리 완료 (데모 모드)")

        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.current_step = "처리 실패"
            job.error_message = str(e)
            job.updated_at = datetime.now().isoformat()

        return job

    # ── 벡터 DB 저장 (승인 시) ─────────────────────────────

    def approve_document(
        self,
        job_id: str,
        edited_qa_pairs: Optional[List[dict]] = None,
    ) -> dict:
        """
        생성된 문서를 승인하고 벡터 DB에 저장.
        
        Args:
            job_id: 작업 ID
            edited_qa_pairs: 사용자가 수정한 Q&A 쌍 (없으면 원본 사용)
            
        Returns:
            저장 결과 딕셔너리
        """
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"작업을 찾을 수 없습니다: {job_id}")
        if job.status not in (ProcessingStatus.COMPLETE, ProcessingStatus.APPROVED):
            raise ValueError(f"승인할 수 없는 상태입니다: {job.status.value}")
        if not job.document:
            raise ValueError("생성된 문서가 없습니다.")

        # 수정된 Q&A 적용
        if edited_qa_pairs:
            job.document.qa_pairs = [
                QAPair(
                    question=qa.get("question", ""),
                    answer=qa.get("answer", ""),
                    category=qa.get("category", "기타"),
                    confidence=qa.get("confidence", 0.8),
                )
                for qa in edited_qa_pairs
            ]
            job.document.qa_count = len(job.document.qa_pairs)
            # 마크다운 재생성
            gen = DocumentGenerator()
            job.document.markdown = gen._build_markdown(
                qa_pairs=job.document.qa_pairs,
                category=job.document.primary_category,
                source_file=job.document.source_file,
                date_str=job.document.generated_date,
            )

        # ChromaDB에 저장
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from rag.retriever import add_documents

            texts: List[str] = []
            metadatas: List[dict] = []

            for i, qa in enumerate(job.document.qa_pairs):
                # Q&A를 검색 가능한 텍스트로 변환
                text = f"질문: {qa.question}\n답변: {qa.answer}"
                texts.append(text)
                metadatas.append({
                    "source": f"voice_{job.source_file}",
                    "doc_type": "voice_qa",
                    "category": qa.category,
                    "qa_index": i,
                    "job_id": job.job_id,
                    "generated_date": job.document.generated_date,
                })

            doc_ids = add_documents(texts=texts, metadatas=metadatas)

            job._update(ProcessingStatus.APPROVED, "지식베이스에 저장 완료")

            return {
                "status": "approved",
                "job_id": job_id,
                "documents_added": len(doc_ids),
                "document_ids": doc_ids,
                "category": job.document.primary_category,
                "message": f"{len(doc_ids)}개의 Q&A가 지식베이스에 추가되었습니다.",
            }

        except Exception as e:
            raise RuntimeError(f"벡터 DB 저장 실패: {e}")
