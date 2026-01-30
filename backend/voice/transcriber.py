"""
Speech-to-Text 모듈
- OpenAI Whisper API (온라인) 또는 로컬 whisper 라이브러리 (오프라인)
- 지원 형식: MP3, WAV, M4A, WebM, OGG
- 지원 언어: 한국어(ko), 영어(en)
- 기본 화자 분리: 묵음 구간 기반 턴 감지
"""

from __future__ import annotations

import io
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".webm", ".ogg"}
SUPPORTED_LANGUAGES = {"ko", "en"}


@dataclass
class TranscriptSegment:
    """전사 결과의 개별 세그먼트"""
    speaker: str
    text: str
    start_time: float
    end_time: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TranscriptResult:
    """전사 전체 결과"""
    segments: List[TranscriptSegment] = field(default_factory=list)
    language: str = "ko"
    duration: float = 0.0
    source_file: str = ""
    method: str = "unknown"  # "whisper_api" | "whisper_local" | "demo"

    def to_dict(self) -> dict:
        return {
            "segments": [s.to_dict() for s in self.segments],
            "language": self.language,
            "duration": self.duration,
            "source_file": self.source_file,
            "method": self.method,
            "segment_count": len(self.segments),
        }

    @property
    def full_text(self) -> str:
        """전체 텍스트를 하나의 문자열로 반환"""
        return "\n".join(
            f"[{s.speaker}] {s.text}" for s in self.segments
        )


class Transcriber:
    """
    음성 파일을 텍스트로 변환하는 전사기.
    
    우선순위:
    1. OpenAI Whisper API (API 키가 있을 때)
    2. 로컬 whisper 라이브러리 (openai-whisper 설치 시)
    3. 에러 발생
    """

    def __init__(
        self,
        language: str = "ko",
        model_size: str = "base",
        api_key: Optional[str] = None,
        silence_threshold_ms: int = 1500,
    ):
        """
        Args:
            language: 전사 언어 ("ko" 또는 "en")
            model_size: 로컬 Whisper 모델 크기 ("base", "small", "medium")
            api_key: OpenAI API 키 (None이면 환경변수 또는 로컬 모드)
            silence_threshold_ms: 화자 교체 감지용 묵음 기준 (밀리초)
        """
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"지원하지 않는 언어: {language}. 지원: {SUPPORTED_LANGUAGES}")
        self.language = language
        self.model_size = model_size
        self.silence_threshold_ms = silence_threshold_ms

        # API 키 결정
        self._api_key = api_key
        if self._api_key is None:
            import os
            self._api_key = os.getenv("OPENAI_API_KEY", "")

    def transcribe(self, audio_path: str | Path) -> TranscriptResult:
        """
        오디오 파일을 전사한다.
        
        Args:
            audio_path: 오디오 파일 경로
            
        Returns:
            TranscriptResult: 전사 결과 (세그먼트 리스트 포함)
        """
        audio_path = Path(audio_path)
        self._validate_file(audio_path)

        # 1) OpenAI Whisper API 시도
        if self._api_key:
            try:
                return self._transcribe_api(audio_path)
            except Exception as e:
                print(f"[Whisper API 실패] {e} — 로컬 모드로 전환합니다.")

        # 2) 로컬 whisper 라이브러리 시도
        try:
            return self._transcribe_local(audio_path)
        except ImportError:
            raise RuntimeError(
                "전사 불가: OpenAI API 키가 없고, 로컬 whisper 라이브러리도 "
                "설치되어 있지 않습니다. 다음 중 하나를 실행하세요:\n"
                "  1) OPENAI_API_KEY 환경변수 설정\n"
                "  2) pip install openai-whisper"
            )
        except Exception as e:
            raise RuntimeError(f"로컬 전사 실패: {e}")

    def _validate_file(self, path: Path) -> None:
        """파일 존재 및 형식 검증"""
        if not path.exists():
            raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {path}")
        if path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(
                f"지원하지 않는 형식: {path.suffix}. "
                f"지원 형식: {', '.join(SUPPORTED_FORMATS)}"
            )

    # ── OpenAI Whisper API ─────────────────────────────────

    def _transcribe_api(self, audio_path: Path) -> TranscriptResult:
        """OpenAI Whisper API를 사용한 전사"""
        from openai import OpenAI

        client = OpenAI(api_key=self._api_key)

        # 오디오 파일을 pydub로 변환 (필요 시)
        processed_path = self._ensure_compatible_format(audio_path)

        with open(processed_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=self.language,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        # API 응답 → TranscriptResult
        raw_segments = response.segments if hasattr(response, "segments") else []
        segments = self._assign_speakers(
            [
                {
                    "text": seg.get("text", seg.text if hasattr(seg, "text") else "").strip(),
                    "start": seg.get("start", getattr(seg, "start", 0.0)),
                    "end": seg.get("end", getattr(seg, "end", 0.0)),
                }
                for seg in raw_segments
            ]
        )

        duration = 0.0
        if segments:
            duration = segments[-1].end_time

        return TranscriptResult(
            segments=segments,
            language=self.language,
            duration=duration,
            source_file=audio_path.name,
            method="whisper_api",
        )

    # ── 로컬 Whisper ──────────────────────────────────────

    def _transcribe_local(self, audio_path: Path) -> TranscriptResult:
        """로컬 whisper 라이브러리를 사용한 전사"""
        import whisper  # openai-whisper

        model = whisper.load_model(self.model_size)
        result = model.transcribe(
            str(audio_path),
            language=self.language,
            verbose=False,
        )

        raw_segments = result.get("segments", [])
        segments = self._assign_speakers(
            [
                {
                    "text": seg["text"].strip(),
                    "start": seg["start"],
                    "end": seg["end"],
                }
                for seg in raw_segments
            ]
        )

        duration = 0.0
        if segments:
            duration = segments[-1].end_time

        return TranscriptResult(
            segments=segments,
            language=self.language,
            duration=duration,
            source_file=audio_path.name,
            method="whisper_local",
        )

    # ── 화자 분리 (턴 감지) ────────────────────────────────

    def _assign_speakers(
        self, raw_segments: List[dict]
    ) -> List[TranscriptSegment]:
        """
        묵음 구간 기반으로 화자를 교대 배정.
        silence_threshold_ms 이상의 간격이 있으면 화자가 바뀐 것으로 간주.
        """
        if not raw_segments:
            return []

        threshold_sec = self.silence_threshold_ms / 1000.0
        speakers = ["상담원", "고객"]
        current_speaker_idx = 0
        result: List[TranscriptSegment] = []

        for i, seg in enumerate(raw_segments):
            if i > 0:
                gap = seg["start"] - raw_segments[i - 1]["end"]
                if gap >= threshold_sec:
                    current_speaker_idx = 1 - current_speaker_idx

            result.append(
                TranscriptSegment(
                    speaker=speakers[current_speaker_idx],
                    text=seg["text"],
                    start_time=round(seg["start"], 2),
                    end_time=round(seg["end"], 2),
                )
            )

        return result

    # ── 오디오 변환 헬퍼 ───────────────────────────────────

    def _ensure_compatible_format(self, audio_path: Path) -> Path:
        """
        Whisper API가 처리할 수 있는 형식으로 변환.
        MP3, WAV는 그대로, 나머지는 WAV로 변환.
        """
        if audio_path.suffix.lower() in {".mp3", ".wav", ".m4a"}:
            return audio_path

        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(str(audio_path))
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            audio.export(tmp.name, format="wav")
            return Path(tmp.name)
        except ImportError:
            # pydub 미설치 시 원본 그대로 전달 (API가 처리할 수도 있음)
            return audio_path


# ── 데모용 전사 결과 생성 ──────────────────────────────────

def create_demo_transcript(source_file: str = "demo_audio.mp3") -> TranscriptResult:
    """
    데모용 전사 결과를 생성한다.
    실제 오디오 파일 없이 파이프라인을 테스트할 수 있다.
    """
    segments = [
        TranscriptSegment("상담원", "안녕하세요, 고객센터입니다. 무엇을 도와드릴까요?", 0.0, 3.2),
        TranscriptSegment("고객", "네, 지난주에 주문한 상품이 아직 안 왔어요.", 3.5, 7.1),
        TranscriptSegment("상담원", "불편을 드려 죄송합니다. 주문번호 알려주시겠어요?", 7.8, 11.2),
        TranscriptSegment("고객", "주문번호는 ORD-2024-78532입니다.", 11.8, 14.5),
        TranscriptSegment("상담원", "확인해 보겠습니다. 잠시만 기다려 주세요.", 15.0, 17.8),
        TranscriptSegment("상담원", "확인했습니다. 해당 상품은 현재 배송 중이며, 내일 도착 예정입니다.", 20.0, 25.3),
        TranscriptSegment("고객", "내일이요? 원래 2일 안에 온다고 했는데 벌써 5일이나 지났잖아요.", 25.8, 30.5),
        TranscriptSegment("상담원", "죄송합니다. 물류센터 사정으로 지연되었습니다. 일반배송은 보통 2-3일이지만, 연휴 기간에는 3-5일 소요될 수 있습니다.", 31.0, 38.2),
        TranscriptSegment("고객", "그럼 혹시 반품도 가능한가요?", 38.8, 41.2),
        TranscriptSegment("상담원", "네, 물론입니다. 상품 수령 후 7일 이내에 반품 신청 가능합니다. 앱에서 마이페이지 → 주문내역 → 반품신청으로 진행하시면 됩니다.", 41.8, 50.5),
        TranscriptSegment("고객", "반품 배송비는 어떻게 되나요?", 51.0, 53.5),
        TranscriptSegment("상담원", "단순 변심의 경우 편도 3,000원이 부과되고, 상품 불량이면 무료입니다.", 54.0, 59.8),
        TranscriptSegment("고객", "아, 알겠습니다. 그리고 멤버십 등급은 어떻게 올릴 수 있나요?", 60.5, 65.0),
        TranscriptSegment("상담원", "월 구매금액 기준으로 자동 산정됩니다. 실버는 5만원, 골드는 15만원, VIP는 30만원 이상이면 다음 달부터 적용됩니다.", 65.5, 74.2),
        TranscriptSegment("고객", "VIP가 되면 어떤 혜택이 있나요?", 74.8, 77.5),
        TranscriptSegment("상담원", "VIP 회원은 무료배송, 5% 추가 할인, 전용 상담 채널, 그리고 생일 쿠폰이 제공됩니다.", 78.0, 85.3),
        TranscriptSegment("고객", "오, 괜찮네요. 그러면 일단 배송 오는 거 기다려 볼게요.", 85.8, 90.2),
        TranscriptSegment("상담원", "네, 내일 중으로 도착할 예정이니 조금만 기다려 주세요. 혹시 도착하지 않으면 다시 연락 주시면 바로 처리해 드리겠습니다.", 90.8, 99.5),
        TranscriptSegment("고객", "네, 감사합니다.", 100.0, 101.5),
        TranscriptSegment("상담원", "감사합니다. 좋은 하루 되세요!", 102.0, 104.3),
    ]

    return TranscriptResult(
        segments=segments,
        language="ko",
        duration=104.3,
        source_file=source_file,
        method="demo",
    )
