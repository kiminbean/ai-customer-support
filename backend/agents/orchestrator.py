"""
메인 오케스트레이터 — 딥 에이전트 패턴
사용자 의도를 분류하고 적절한 서브에이전트에게 라우팅한다.

흐름:
  사용자 입력 → 의도 분류 → 서브에이전트 → 에스컬레이션 체크 → 응답
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from agents import faq_agent, order_agent, escalation_agent

# ── 대화 메모리 (인메모리) ─────────────────────────────────

_MAX_CONVERSATIONS = 1000
_conversations: Dict[str, Dict] = {}


def _get_or_create_conversation(conversation_id: Optional[str] = None) -> Dict:
    """대화 세션을 가져오거나 생성"""
    if conversation_id and conversation_id in _conversations:
        return _conversations[conversation_id]

    conv_id = conversation_id or str(uuid.uuid4())
    if len(_conversations) >= _MAX_CONVERSATIONS:
        oldest_key = next(iter(_conversations))
        del _conversations[oldest_key]
    conv = {
        "id": conv_id,
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "metadata": {},
    }
    _conversations[conv_id] = conv
    return conv


# ── 의도 분류 ──────────────────────────────────────────────

class Intent:
    FAQ = "faq"
    ORDER = "order"
    ESCALATION = "escalation"
    GREETING = "greeting"


def classify_intent(query: str) -> str:
    """
    사용자 쿼리의 의도를 분류.
    - 에스컬레이션 체크 우선 (감정/명시적 요청)
    - 주문 관련 키워드 체크
    - 나머지는 FAQ
    """
    # 1. 에스컬레이션 체크 (최우선)
    if escalation_agent.needs_escalation(query, confidence=1.0):
        return Intent.ESCALATION

    # 2. 인사/간단 대화
    greetings = ["안녕", "hello", "hi", "반가", "처음", "도움"]
    if any(g in query.lower() for g in greetings) and len(query) < 20:
        return Intent.GREETING

    # 3. 주문 관련
    if order_agent.is_order_query(query):
        return Intent.ORDER

    # 4. 기본: FAQ
    return Intent.FAQ


# ── 인사 처리 ──────────────────────────────────────────────

def _handle_greeting(query: str) -> Dict:
    return {
        "answer": (
            "안녕하세요! 😊 AI 고객지원 도우미입니다.\n\n"
            "무엇을 도와드릴까요? 아래와 같은 문의를 처리할 수 있습니다:\n\n"
            "📦 배송/주문 조회\n"
            "🔄 반품/교환/환불\n"
            "❓ 자주 묻는 질문 (FAQ)\n"
            "👤 상담원 연결\n\n"
            "자유롭게 질문해 주세요!"
        ),
        "confidence": 1.0,
        "source_documents": [],
        "agent": "orchestrator",
        "intent": "greeting",
        "mode": "demo",
    }


# ── 메인 오케스트레이터 ───────────────────────────────────

def process_message(
    message: str,
    conversation_id: Optional[str] = None,
) -> Dict:
    """
    메인 처리 함수.
    1) 의도 분류
    2) 서브에이전트 라우팅
    3) 에스컬레이션 체크
    4) 대화 기록 저장
    5) 구조화된 응답 반환
    """
    conv = _get_or_create_conversation(conversation_id)
    conv_id = conv["id"]

    # 1. 의도 분류
    intent = classify_intent(message)

    # 2. 서브에이전트 라우팅
    if intent == Intent.GREETING:
        result = _handle_greeting(message)
    elif intent == Intent.ESCALATION:
        result = escalation_agent.handle(message, conversation_id=conv_id)
    elif intent == Intent.ORDER:
        result = order_agent.handle(message, conversation_id=conv_id)
    else:  # FAQ
        result = faq_agent.handle(message, conversation_id=conv_id)

    # 3. FAQ 응답의 에스컬레이션 재확인
    if intent == Intent.FAQ and result.get("confidence", 1.0) < 0.3:
        result = escalation_agent.handle(
            message, conversation_id=conv_id, confidence=result["confidence"]
        )
        result["intent"] = "escalation_auto"

    # 4. 대화 기록 저장
    conv["messages"].append({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat(),
    })
    conv["messages"].append({
        "role": "assistant",
        "content": result["answer"],
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "agent": result.get("agent", "unknown"),
            "confidence": result.get("confidence", 0),
            "intent": intent,
        },
    })
    conv["updated_at"] = datetime.now().isoformat()

    # 5. 응답 구성
    result["conversation_id"] = conv_id
    result["intent"] = result.get("intent", intent)
    return result


# ── 대화 관리 ──────────────────────────────────────────────

def get_conversation(conversation_id: str) -> Optional[Dict]:
    """대화 이력 조회"""
    return _conversations.get(conversation_id)


def list_conversations() -> List[Dict]:
    """전체 대화 목록"""
    return [
        {
            "id": c["id"],
            "message_count": len(c["messages"]),
            "created_at": c["created_at"],
            "updated_at": c["updated_at"],
            "preview": c["messages"][-1]["content"][:50] if c["messages"] else "",
        }
        for c in _conversations.values()
    ]


def get_analytics() -> Dict:
    """사용 분석 데이터"""
    total_conversations = len(_conversations)
    total_messages = sum(len(c["messages"]) for c in _conversations.values())

    # 에이전트별 통계
    agent_counts: Dict[str, int] = {}
    intent_counts: Dict[str, int] = {}
    for conv in _conversations.values():
        for msg in conv["messages"]:
            if msg["role"] == "assistant":
                meta = msg.get("metadata", {})
                agent = meta.get("agent", "unknown")
                intent = meta.get("intent", "unknown")
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
                intent_counts[intent] = intent_counts.get(intent, 0) + 1

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "agent_distribution": agent_counts,
        "intent_distribution": intent_counts,
        "avg_messages_per_conversation": (
            round(total_messages / total_conversations, 1)
            if total_conversations > 0 else 0
        ),
    }
