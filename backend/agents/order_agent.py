"""
주문 에이전트 — 주문 조회, 배송 추적, 반품/환불 처리
데모 모드에서는 목업 주문 데이터를 사용한다.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Dict, Optional

# ── 목업 주문 데이터 ───────────────────────────────────────

_MOCK_ORDERS = {
    "ORD-2024-001": {
        "order_id": "ORD-2024-001",
        "status": "배송중",
        "product": "프리미엄 무선 이어폰 (화이트)",
        "quantity": 1,
        "price": 89000,
        "ordered_at": "2024-01-15",
        "shipped_at": "2024-01-16",
        "tracking_number": "CJ1234567890",
        "carrier": "CJ대한통운",
        "estimated_delivery": "2024-01-18",
        "customer_name": "김고객",
    },
    "ORD-2024-002": {
        "order_id": "ORD-2024-002",
        "status": "배송완료",
        "product": "스마트워치 프로 (블랙)",
        "quantity": 1,
        "price": 299000,
        "ordered_at": "2024-01-10",
        "shipped_at": "2024-01-11",
        "delivered_at": "2024-01-13",
        "tracking_number": "HJ9876543210",
        "carrier": "한진택배",
        "customer_name": "김고객",
    },
    "ORD-2024-003": {
        "order_id": "ORD-2024-003",
        "status": "결제완료",
        "product": "울 캐시미어 코트 (네이비, L)",
        "quantity": 1,
        "price": 189000,
        "ordered_at": "2024-01-17",
        "customer_name": "김고객",
    },
    "ORD-2024-004": {
        "order_id": "ORD-2024-004",
        "status": "반품처리중",
        "product": "런닝화 에어맥스 (270mm)",
        "quantity": 1,
        "price": 139000,
        "ordered_at": "2024-01-05",
        "return_requested": "2024-01-14",
        "return_reason": "사이즈 불일치",
        "refund_amount": 136000,
        "customer_name": "김고객",
    },
}

# ── 주문 관련 키워드 ───────────────────────────────────────

ORDER_KEYWORDS = [
    "주문", "배송", "택배", "추적", "조회",
    "반품", "교환", "환불", "취소",
    "송장", "운송장", "도착", "발송",
]


def is_order_query(query: str) -> bool:
    """주문 관련 쿼리인지 판별"""
    # 주문번호 패턴 체크
    if re.search(r"ORD-\d{4}-\d{3}", query, re.IGNORECASE):
        return True
    # 키워드 체크
    return any(kw in query for kw in ORDER_KEYWORDS)


# ── 주문 에이전트 핸들러 ───────────────────────────────────

def handle(query: str, conversation_id: Optional[str] = None) -> Dict:
    """
    주문 관련 쿼리 처리.
    - 주문번호가 있으면 상세 조회
    - 없으면 최근 주문 요약
    """
    # 주문번호 추출
    match = re.search(r"(ORD-\d{4}-\d{3})", query, re.IGNORECASE)
    if match:
        order_id = match.group(1).upper()
        return _lookup_order(order_id, query)

    # 주문 목록 / 일반 주문 질문
    if any(kw in query for kw in ["반품", "환불", "취소"]):
        return _handle_return_query(query)
    if any(kw in query for kw in ["주문", "내 주문", "주문내역", "목록"]):
        return _list_orders()

    return _handle_general_order_query(query)


def _lookup_order(order_id: str, query: str) -> Dict:
    """주문번호로 상세 조회"""
    order = _MOCK_ORDERS.get(order_id)
    if not order:
        return {
            "answer": f"주문번호 '{order_id}'을(를) 찾을 수 없습니다. "
                      f"주문번호를 다시 확인해 주세요.\n"
                      f"예시: ORD-2024-001",
            "confidence": 0.9,
            "order_data": None,
            "agent": "order_agent",
            "mode": "demo",
        }

    # 상태별 상세 메시지
    status = order["status"]
    lines = [
        f"📦 주문 조회 결과",
        f"",
        f"• 주문번호: {order['order_id']}",
        f"• 상품: {order['product']}",
        f"• 금액: {order['price']:,}원",
        f"• 주문일: {order['ordered_at']}",
        f"• 상태: {status}",
    ]

    if status == "배송중":
        lines.extend([
            f"",
            f"🚚 배송 정보",
            f"• 택배사: {order.get('carrier', '-')}",
            f"• 송장번호: {order.get('tracking_number', '-')}",
            f"• 발송일: {order.get('shipped_at', '-')}",
            f"• 도착예정: {order.get('estimated_delivery', '-')}",
        ])
    elif status == "배송완료":
        lines.extend([
            f"",
            f"✅ 배송이 완료되었습니다.",
            f"• 배송완료일: {order.get('delivered_at', '-')}",
            f"• 반품/교환은 수령 후 7일 이내 가능합니다.",
        ])
    elif status == "결제완료":
        lines.append(f"\n⏳ 상품 준비 중입니다. 1~2 영업일 내에 발송됩니다.")
    elif status == "반품처리중":
        lines.extend([
            f"",
            f"🔄 반품 처리 현황",
            f"• 반품 사유: {order.get('return_reason', '-')}",
            f"• 반품 신청일: {order.get('return_requested', '-')}",
            f"• 환불 예정액: {order.get('refund_amount', 0):,}원",
            f"• 환불은 상품 수거 후 3~5 영업일 내에 처리됩니다.",
        ])

    return {
        "answer": "\n".join(lines),
        "confidence": 0.95,
        "order_data": order,
        "agent": "order_agent",
        "mode": "demo",
    }


def _list_orders() -> Dict:
    """최근 주문 목록"""
    lines = ["📋 최근 주문 내역\n"]
    for oid, order in _MOCK_ORDERS.items():
        lines.append(
            f"• {order['order_id']} | {order['product'][:20]}... | "
            f"{order['price']:,}원 | {order['status']}"
        )
    lines.append("\n상세 조회를 원하시면 주문번호를 알려주세요.")

    return {
        "answer": "\n".join(lines),
        "confidence": 0.90,
        "order_data": list(_MOCK_ORDERS.values()),
        "agent": "order_agent",
        "mode": "demo",
    }


def _handle_return_query(query: str) -> Dict:
    """반품/환불/취소 관련 안내"""
    return {
        "answer": (
            "🔄 반품/교환/환불 안내\n\n"
            "• 반품/교환: 상품 수령 후 7일 이내 신청 가능\n"
            "• 반품 배송비: 고객 변심 시 편도 3,000원 / 상품 하자 시 무료\n"
            "• 환불 처리: 상품 수거 후 3~5 영업일\n"
            "• 주문 취소: 발송 전 상태에서만 가능\n\n"
            "반품을 신청하시려면 주문번호를 알려주세요.\n"
            "예: ORD-2024-001 반품 신청"
        ),
        "confidence": 0.85,
        "order_data": None,
        "agent": "order_agent",
        "mode": "demo",
    }


def _handle_general_order_query(query: str) -> Dict:
    """일반 주문 관련 질문"""
    return {
        "answer": (
            "주문 관련 도움을 드리겠습니다. 아래 중 원하시는 서비스를 선택해 주세요:\n\n"
            "1️⃣ 주문 조회 — 주문번호를 입력해 주세요 (예: ORD-2024-001)\n"
            "2️⃣ 배송 추적 — 주문번호 또는 송장번호를 입력해 주세요\n"
            "3️⃣ 반품/교환 — '반품 신청' 또는 '교환 신청'이라고 말씀해 주세요\n"
            "4️⃣ 주문 취소 — '주문 취소'라고 말씀해 주세요\n"
            "5️⃣ 최근 주문 목록 — '내 주문'이라고 말씀해 주세요"
        ),
        "confidence": 0.70,
        "order_data": None,
        "agent": "order_agent",
        "mode": "demo",
    }
