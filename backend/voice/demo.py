#!/usr/bin/env python3
"""
Voice-to-RAG 데모

실제 오디오 파일이나 API 키 없이 전체 파이프라인을 시연합니다.

실행:
    cd /Users/ibkim/clawd/ai-customer-support/backend
    python -m voice.demo
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def run_demo():
    """데모 파이프라인 실행"""
    from voice.processor import VoiceProcessor

    print("=" * 60)
    print("🎙️  Voice-to-RAG 데모")
    print("   음성 → 텍스트 → 지식베이스 자동 변환")
    print("=" * 60)
    print()

    # ── 1) 파이프라인 초기화 ───────────────────────────────
    processor = VoiceProcessor()
    print("✅ 파이프라인 초기화 완료")
    print()

    # ── 2) 데모 처리 실행 ──────────────────────────────────
    print("🔄 데모 데이터로 파이프라인 실행 중...")
    job = processor.process_demo()
    print(f"   작업 ID: {job.job_id}")
    print(f"   상태: {job.status.value}")
    print(f"   진행률: {job.progress}%")
    print()

    # ── 3) 전사 결과 출력 ──────────────────────────────────
    if job.transcript:
        print("📝 전사 결과:")
        print(f"   방식: {job.transcript.method}")
        print(f"   언어: {job.transcript.language}")
        print(f"   길이: {job.transcript.duration}초")
        print(f"   세그먼트: {len(job.transcript.segments)}개")
        print()
        print("   ─── 대화 내용 (처음 5개 세그먼트) ───")
        for seg in job.transcript.segments[:5]:
            print(f"   [{seg.start_time:6.1f}s] {seg.speaker}: {seg.text}")
        if len(job.transcript.segments) > 5:
            print(f"   ... 외 {len(job.transcript.segments) - 5}개 세그먼트")
        print()

    # ── 4) 생성된 RAG 문서 출력 ────────────────────────────
    if job.document:
        print("📄 생성된 RAG 문서:")
        print(f"   카테고리: {job.document.primary_category}")
        print(f"   Q&A 쌍: {job.document.qa_count}개")
        print(f"   신뢰도: {job.document.confidence:.0%}")
        print()
        print("   ─── Q&A 목록 ───")
        for i, qa in enumerate(job.document.qa_pairs, 1):
            print(f"   [{qa.category}] Q{i}: {qa.question}")
            print(f"           A{i}: {qa.answer[:60]}{'...' if len(qa.answer) > 60 else ''}")
            print()

        print("   ─── 마크다운 문서 미리보기 ───")
        print()
        for line in job.document.markdown.split("\n"):
            print(f"   {line}")
        print()

    # ── 5) 작업 요약 ──────────────────────────────────────
    print("=" * 60)
    print("📊 처리 결과 요약:")
    print(f"   • 작업 ID: {job.job_id}")
    print(f"   • 상태: {job.status.value}")
    print(f"   • 원본: {job.source_file}")
    if job.document:
        print(f"   • 추출된 Q&A: {job.document.qa_count}개")
        print(f"   • 주요 카테고리: {job.document.primary_category}")
        print(f"   • 평균 신뢰도: {job.document.confidence:.0%}")
    print()
    print("💡 다음 단계:")
    print("   • POST /api/voice/demo           → API로 데모 실행")
    print("   • POST /api/voice/upload          → 실제 오디오 업로드")
    print(f"   • POST /api/voice/document/{job.job_id}/approve → 지식베이스에 추가")
    print("=" * 60)

    return job


def run_demo_with_sample_data():
    """샘플 전사 데이터(JSON)를 사용한 데모"""
    from voice.transcriber import TranscriptResult, TranscriptSegment
    from voice.document_generator import DocumentGenerator

    sample_path = Path(__file__).resolve().parent.parent / "data" / "sample_transcripts" / "전화상담_예시.json"

    if not sample_path.exists():
        print(f"⚠️  샘플 파일을 찾을 수 없습니다: {sample_path}")
        print("   기본 데모를 실행합니다.")
        return run_demo()

    print("=" * 60)
    print("🎙️  Voice-to-RAG 데모 (샘플 데이터)")
    print("=" * 60)
    print()

    # JSON 로드
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # TranscriptResult 생성
    segments = [
        TranscriptSegment(
            speaker=seg["speaker"],
            text=seg["text"],
            start_time=seg["start_time"],
            end_time=seg["end_time"],
        )
        for seg in data["segments"]
    ]

    transcript = TranscriptResult(
        segments=segments,
        language=data.get("language", "ko"),
        duration=data.get("duration", 0),
        source_file=data.get("source_file", "sample.mp3"),
        method="sample_data",
    )

    print(f"📝 샘플 전사 데이터 로드: {len(segments)}개 세그먼트")
    print()

    # 문서 생성
    generator = DocumentGenerator()
    document = generator.generate(transcript)

    print(f"📄 생성된 문서:")
    print(f"   카테고리: {document.primary_category}")
    print(f"   Q&A: {document.qa_count}개")
    print()

    for line in document.markdown.split("\n"):
        print(f"   {line}")

    print()
    print("=" * 60)
    return document


if __name__ == "__main__":
    if "--sample" in sys.argv:
        run_demo_with_sample_data()
    else:
        run_demo()
