"""
에스컬레이션 에이전트 — 상담원 연결 판단 및 처리
- 낮은 신뢰도 응답
- 부정적 감정 감지
- 복잡한 문의
- 고객의 명시적 요청
"""

from __future__ import annotations

import re
from typing import Dict, Optional

# ── 에스컬레이션 트리거 키워드 ─────────────────────────────

_ANGRY_KEYWORDS = [
    "화나", "짜증", "열받", "미친", "어이없", "황당",
    "사기", "고소", "신고", "소비자원", "소보원",
    "불만", "항의", "클레임", "최악", "실망",
    "책임자", "매니저", "팀장", "대표",
]

_EXPLICIT_ESCALATION = [
    "상담원", "상담사", "사람", "직원", "전화",
    "연결", "통화", "콜센터", "고객센터",
    "담당자", "책임자",
]

_COMPLEX_KEYWORDS = [
    "법적", "변호사", "소송", "피해보상", "손해배상",
    "개인정보", "유출", "해킹", "부정결제",
    "대량주문", "도매", "계약", "제휴",
]


def needs_escalation(query: str, confidence: float = 1.0) -> bool:
    """에스컬레이션 필요 여부 판단"""
    query_lower = query.lower()

    # 1. 명시적 상담원 요청
    if any(kw in query_lower for kw in _EXPLICIT_ESCALATION):
        return True

    # 2. 부정적 감정
    if any(kw in query_lower for kw in _ANGRY_KEYWORDS):
        return True

    # 3. 복잡한 문의
    if any(kw in query_lower for kw in _COMPLEX_KEYWORDS):
        return True

    # 4. 낮은 신뢰도
    if confidence < 0.3:
        return True

    return False


def get_escalation_reason(query: str, confidence: float = 1.0) -> str:
    """에스컬레이션 사유 분류"""
    query_lower = query.lower()

    if any(kw in query_lower for kw in _EXPLICIT_ESCALATION):
        return "고객 요청"
    if any(kw in query_lower for kw in _ANGRY_KEYWORDS):
        return "부정적 감정 감지"
    if any(kw in query_lower for kw in _COMPLEX_KEYWORDS):
        return "복잡한 문의"
    if confidence < 0.3:
        return "낮은 응답 신뢰도"
    return "기타"


# ── 에스컬레이션 핸들러 ────────────────────────────────────

def handle(query: str, conversation_id: Optional[str] = None, confidence: float = 0.0) -> Dict:
    """
    에스컬레이션 처리.
    상담원 연결 안내 메시지를 반환한다.
    """
    reason = get_escalation_reason(query, confidence)

    # 사유별 맞춤 메시지
    if reason == "고객 요청":
        message = (
            "👤 상담원 연결을 요청하셨습니다.\n\n"
            "고객센터 운영시간:\n"
            "• 평일: 09:00 ~ 18:00\n"
            "• 토요일: 09:00 ~ 13:00\n"
            "• 일요일/공휴일: 휴무\n\n"
            "📞 전화: 1588-0000\n"
            "💬 카카오톡: @쇼핑몰고객센터\n"
            "📧 이메일: support@shop.example.com\n\n"
            "현재 대기 중인 상담 요청이 등록되었습니다. "
            "영업시간 내 순차적으로 연락드리겠습니다."
        )
    elif reason == "부정적 감정 감지":
        message = (
            "불편을 드려 정말 죄송합니다. 😔\n\n"
            "고객님의 소중한 의견을 전문 상담원이 직접 확인할 수 있도록 "
            "상담 요청을 등록하겠습니다.\n\n"
            "📞 긴급 문의: 1588-0000 (평일 09:00~18:00)\n"
            "💬 카카오톡: @쇼핑몰고객센터\n\n"
            "빠른 시간 내에 연락드리겠습니다. "
            "양해 부탁드립니다."
        )
    elif reason == "복잡한 문의":
        message = (
            "해당 문의는 전문 상담이 필요한 사안입니다.\n\n"
            "전문 담당자가 확인 후 연락드릴 수 있도록 "
            "상담 요청을 등록하겠습니다.\n\n"
            "📞 고객센터: 1588-0000\n"
            "📧 이메일: support@shop.example.com\n\n"
            "1~2 영업일 내에 담당자가 연락드리겠습니다."
        )
    else:
        message = (
            "해당 질문에 대해 정확한 답변을 드리기 어렵습니다.\n\n"
            "전문 상담원에게 연결해 드리겠습니다.\n\n"
            "📞 고객센터: 1588-0000 (평일 09:00~18:00)\n"
            "💬 카카오톡: @쇼핑몰고객센터\n"
            "📧 이메일: support@shop.example.com"
        )

    return {
        "answer": message,
        "confidence": 1.0,
        "escalation": {
            "reason": reason,
            "priority": _get_priority(reason),
            "conversation_id": conversation_id,
        },
        "agent": "escalation_agent",
        "mode": "demo",
    }


def _get_priority(reason: str) -> str:
    """에스컬레이션 우선순위"""
    priority_map = {
        "부정적 감정 감지": "높음",
        "복잡한 문의": "높음",
        "고객 요청": "보통",
        "낮은 응답 신뢰도": "낮음",
        "기타": "낮음",
    }
    return priority_map.get(reason, "보통")
