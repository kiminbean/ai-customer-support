"""
Tests for voice/processor module
Target: Increase coverage from 50% to 80%+
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from voice.processor import (
    ProcessingStatus,
    VoiceJob,
    VoiceProcessor,
)
from voice.transcriber import TranscriptResult, TranscriptSegment, create_demo_transcript
from voice.document_generator import GeneratedDocument, QAPair


class TestProcessingStatus:
    """ProcessingStatus Enum 테스트"""

    def test_status_values(self):
        """상태 값 확인"""
        assert ProcessingStatus.UPLOADING.value == "UPLOADING"
        assert ProcessingStatus.TRANSCRIBING.value == "TRANSCRIBING"
        assert ProcessingStatus.PROCESSING.value == "PROCESSING"
        assert ProcessingStatus.GENERATING.value == "GENERATING"
        assert ProcessingStatus.COMPLETE.value == "COMPLETE"
        assert ProcessingStatus.FAILED.value == "FAILED"
        assert ProcessingStatus.APPROVED.value == "APPROVED"

    def test_progress_values(self):
        """진행률 값"""
        assert ProcessingStatus.UPLOADING.progress == 10
        assert ProcessingStatus.TRANSCRIBING.progress == 30
        assert ProcessingStatus.PROCESSING.progress == 60
        assert ProcessingStatus.GENERATING.progress == 80
        assert ProcessingStatus.COMPLETE.progress == 100
        assert ProcessingStatus.FAILED.progress == 0
        assert ProcessingStatus.APPROVED.progress == 100

    def test_string_enum(self):
        """문자열 열거형 확인"""
        status = ProcessingStatus.TRANSCRIBING
        assert status == "TRANSCRIBING"
        assert isinstance(status, str)


class TestVoiceJob:
    """VoiceJob 데이터클래스 테스트"""

    def test_creation(self):
        """작업 생성"""
        job = VoiceJob(
            job_id="test-123",
            source_file="audio.mp3",
        )

        assert job.job_id == "test-123"
        assert job.status == ProcessingStatus.UPLOADING
        assert job.progress == 0
        assert job.source_file == "audio.mp3"

    def test_to_dict_basic(self):
        """기본 직렬화"""
        job = VoiceJob(
            job_id="test-123",
            status=ProcessingStatus.TRANSCRIBING,
            progress=30,  # 명시적으로 설정
            current_step="전사 중",
            source_file="audio.mp3",
            created_at="2024-01-01T00:00:00",
        )

        result = job.to_dict()

        assert result["job_id"] == "test-123"
        assert result["status"] == "TRANSCRIBING"
        assert result["progress"] == 30
        assert result["current_step"] == "전사 중"
        assert result["source_file"] == "audio.mp3"

    def test_to_dict_with_transcript(self):
        """전사 결과 포함 직렬화"""
        transcript = TranscriptResult(
            segments=[TranscriptSegment(speaker="A", text="세그먼트", start_time=0.0, end_time=1.0)],
            duration=10.0,
            language="ko",
            method="whisper",
        )

        job = VoiceJob(
            job_id="test-123",
            transcript=transcript,
        )

        result = job.to_dict()

        assert "transcript_summary" in result
        assert result["transcript_summary"]["segment_count"] == 1
        assert result["transcript_summary"]["duration"] == 10.0

    def test_to_dict_with_document(self):
        """문서 포함 직렬화"""
        document = GeneratedDocument(
            markdown="# 문서",
            qa_pairs=[QAPair(question="Q", answer="A")],
            qa_count=1,
            primary_category="테스트",
            confidence=0.9,
            source_file="audio.mp3",
            generated_date="2024-01-01",
        )

        job = VoiceJob(
            job_id="test-123",
            document=document,
        )

        result = job.to_dict()

        assert "document_summary" in result
        assert result["document_summary"]["qa_count"] == 1
        assert result["document_summary"]["primary_category"] == "테스트"

    def test_update(self):
        """상태 업데이트"""
        job = VoiceJob(job_id="test-123")
        job._update(ProcessingStatus.TRANSCRIBING, "전사 중")

        assert job.status == ProcessingStatus.TRANSCRIBING
        assert job.progress == 30
        assert job.current_step == "전사 중"
        assert job.updated_at != ""


class TestVoiceProcessor:
    """VoiceProcessor 클래스 테스트"""

    @pytest.fixture
    def processor(self):
        return VoiceProcessor()

    def test_init(self, processor):
        """초기화"""
        assert processor._jobs == {}
        assert processor._language == "ko"
        assert processor._whisper_model == "base"

    def test_create_job(self, processor):
        """작업 생성"""
        job = processor.create_job("test.mp3")

        assert job.job_id != ""
        assert job.source_file == "test.mp3"
        assert job.status == ProcessingStatus.UPLOADING
        assert job.job_id in processor._jobs

    def test_create_job_with_file_path(self, processor):
        """파일 경로와 함께 작업 생성"""
        job = processor.create_job("test.mp3", file_path="/path/to/test.mp3")

        assert job.file_path == "/path/to/test.mp3"

    def test_get_job(self, processor):
        """작업 조회"""
        created = processor.create_job("test.mp3")
        found = processor.get_job(created.job_id)

        assert found == created

    def test_get_nonexistent_job(self, processor):
        """존재하지 않는 작업 조회"""
        result = processor.get_job("nonexistent")
        assert result is None

    def test_list_jobs(self, processor):
        """작업 목록"""
        job1 = processor.create_job("audio1.mp3")
        job2 = processor.create_job("audio2.mp3")

        jobs = processor.list_jobs()

        assert len(jobs) == 2

    def test_jobs_property(self, processor):
        """jobs 프로퍼티"""
        processor.create_job("test.mp3")
        assert len(processor.jobs) == 1


class TestProcessDemo:
    """process_demo 메서드 테스트"""

    @pytest.fixture
    def processor(self):
        return VoiceProcessor()

    def test_process_demo_success(self, processor):
        """데모 처리 성공"""
        job = processor.process_demo()

        assert job.status == ProcessingStatus.COMPLETE
        assert job.transcript is not None
        assert job.document is not None

    def test_process_demo_transcript_content(self, processor):
        """데모 전사 내용"""
        job = processor.process_demo()

        assert len(job.transcript.segments) > 0
        assert job.transcript.language == "ko"

    def test_process_demo_document_content(self, processor):
        """데모 문서 내용"""
        job = processor.process_demo()

        assert job.document.qa_count > 0
        assert len(job.document.qa_pairs) > 0


class TestProcessDemoAsync:
    """process_demo_async 메서드 테스트"""

    @pytest.fixture
    def processor(self):
        return VoiceProcessor()

    @pytest.mark.asyncio
    async def test_process_demo_async_success(self, processor):
        """비동기 데모 처리 성공"""
        job = await processor.process_demo_async()

        assert job.status == ProcessingStatus.COMPLETE
        assert job.transcript is not None


class TestApproveDocument:
    """approve_document 메서드 테스트"""

    @pytest.fixture
    def processor(self):
        return VoiceProcessor()

    def test_approve_nonexistent_job(self, processor):
        """존재하지 않는 작업 승인"""
        with pytest.raises(ValueError) as exc_info:
            processor.approve_document("nonexistent")

        assert "찾을 수 없습니다" in str(exc_info.value)

    def test_approve_incomplete_job(self, processor):
        """미완료 작업 승인"""
        job = processor.create_job("test.mp3")

        with pytest.raises(ValueError) as exc_info:
            processor.approve_document(job.job_id)

        assert "승인할 수 없는 상태" in str(exc_info.value)

    def test_approve_job_without_document(self, processor):
        """문서 없는 작업 승인"""
        job = processor.create_job("test.mp3")
        job.status = ProcessingStatus.COMPLETE

        with pytest.raises(ValueError) as exc_info:
            processor.approve_document(job.job_id)

        assert "문서가 없습니다" in str(exc_info.value)

    def test_approve_with_edited_qa(self, processor):
        """수정된 Q&A로 승인"""
        job = processor.process_demo()

        edited_qa = [
            {
                "question": "수정된 질문",
                "answer": "수정된 답변",
                "category": "수정",
                "confidence": 0.95,
            }
        ]

        with patch("rag.retriever.add_documents") as mock_add:
            mock_add.return_value = ["doc-1"]

            result = processor.approve_document(job.job_id, edited_qa_pairs=edited_qa)

            assert result["status"] == "approved"
            assert len(job.document.qa_pairs) == 1
            assert job.document.qa_pairs[0].question == "수정된 질문"

    def test_approve_adds_to_vector_db(self, processor):
        """벡터 DB에 추가"""
        job = processor.process_demo()

        with patch("rag.retriever.add_documents") as mock_add:
            mock_add.return_value = ["doc-1", "doc-2"]

            result = processor.approve_document(job.job_id)

            assert result["documents_added"] == 2
            assert job.status == ProcessingStatus.APPROVED


class TestProcessFile:
    """process_file 메서드 테스트"""

    @pytest.fixture
    def processor(self):
        return VoiceProcessor()

    def test_process_file_success(self, processor, tmp_path):
        """파일 처리 성공"""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("fake audio")

        mock_transcript = TranscriptResult(
            segments=[TranscriptSegment(speaker="A", text="텍스트", start_time=0.0, end_time=1.0)],
            duration=1.0,
            language="ko",
            method="demo",
        )

        with patch.object(processor._transcriber, "transcribe") as mock_transcribe:
            with patch.object(processor._generator, "generate") as mock_generate:
                mock_transcribe.return_value = mock_transcript
                mock_generate.return_value = GeneratedDocument(
                    markdown="# 문서",
                    qa_pairs=[],
                    qa_count=0,
                    primary_category="",
                    confidence=0.9,
                    source_file="test.mp3",
                    generated_date="2024-01-01",
                )

                job = processor.process_file(audio_file)

                assert job.status == ProcessingStatus.COMPLETE

    def test_process_file_error(self, processor, tmp_path):
        """파일 처리 에러"""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("fake audio")

        with patch.object(processor._transcriber, "transcribe") as mock_transcribe:
            mock_transcribe.side_effect = Exception("Transcription failed")

            job = processor.process_file(audio_file)

            assert job.status == ProcessingStatus.FAILED
            assert job.error_message == "Transcription failed"


class TestProcessFileAsync:
    """process_file_async 메서드 테스트"""

    @pytest.fixture
    def processor(self):
        return VoiceProcessor()

    @pytest.mark.asyncio
    async def test_process_file_async_success(self, processor, tmp_path):
        """비동기 파일 처리 성공"""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("fake audio")

        mock_transcript = TranscriptResult(
            segments=[],
            duration=1.0,
            language="ko",
            method="demo",
        )

        with patch.object(processor._transcriber, "transcribe") as mock_transcribe:
            with patch.object(processor._generator, "generate") as mock_generate:
                mock_transcribe.return_value = mock_transcript
                mock_generate.return_value = GeneratedDocument(
                    markdown="# 문서",
                    qa_pairs=[],
                    qa_count=0,
                    primary_category="",
                    confidence=0.9,
                    source_file="test.mp3",
                    generated_date="2024-01-01",
                )

                job = await processor.process_file_async(audio_file)

                assert job.status == ProcessingStatus.COMPLETE

    @pytest.mark.asyncio
    async def test_process_file_async_error(self, processor, tmp_path):
        """비동기 파일 처리 에러"""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("fake audio")

        with patch.object(processor._transcriber, "transcribe") as mock_transcribe:
            mock_transcribe.side_effect = Exception("Async error")

            job = await processor.process_file_async(audio_file)

            assert job.status == ProcessingStatus.FAILED
            assert "Async error" in job.error_message


class TestVoiceJobStateTransitions:
    """작업 상태 전이 테스트"""

    @pytest.fixture
    def processor(self):
        return VoiceProcessor()

    def test_state_sequence(self, processor):
        """상태 전이 순서"""
        job = processor.create_job("test.mp3")

        assert job.status == ProcessingStatus.UPLOADING

        job._update(ProcessingStatus.TRANSCRIBING, "전사 중")
        assert job.status == ProcessingStatus.TRANSCRIBING

        job._update(ProcessingStatus.PROCESSING, "처리 중")
        assert job.status == ProcessingStatus.PROCESSING

        job._update(ProcessingStatus.GENERATING, "생성 중")
        assert job.status == ProcessingStatus.GENERATING

        job._update(ProcessingStatus.COMPLETE, "완료")
        assert job.status == ProcessingStatus.COMPLETE
