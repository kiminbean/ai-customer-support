"""
Voice-to-RAG 파이프라인 모듈
음성 파일을 텍스트로 변환하고, 구조화된 지식베이스 문서를 자동 생성한다.

주요 구성:
- transcriber: 음성→텍스트 (STT)
- document_generator: 텍스트→Q&A 문서
- processor: 전체 파이프라인 오케스트레이터
- routes: FastAPI 엔드포인트
- demo: 데모 모드 (API 키/오디오 불필요)
"""

from voice.processor import VoiceProcessor, ProcessingStatus
from voice.transcriber import Transcriber
from voice.document_generator import DocumentGenerator

__all__ = [
    "VoiceProcessor",
    "ProcessingStatus",
    "Transcriber",
    "DocumentGenerator",
]
