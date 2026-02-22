"""
Tests for faq_agent module
Target: Increase coverage from 47% to 80%+
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

import config
from agents import faq_agent


class TestDemoAnswer:
    """_demo_answer 함수 테스트"""

    def test_delivery_keyword(self):
        """배송 키워드 매칭"""
        with patch.object(config, "DEMO_MODE", True):
            result = faq_agent._demo_answer("배송 상태 확인해주세요", [])

        assert "배송" in result["answer"]
        assert result["confidence"] >= 0.8
        assert result["agent"] == "faq_agent"
        assert result["mode"] == "demo"

    def test_return_keyword(self):
        """반품 키워드 매칭"""
        with patch.object(config, "DEMO_MODE", True):
            result = faq_agent._demo_answer("반품하고 싶습니다", [])

        assert "반품" in result["answer"]
        assert result["confidence"] >= 0.8

    def test_exchange_keyword(self):
        """교환 키워드 매칭"""
        with patch.object(config, "DEMO_MODE", True):
            result = faq_agent._demo_answer("교환 가능한가요", [])

        assert "교환" in result["answer"]

    def test_refund_keyword(self):
        """환불 키워드 매칭"""
        with patch.object(config, "DEMO_MODE", True):
            result = faq_agent._demo_answer("환불 요청합니다", [])

        assert "환불" in result["answer"]

    def test_member_keyword(self):
        """회원 키워드 매칭"""
        with patch.object(config, "DEMO_MODE", True):
            result = faq_agent._demo_answer("회원 가입 방법", [])

        assert "회원" in result["answer"]

    def test_point_keyword(self):
        """포인트 키워드 매칭"""
        with patch.object(config, "DEMO_MODE", True):
            result = faq_agent._demo_answer("포인트 적립 언제?", [])

        assert "포인트" in result["answer"]

    def test_coupon_keyword(self):
        """쿠폰 키워드 매칭"""
        with patch.object(config, "DEMO_MODE", True):
            result = faq_agent._demo_answer("쿠폰 사용법 알려주세요", [])

        assert "쿠폰" in result["answer"]

    def test_payment_keyword(self):
        """결제 키워드 매칭"""
        with patch.object(config, "DEMO_MODE", True):
            result = faq_agent._demo_answer("결제 수단 뭐 있나요", [])

        assert "결제" in result["answer"]

    def test_no_keyword_with_docs(self):
        """키워드 없지만 문서 존재"""
        docs = [
            {"text": "이것은 테스트 문서입니다. 관련 정보가 포함되어 있습니다.", "score": 0.9}
        ]

        result = faq_agent._demo_answer("일반적인 질문", docs)

        assert "관련 정보" in result["answer"]
        assert result["confidence"] == 0.9

    def test_no_keyword_no_docs(self):
        """키워드도 없고 문서도 없음 - 폴백"""
        result = faq_agent._demo_answer("알 수 없는 질문", [])

        assert "죄송" in result["answer"] or "문의" in result["answer"]
        assert result["confidence"] == 0.2
        assert result["source_documents"] == []

    def test_docs_limited_to_three(self):
        """문서가 3개로 제한됨"""
        docs = [
            {"text": f"문서 {i}", "score": 0.8 - i * 0.1}
            for i in range(10)
        ]

        result = faq_agent._demo_answer("테스트", docs)

        assert len(result["source_documents"]) == 3


class TestHandle:
    """handle 함수 테스트"""

    @patch("agents.faq_agent.search")
    def test_handle_demo_mode(self, mock_search, monkeypatch):
        """데모 모드에서 handle 호출"""
        monkeypatch.setattr(config, "DEMO_MODE", True)
        mock_search.return_value = [{"text": "test doc", "score": 0.8}]

        result = faq_agent.handle("배송 문의")

        assert "answer" in result
        assert "confidence" in result
        assert result["agent"] == "faq_agent"

    @patch("agents.faq_agent.search")
    def test_handle_with_conversation_id(self, mock_search, monkeypatch):
        """conversation_id와 함께 호출"""
        monkeypatch.setattr(config, "DEMO_MODE", True)
        mock_search.return_value = []

        result = faq_agent.handle("테스트 질문", conversation_id="conv-123")

        assert "answer" in result

    @patch("agents.faq_agent.search")
    def test_handle_uses_retrieval_k(self, mock_search, monkeypatch):
        """RETRIEVAL_K 설정 사용"""
        monkeypatch.setattr(config, "DEMO_MODE", True)
        monkeypatch.setattr(config, "RETRIEVAL_K", 5)
        mock_search.return_value = []

        faq_agent.handle("테스트")

        mock_search.assert_called_once_with("테스트", k=5)


class TestLlmAnswer:
    """_llm_answer 함수 테스트 - 예외 처리 중심"""

    def test_llm_answer_exception(self, monkeypatch):
        """LLM 예외 처리"""
        monkeypatch.setattr(config, "MODEL_NAME", "gpt-4o-mini")
        monkeypatch.setattr(config, "TEMPERATURE", 0.3)
        monkeypatch.setattr(config, "MAX_TOKENS", 1024)
        monkeypatch.setattr(config, "OPENAI_API_KEY", "invalid-key")

        with patch("langchain_openai.ChatOpenAI") as MockChatOpenAI:
            MockChatOpenAI.side_effect = Exception("API Error")

            result = faq_agent._llm_answer("질문", [])

        assert "오류" in result["answer"]
        assert result["confidence"] == 0.0
        assert result["mode"] == "error"

    def test_llm_answer_with_docs(self, monkeypatch):
        """문서와 함께 LLM 호출 구조 테스트"""
        monkeypatch.setattr(config, "MODEL_NAME", "gpt-4o-mini")
        monkeypatch.setattr(config, "TEMPERATURE", 0.3)
        monkeypatch.setattr(config, "MAX_TOKENS", 1024)
        monkeypatch.setattr(config, "OPENAI_API_KEY", "test-key")

        docs = [{"text": "문서1", "score": 0.9}, {"text": "문서2", "score": 0.8}]

        # 예외를 발생시켜서 함수가 문서를 올바르게 처리하는지 확인
        with patch("langchain_openai.ChatOpenAI") as MockChatOpenAI:
            MockChatOpenAI.side_effect = Exception("Test exception")

            result = faq_agent._llm_answer("질문", docs)

        # 예외가 발생해도 문서 정보가 source_documents에 포함됨 (최대 3개)
        assert len(result["source_documents"]) == 2


class TestDemoResponses:
    """_DEMO_RESPONSES 상수 테스트"""

    def test_all_keywords_have_answers(self):
        """모든 키워드에 답변 존재"""
        for keyword, resp in faq_agent._DEMO_RESPONSES.items():
            assert "answer" in resp
            assert "confidence" in resp
            assert len(resp["answer"]) > 0
            assert 0 <= resp["confidence"] <= 1

    def test_responses_contain_relevant_info(self):
        """답변에 관련 정보 포함"""
        assert "1~3 영업일" in faq_agent._DEMO_RESPONSES["배송"]["answer"]
        assert "7일" in faq_agent._DEMO_RESPONSES["반품"]["answer"]
        assert "3~5 영업일" in faq_agent._DEMO_RESPONSES["환불"]["answer"]


class TestConfidenceScore:
    """신뢰도 점수 테스트"""

    def test_keyword_match_confidence(self):
        """키워드 매칭 시 신뢰도"""
        result = faq_agent._demo_answer("배송", [])
        assert result["confidence"] >= 0.78

    def test_doc_based_confidence(self):
        """문서 기반 신뢰도"""
        docs = [{"text": "테스트 문서", "score": 0.75}]
        result = faq_agent._demo_answer("일반 질문", docs)
        assert result["confidence"] == 0.75

    def test_fallback_confidence(self):
        """폴백 신뢰도"""
        result = faq_agent._demo_answer("알 수 없는 질문", [])
        assert result["confidence"] == 0.2
