from __future__ import annotations

"""
API 테스트 — 기본 엔드포인트 동작 확인
데모 모드에서 실행 (API 키 불필요)
"""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ── 헬스 체크 ──────────────────────────────────────────────

def test_health():
    """서비스 상태 확인"""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "demo_mode" in data


# ── 채팅 API ──────────────────────────────────────────────

def test_chat_greeting():
    """인사 메시지 테스트"""
    resp = client.post("/api/chat", json={"message": "안녕하세요"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["conversation_id"]
    assert data["agent"] in ("orchestrator", "faq_agent")


def test_chat_faq():
    """FAQ 질문 테스트"""
    resp = client.post("/api/chat", json={"message": "배송은 얼마나 걸리나요?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["confidence"] > 0


def test_chat_order():
    """주문 조회 테스트"""
    resp = client.post("/api/chat", json={"message": "ORD-2024-001 주문 조회"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["agent"] == "order_agent"


def test_chat_order_not_found():
    """존재하지 않는 주문 테스트"""
    resp = client.post("/api/chat", json={"message": "ORD-9999-999 조회"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data


def test_chat_escalation():
    """상담원 연결 요청 테스트"""
    resp = client.post("/api/chat", json={"message": "상담원 연결해 주세요"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent"] == "escalation_agent"


def test_chat_empty_message():
    """빈 메시지 에러 테스트"""
    resp = client.post("/api/chat", json={"message": "   "})
    assert resp.status_code == 400


def test_chat_conversation_continuity():
    """대화 연속성 테스트"""
    # 첫 메시지
    resp1 = client.post("/api/chat", json={"message": "안녕하세요"})
    conv_id = resp1.json()["conversation_id"]

    # 같은 대화에서 두 번째 메시지
    resp2 = client.post("/api/chat", json={
        "message": "배송 문의입니다",
        "conversation_id": conv_id,
    })
    assert resp2.json()["conversation_id"] == conv_id


# ── 문서 API ──────────────────────────────────────────────

def test_list_documents():
    """문서 목록 조회 테스트"""
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert "total" in data


# ── 대화 API ──────────────────────────────────────────────

def test_list_conversations():
    """대화 목록 조회 테스트"""
    # 먼저 대화 생성
    client.post("/api/chat", json={"message": "테스트 메시지"})

    resp = client.get("/api/conversations")
    assert resp.status_code == 200
    data = resp.json()
    assert "conversations" in data
    assert data["total"] > 0


def test_get_conversation():
    """대화 상세 조회 테스트"""
    # 대화 생성
    chat_resp = client.post("/api/chat", json={"message": "대화 테스트"})
    conv_id = chat_resp.json()["conversation_id"]

    resp = client.get(f"/api/conversations/{conv_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == conv_id
    assert len(data["messages"]) >= 2  # user + assistant


def test_get_conversation_not_found():
    """존재하지 않는 대화 테스트"""
    resp = client.get("/api/conversations/nonexistent-id")
    assert resp.status_code == 404


# ── 분석 API ──────────────────────────────────────────────

def test_analytics():
    """분석 데이터 테스트"""
    resp = client.get("/api/analytics")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_conversations" in data
    assert "total_messages" in data


# ── 설정 API ──────────────────────────────────────────────

def test_get_settings():
    """설정 조회 테스트"""
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert "demo_mode" in data
    assert "model_name" in data


def test_update_settings():
    """설정 변경 테스트"""
    resp = client.post("/api/settings", json={
        "temperature": 0.5,
        "max_tokens": 2048,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["settings"]["temperature"] == 0.5
    assert data["settings"]["max_tokens"] == 2048


# ── 다양한 시나리오 ───────────────────────────────────────

def test_return_query():
    """반품 문의 테스트"""
    resp = client.post("/api/chat", json={"message": "반품하고 싶어요"})
    assert resp.status_code == 200
    assert "반품" in resp.json()["answer"]


def test_angry_customer():
    """불만 고객 에스컬레이션 테스트"""
    resp = client.post("/api/chat", json={"message": "정말 화가 나요! 이게 뭐예요!"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent"] == "escalation_agent"


def test_refund_query():
    """환불 문의 테스트"""
    resp = client.post("/api/chat", json={"message": "환불은 얼마나 걸려요?"})
    assert resp.status_code == 200
    assert "answer" in resp.json()
