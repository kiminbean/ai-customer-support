"""
데이터 허브 프로세서 — 다운로드된 데이터셋을 RAG 호환 문서로 변환

다양한 데이터 포맷(대화, Q&A, 의도-응답, 티켓, 트윗)을 처리하여
구조화된 마크다운 문서를 생성한다.
중복 제거, 배치 처리, 번역 파이프라인을 포함.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

import config
from datahub.downloader import get_downloaded_data
from datahub.registry import get_dataset_info

# ── 상수 ───────────────────────────────────────────────────

PROCESSED_DIR = config.DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ── Q&A 쌍 데이터 클래스 ──────────────────────────────────


class QAPair:
    """RAG용 질문-답변 쌍"""

    def __init__(
        self,
        question: str,
        answer: str,
        category: str = "",
        source_format: str = "",
        metadata: Optional[Dict] = None,
    ):
        self.question = question
        self.answer = answer
        self.category = category
        self.source_format = source_format
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        return {
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "source_format": self.source_format,
            "metadata": self.metadata,
        }

    def fingerprint(self) -> str:
        """중복 검사용 해시값 생성"""
        text = (self.question + self.answer).lower().strip()
        return hashlib.md5(text.encode("utf-8")).hexdigest()


# ── 포맷별 프로세서 ────────────────────────────────────────


def _process_conversation(records: List[Dict]) -> List[QAPair]:
    """
    대화 포맷 처리: 고객-상담원 대화에서 Q&A 쌍을 추출한다.

    기대 필드: customer/user/input + agent/assistant/output
    """
    pairs: List[QAPair] = []

    # 가능한 필드명 매핑
    question_keys = ["customer", "user", "input", "question", "instruction", "text", "message"]
    answer_keys = ["agent", "assistant", "output", "answer", "response", "reply"]
    category_keys = ["category", "topic", "intent", "label", "tag"]

    for record in records:
        question = _extract_field(record, question_keys)
        answer = _extract_field(record, answer_keys)
        category = _extract_field(record, category_keys)

        if question and answer:
            pairs.append(QAPair(
                question=question.strip(),
                answer=answer.strip(),
                category=category or "일반",
                source_format="conversation",
                metadata={"original_keys": list(record.keys())},
            ))

        # 멀티턴 대화 처리: 'conversation' 또는 'messages' 키
        conv_field = record.get("conversation") or record.get("messages") or record.get("dialogue")
        if conv_field and isinstance(conv_field, (list, str)):
            sub_pairs = _extract_from_dialogue(conv_field)
            pairs.extend(sub_pairs)

    return pairs


def _extract_from_dialogue(dialogue: Any) -> List[QAPair]:
    """멀티턴 대화에서 Q&A 쌍을 추출한다."""
    pairs: List[QAPair] = []

    # 문자열인 경우 줄바꿈으로 분리
    if isinstance(dialogue, str):
        lines = [l.strip() for l in dialogue.split("\n") if l.strip()]
        for i in range(0, len(lines) - 1, 2):
            q = lines[i].lstrip("Customer:").lstrip("User:").strip()
            a = lines[i + 1].lstrip("Agent:").lstrip("Assistant:").strip()
            if q and a:
                pairs.append(QAPair(
                    question=q,
                    answer=a,
                    category="대화",
                    source_format="conversation_turn",
                ))

    # 리스트인 경우 (역할 기반)
    elif isinstance(dialogue, list):
        # [{role: "user", content: "..."}, {role: "assistant", content: "..."}]
        user_msgs: List[str] = []
        for turn in dialogue:
            if isinstance(turn, dict):
                role = turn.get("role", "").lower()
                content = turn.get("content", "") or turn.get("text", "")
                if role in ("user", "customer", "human"):
                    user_msgs.append(content)
                elif role in ("assistant", "agent", "bot") and user_msgs:
                    q = user_msgs.pop(0)
                    pairs.append(QAPair(
                        question=q,
                        answer=content,
                        category="대화",
                        source_format="conversation_turn",
                    ))

    return pairs


def _process_qa(records: List[Dict]) -> List[QAPair]:
    """
    Q&A 포맷 처리: 직접적인 질문-답변 쌍.
    """
    pairs: List[QAPair] = []
    question_keys = ["question", "query", "input", "instruction", "text"]
    answer_keys = ["answer", "response", "output", "reply", "context"]
    category_keys = ["category", "topic", "label", "intent"]

    for record in records:
        question = _extract_field(record, question_keys)
        answer = _extract_field(record, answer_keys)
        category = _extract_field(record, category_keys)

        if question and answer:
            pairs.append(QAPair(
                question=question.strip(),
                answer=answer.strip(),
                category=category or "FAQ",
                source_format="qa",
            ))

    return pairs


def _process_intent_response(records: List[Dict]) -> List[QAPair]:
    """
    의도-응답 포맷 처리: 의도 분류 기반 Q&A.
    """
    pairs: List[QAPair] = []

    for record in records:
        intent = record.get("intent", "") or record.get("category", "")
        instruction = (
            record.get("instruction", "")
            or record.get("input", "")
            or record.get("text", "")
            or record.get("utterance", "")
        )
        response = (
            record.get("response", "")
            or record.get("output", "")
            or record.get("answer", "")
        )

        if instruction and response:
            pairs.append(QAPair(
                question=instruction.strip(),
                answer=response.strip(),
                category=intent or "의도 기반",
                source_format="intent-response",
                metadata={"intent": intent},
            ))

    return pairs


def _process_ticket(records: List[Dict]) -> List[QAPair]:
    """
    티켓 포맷 처리: 문제-해결 쌍 추출.
    """
    pairs: List[QAPair] = []

    for record in records:
        subject = record.get("subject", "") or record.get("title", "")
        description = record.get("description", "") or record.get("body", "") or record.get("text", "")
        resolution = (
            record.get("resolution", "")
            or record.get("solution", "")
            or record.get("response", "")
            or record.get("answer", "")
        )
        priority = record.get("priority", "")
        category = record.get("category", "") or record.get("type", "")

        # 제목 + 설명을 질문으로
        question_parts = [p for p in [subject, description] if p]
        question = " — ".join(question_parts) if question_parts else ""

        if question and resolution:
            pairs.append(QAPair(
                question=question.strip(),
                answer=resolution.strip(),
                category=category or "티켓",
                source_format="ticket",
                metadata={"priority": priority, "subject": subject},
            ))

    return pairs


def _process_tweet(records: List[Dict]) -> List[QAPair]:
    """
    트윗 포맷 처리: 고객 트윗-지원 응답 쌍 추출.
    """
    pairs: List[QAPair] = []

    customer_keys = ["customer_tweet", "tweet", "text", "inbound", "input", "message"]
    reply_keys = ["support_reply", "reply", "response", "outbound", "output", "answer"]
    category_keys = ["category", "topic", "label"]

    for record in records:
        tweet = _extract_field(record, customer_keys)
        reply = _extract_field(record, reply_keys)
        category = _extract_field(record, category_keys)

        if tweet and reply:
            # @멘션 정리
            clean_tweet = _clean_tweet(tweet)
            clean_reply = _clean_tweet(reply)

            if clean_tweet and clean_reply:
                pairs.append(QAPair(
                    question=clean_tweet,
                    answer=clean_reply,
                    category=category or "SNS",
                    source_format="tweet",
                ))

    return pairs


# ── 유틸리티 ───────────────────────────────────────────────


def _extract_field(record: Dict, possible_keys: List[str]) -> str:
    """여러 가능한 키에서 값을 추출한다."""
    for key in possible_keys:
        value = record.get(key)
        if value and isinstance(value, str) and value.strip():
            return value
    return ""


def _clean_tweet(text: str) -> str:
    """트윗 텍스트에서 @멘션을 제거한다."""
    import re
    text = re.sub(r"@\w+", "", text).strip()
    return text


def _deduplicate(pairs: List[QAPair]) -> List[QAPair]:
    """중복 Q&A 쌍을 제거한다."""
    seen: set = set()
    unique: List[QAPair] = []

    for pair in pairs:
        fp = pair.fingerprint()
        if fp not in seen:
            seen.add(fp)
            unique.append(pair)

    return unique


# ── 메인 프로세서 ─────────────────────────────────────────

# 포맷별 프로세서 매핑
FORMAT_PROCESSORS = {
    "conversation": _process_conversation,
    "qa": _process_qa,
    "intent-response": _process_intent_response,
    "ticket": _process_ticket,
    "tweet": _process_tweet,
    "audio+text": _process_conversation,  # 텍스트 부분만 처리
}


def process_dataset(
    dataset_id: str,
    translate: bool = False,
    max_entries: Optional[int] = None,
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> Dict[str, Any]:
    """
    다운로드된 데이터셋을 RAG 호환 문서로 변환한다.

    Args:
        dataset_id: 데이터셋 ID
        translate: 한국어 번역 여부
        max_entries: 최대 처리 항목 수 (None이면 전체)
        progress_callback: 진행 상태 콜백

    Returns:
        {
            "status": "completed" | "failed",
            "dataset_id": str,
            "qa_pairs": int,        # 추출된 Q&A 쌍 수
            "deduplicated": int,    # 중복 제거 후 수
            "output_path": str,     # 처리된 파일 경로
            "markdown_path": str,   # 마크다운 문서 경로
            "error": str | None,
        }
    """
    if progress_callback:
        progress_callback("데이터 로딩 중...", 0.1)

    # 데이터셋 정보 조회
    ds_info = get_dataset_info(dataset_id)
    if not ds_info:
        return {
            "status": "failed",
            "dataset_id": dataset_id,
            "error": f"레지스트리에서 데이터셋을 찾을 수 없습니다: {dataset_id}",
        }

    # 다운로드된 데이터 로드
    raw_data = get_downloaded_data(dataset_id)
    if not raw_data:
        return {
            "status": "failed",
            "dataset_id": dataset_id,
            "error": "다운로드된 데이터를 찾을 수 없습니다. 먼저 다운로드하세요.",
        }

    data_format = ds_info.get("format", "qa")
    domain = ds_info.get("domain", "알 수 없음")
    ds_name = ds_info.get("name", dataset_id)

    if progress_callback:
        progress_callback(f"'{data_format}' 포맷 처리 중... (총 {len(raw_data)}건)", 0.3)

    # 최대 항목 수 제한
    if max_entries and len(raw_data) > max_entries:
        raw_data = raw_data[:max_entries]

    # 포맷별 프로세서 실행
    processor = FORMAT_PROCESSORS.get(data_format, _process_qa)
    qa_pairs = processor(raw_data)

    if progress_callback:
        progress_callback(f"Q&A 쌍 {len(qa_pairs)}개 추출 완료, 중복 제거 중...", 0.6)

    # 중복 제거
    original_count = len(qa_pairs)
    qa_pairs = _deduplicate(qa_pairs)
    dedup_count = len(qa_pairs)

    if progress_callback:
        progress_callback(
            f"중복 제거: {original_count} → {dedup_count}개 ({original_count - dedup_count}개 제거)",
            0.7,
        )

    # 번역 처리
    if translate:
        if progress_callback:
            progress_callback("번역 처리 중...", 0.8)
        qa_pairs = _translate_pairs(qa_pairs)

    # 결과 저장
    if progress_callback:
        progress_callback("결과 저장 중...", 0.9)

    safe_name = dataset_id.replace("/", "__")
    output_dir = PROCESSED_DIR / safe_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON 저장
    json_path = output_dir / "qa_pairs.json"
    json_data = [pair.to_dict() for pair in qa_pairs]
    json_path.write_text(
        json.dumps(json_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 마크다운 RAG 문서 생성
    markdown_path = output_dir / "rag_document.md"
    markdown_content = _generate_markdown(
        qa_pairs=qa_pairs,
        domain=domain,
        ds_name=ds_name,
        dataset_id=dataset_id,
    )
    markdown_path.write_text(markdown_content, encoding="utf-8")

    # 처리 메타데이터 저장
    meta = {
        "dataset_id": dataset_id,
        "domain": domain,
        "format": data_format,
        "raw_records": len(raw_data),
        "qa_pairs_extracted": original_count,
        "qa_pairs_deduplicated": dedup_count,
        "translated": translate,
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (output_dir / "process_metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if progress_callback:
        progress_callback("처리 완료!", 1.0)

    return {
        "status": "completed",
        "dataset_id": dataset_id,
        "domain": domain,
        "qa_pairs": original_count,
        "deduplicated": dedup_count,
        "output_path": str(output_dir),
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "error": None,
    }


def _translate_pairs(pairs: List[QAPair]) -> List[QAPair]:
    """
    Q&A 쌍을 한국어로 번역한다.
    translator 모듈이 사용 가능하면 실제 번역, 아니면 데모 마킹.
    """
    try:
        from datahub.translator import translate_batch

        qa_dicts = [p.to_dict() for p in pairs]
        translated = translate_batch(qa_dicts)

        result = []
        for t_dict in translated:
            result.append(QAPair(
                question=t_dict["question"],
                answer=t_dict["answer"],
                category=t_dict.get("category", ""),
                source_format=t_dict.get("source_format", ""),
                metadata=t_dict.get("metadata", {}),
            ))
        return result
    except Exception as e:
        logger.warning("번역 실패, 원본 반환: %s", e)
        return pairs


def _generate_markdown(
    qa_pairs: List[QAPair],
    domain: str,
    ds_name: str,
    dataset_id: str,
) -> str:
    """RAG용 구조화된 마크다운 문서를 생성한다."""
    lines: List[str] = []

    lines.append(f"# {domain} — {ds_name}")
    lines.append(f"출처: HuggingFace/{dataset_id}")
    lines.append(f"총 Q&A: {len(qa_pairs)}개")
    lines.append(f"생성일: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for idx, pair in enumerate(qa_pairs, 1):
        lines.append(f"## Q&A {idx}")
        if pair.category:
            lines.append(f"**카테고리:** {pair.category}")
        lines.append(f"**질문:** {pair.question}")
        lines.append(f"**답변:** {pair.answer}")
        lines.append("")

    return "\n".join(lines)


# ── 처리된 데이터 조회 ────────────────────────────────────


def get_processed_data(dataset_id: str) -> Optional[List[Dict]]:
    """처리된 Q&A 데이터를 로드한다."""
    safe_name = dataset_id.replace("/", "__")
    json_path = PROCESSED_DIR / safe_name / "qa_pairs.json"
    if json_path.exists():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("처리된 데이터 로드 실패 (%s): %s", dataset_id, e)
            return None
    return None


def get_process_metadata(dataset_id: str) -> Optional[Dict]:
    """처리 메타데이터를 로드한다."""
    safe_name = dataset_id.replace("/", "__")
    meta_path = PROCESSED_DIR / safe_name / "process_metadata.json"
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("메타데이터 로드 실패 (%s): %s", dataset_id, e)
            return None
    return None
