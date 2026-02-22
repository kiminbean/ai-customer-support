"""
Tests for datahub/processor module
Target: Increase coverage from 20% to 70%+
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from datahub.processor import (
    QAPair,
    PROCESSED_DIR,
    FORMAT_PROCESSORS,
    _extract_field,
    _clean_tweet,
    _deduplicate,
    _process_conversation,
    _process_qa,
    _process_intent_response,
    _process_ticket,
    _process_tweet,
    _extract_from_dialogue,
    _translate_pairs,
    _generate_markdown,
    process_dataset,
    get_processed_data,
    get_process_metadata,
)
import config


class TestQAPair:
    """QAPair 클래스 테스트"""

    def test_creation(self):
        """QA 쌍 생성"""
        qa = QAPair(
            question="배송은 얼마나 걸리나요?",
            answer="1~3일 소요됩니다.",
            category="배송",
            source_format="qa",
        )

        assert qa.question == "배송은 얼마나 걸리나요?"
        assert qa.answer == "1~3일 소요됩니다."
        assert qa.category == "배송"
        assert qa.source_format == "qa"

    def test_to_dict(self):
        """직렬화"""
        qa = QAPair(question="Q?", answer="A.", metadata={"key": "value"})
        result = qa.to_dict()

        assert result["question"] == "Q?"
        assert result["answer"] == "A."
        assert result["metadata"] == {"key": "value"}

    def test_fingerprint(self):
        """지문(해시) 생성"""
        qa1 = QAPair(question="Question", answer="Answer")
        qa2 = QAPair(question="question", answer="answer")  # 소문자
        qa3 = QAPair(question="Question", answer="Different")

        assert qa1.fingerprint() == qa2.fingerprint()  # 대소문자 무시
        assert qa1.fingerprint() != qa3.fingerprint()

    def test_fingerprint_strip(self):
        """공백 제거 후 지문 생성 (대소문자 무시)"""
        qa1 = QAPair(question="Question", answer="Answer")
        qa2 = QAPair(question="question", answer="answer")

        # lower() 적용 후 동일해야 함
        assert qa1.fingerprint() == qa2.fingerprint()


class TestExtractField:
    """_extract_field 함수 테스트"""

    def test_extract_first_match(self):
        """첫 번째 매칭 필드 추출"""
        record = {"question": "Q?", "query": "Another"}
        result = _extract_field(record, ["question", "query"])
        assert result == "Q?"

    def test_extract_fallback(self):
        """폴백 필드 추출"""
        record = {"query": "Q?", "input": "Another"}
        result = _extract_field(record, ["question", "query", "input"])
        assert result == "Q?"

    def test_no_match(self):
        """매칭 없음"""
        record = {"other": "value"}
        result = _extract_field(record, ["question", "query"])
        assert result == ""

    def test_empty_value(self):
        """빈 값 무시"""
        record = {"question": "   ", "query": "Q?"}
        result = _extract_field(record, ["question", "query"])
        assert result == "Q?"

    def test_non_string_value(self):
        """문자열이 아닌 값 무시"""
        record = {"question": 123, "query": "Q?"}
        result = _extract_field(record, ["question", "query"])
        assert result == "Q?"


class TestCleanTweet:
    """_clean_tweet 함수 테스트"""

    def test_remove_mentions(self):
        """멘션 제거"""
        text = "Hello @user how are you?"
        result = _clean_tweet(text)
        assert "@user" not in result

    def test_multiple_mentions(self):
        """다중 멘션 제거"""
        text = "@user1 @user2 Hello there"
        result = _clean_tweet(text)
        assert "@user1" not in result
        assert "@user2" not in result

    def test_no_mentions(self):
        """멘션 없음"""
        text = "Just a normal tweet"
        result = _clean_tweet(text)
        assert result == text


class TestDeduplicate:
    """_deduplicate 함수 테스트"""

    def test_remove_duplicates(self):
        """중복 제거"""
        pairs = [
            QAPair(question="Q1", answer="A1"),
            QAPair(question="Q1", answer="A1"),  # 중복
            QAPair(question="Q2", answer="A2"),
        ]
        result = _deduplicate(pairs)
        assert len(result) == 2

    def test_keep_all_unique(self):
        """모두 고유"""
        pairs = [
            QAPair(question="Q1", answer="A1"),
            QAPair(question="Q2", answer="A2"),
        ]
        result = _deduplicate(pairs)
        assert len(result) == 2


class TestProcessConversation:
    """_process_conversation 함수 테스트"""

    def test_basic_conversation(self):
        """기본 대화 처리"""
        records = [
            {"customer": "배송 문의", "agent": "1~3일 소요"},
            {"user": "반품 문의", "assistant": "7일 이내 가능"},
        ]
        result = _process_conversation(records)

        assert len(result) == 2
        assert result[0].question == "배송 문의"
        assert result[1].source_format == "conversation"

    def test_alternative_keys(self):
        """대체 키 처리"""
        records = [
            {"input": "질문", "output": "답변"},
        ]
        result = _process_conversation(records)

        assert len(result) == 1
        assert result[0].question == "질문"

    def test_with_category(self):
        """카테고리 포함"""
        records = [
            {"customer": "Q", "agent": "A", "category": "배송"},
        ]
        result = _process_conversation(records)

        assert result[0].category == "배송"


class TestProcessDialogue:
    """_extract_from_dialogue 함수 테스트"""

    def test_string_dialogue(self):
        """문자열 대화"""
        dialogue = "Customer: Q1\nAgent: A1\nCustomer: Q2\nAgent: A2"
        result = _extract_from_dialogue(dialogue)

        assert len(result) >= 1

    def test_list_dialogue(self):
        """리스트 대화 (역할 기반)"""
        dialogue = [
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
        ]
        result = _extract_from_dialogue(dialogue)

        assert len(result) == 1
        assert result[0].question == "Q1"

    def test_empty_dialogue(self):
        """빈 대화"""
        result = _extract_from_dialogue([])
        assert len(result) == 0


class TestProcessQA:
    """_process_qa 함수 테스트"""

    def test_basic_qa(self):
        """기본 Q&A"""
        records = [
            {"question": "Q1", "answer": "A1"},
            {"query": "Q2", "response": "A2"},
        ]
        result = _process_qa(records)

        assert len(result) == 2

    def test_with_category(self):
        """카테고리 포함"""
        records = [
            {"question": "Q", "answer": "A", "category": "FAQ"},
        ]
        result = _process_qa(records)

        assert result[0].category == "FAQ"


class TestProcessIntentResponse:
    """_process_intent_response 함수 테스트"""

    def test_intent_response(self):
        """의도-응답 처리"""
        records = [
            {"intent": "order", "instruction": "주문하고 싶어요", "response": "주문해 드리겠습니다"},
        ]
        result = _process_intent_response(records)

        assert len(result) == 1
        assert result[0].category == "order"
        assert result[0].source_format == "intent-response"

    def test_alternative_keys(self):
        """대체 키"""
        records = [
            {"category": "shipping", "text": "배송 얼마나?", "output": "1~3일"},
        ]
        result = _process_intent_response(records)

        assert len(result) == 1


class TestProcessTicket:
    """_process_ticket 함수 테스트"""

    def test_ticket_processing(self):
        """티켓 처리"""
        records = [
            {
                "subject": "배송 오류",
                "description": "상품이 도착하지 않았습니다",
                "resolution": "재배송 조치하겠습니다",
            },
        ]
        result = _process_ticket(records)

        assert len(result) == 1
        assert "배송 오류" in result[0].question
        assert result[0].source_format == "ticket"

    def test_with_priority(self):
        """우선순위 포함"""
        records = [
            {
                "title": "긴급 문의",
                "body": "본문",
                "solution": "해결책",
                "priority": "high",
            },
        ]
        result = _process_ticket(records)

        assert result[0].metadata["priority"] == "high"


class TestProcessTweet:
    """_process_tweet 함수 테스트"""

    def test_tweet_processing(self):
        """트윗 처리"""
        records = [
            {
                "customer_tweet": "배송 언제 오나요 @company",
                "support_reply": "1~3일 내 도착 예정입니다",
            },
        ]
        result = _process_tweet(records)

        assert len(result) == 1
        assert "@company" not in result[0].question  # 멘션 제거됨

    def test_alternative_keys(self):
        """대체 키"""
        records = [
            {"inbound": "고객 트윗", "outbound": "회신"},
        ]
        result = _process_tweet(records)

        assert len(result) == 1


class TestGenerateMarkdown:
    """_generate_markdown 함수 테스트"""

    def test_basic_markdown(self):
        """기본 마크다운 생성"""
        pairs = [
            QAPair(question="Q1", answer="A1", category="배송"),
            QAPair(question="Q2", answer="A2"),
        ]
        result = _generate_markdown(
            qa_pairs=pairs,
            domain="고객지원",
            ds_name="테스트 데이터셋",
            dataset_id="test/dataset",
        )

        assert "# 고객지원 — 테스트 데이터셋" in result
        assert "총 Q&A: 2개" in result
        assert "## Q&A 1" in result
        assert "**질문:** Q1" in result
        assert "**카테고리:** 배송" in result


class TestProcessDataset:
    """process_dataset 함수 테스트"""

    @pytest.fixture
    def setup(self, tmp_path: Path, monkeypatch):
        """테스트 환경 설정"""
        # PROCESSED_DIR 설정
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr("datahub.processor.PROCESSED_DIR", processed_dir)

        # 다운로드된 데이터 디렉토리
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(config, "DATA_DIR", data_dir)

        return processed_dir, data_dir

    def test_dataset_not_in_registry(self, setup):
        """레지스트리에 없는 데이터셋"""
        with patch("datahub.processor.get_dataset_info") as mock_info:
            mock_info.return_value = None

            result = process_dataset("unknown/dataset")

            assert result["status"] == "failed"
            assert "찾을 수 없습니다" in result["error"]

    def test_dataset_no_downloaded_data(self, setup):
        """다운로드된 데이터 없음"""
        with patch("datahub.processor.get_dataset_info") as mock_info:
            with patch("datahub.processor.get_downloaded_data") as mock_data:
                mock_info.return_value = {"format": "qa", "domain": "test"}
                mock_data.return_value = None

                result = process_dataset("test/dataset")

                assert result["status"] == "failed"
                assert "다운로드된 데이터" in result["error"]

    def test_process_success(self, setup, monkeypatch):
        """성공적인 처리"""
        processed_dir, data_dir = setup

        with patch("datahub.processor.get_dataset_info") as mock_info:
            with patch("datahub.processor.get_downloaded_data") as mock_data:
                mock_info.return_value = {
                    "format": "qa",
                    "domain": "고객지원",
                    "name": "테스트",
                }
                mock_data.return_value = [
                    {"question": "Q1", "answer": "A1"},
                    {"question": "Q2", "answer": "A2"},
                ]

                result = process_dataset("test/dataset")

                assert result["status"] == "completed"
                assert result["qa_pairs"] == 2

    def test_process_with_max_entries(self, setup):
        """최대 항목 수 제한"""
        with patch("datahub.processor.get_dataset_info") as mock_info:
            with patch("datahub.processor.get_downloaded_data") as mock_data:
                mock_info.return_value = {"format": "qa", "domain": "test"}
                mock_data.return_value = [
                    {"question": f"Q{i}", "answer": f"A{i}"}
                    for i in range(100)
                ]

                result = process_dataset("test/dataset", max_entries=10)

                assert result["status"] == "completed"

    def test_process_with_progress_callback(self, setup):
        """진행 콜백"""
        with patch("datahub.processor.get_dataset_info") as mock_info:
            with patch("datahub.processor.get_downloaded_data") as mock_data:
                mock_info.return_value = {"format": "qa", "domain": "test"}
                mock_data.return_value = [{"question": "Q", "answer": "A"}]

                progress_calls = []

                def callback(msg, progress):
                    progress_calls.append((msg, progress))

                result = process_dataset("test/dataset", progress_callback=callback)

                assert len(progress_calls) >= 1


class TestTranslatePairs:
    """_translate_pairs 함수 테스트"""

    def test_translate_success(self):
        """번역 성공"""
        pairs = [QAPair(question="Hello", answer="World")]

        with patch("datahub.translator.translate_batch") as mock_translate:
            mock_translate.return_value = [
                {"question": "안녕", "answer": "세계", "category": "", "source_format": ""}
            ]

            result = _translate_pairs(pairs)

            assert result[0].question == "안녕"

    def test_translate_failure(self):
        """번역 실패 시 원본 반환"""
        pairs = [QAPair(question="Hello", answer="World")]

        with patch("datahub.translator.translate_batch") as mock_translate:
            mock_translate.side_effect = Exception("Translation failed")

            result = _translate_pairs(pairs)

            assert result[0].question == "Hello"


class TestGetProcessedData:
    """get_processed_data 함수 테스트"""

    def test_get_existing_data(self, tmp_path, monkeypatch):
        """기존 데이터 조회"""
        processed_dir = tmp_path / "processed"
        dataset_dir = processed_dir / "test__dataset"
        dataset_dir.mkdir(parents=True)
        monkeypatch.setattr("datahub.processor.PROCESSED_DIR", processed_dir)

        # 데이터 파일 생성
        qa_data = [{"question": "Q", "answer": "A"}]
        (dataset_dir / "qa_pairs.json").write_text(json.dumps(qa_data))

        result = get_processed_data("test/dataset")

        assert result is not None
        assert len(result) == 1

    def test_get_nonexistent_data(self, tmp_path, monkeypatch):
        """존재하지 않는 데이터"""
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir(parents=True)
        monkeypatch.setattr("datahub.processor.PROCESSED_DIR", processed_dir)

        result = get_processed_data("nonexistent/dataset")

        assert result is None


class TestGetProcessMetadata:
    """get_process_metadata 함수 테스트"""

    def test_get_metadata(self, tmp_path, monkeypatch):
        """메타데이터 조회"""
        processed_dir = tmp_path / "processed"
        dataset_dir = processed_dir / "test__dataset"
        dataset_dir.mkdir(parents=True)
        monkeypatch.setattr("datahub.processor.PROCESSED_DIR", processed_dir)

        # 메타데이터 파일 생성
        meta = {"dataset_id": "test/dataset", "qa_pairs": 10}
        (dataset_dir / "process_metadata.json").write_text(json.dumps(meta))

        result = get_process_metadata("test/dataset")

        assert result is not None
        assert result["dataset_id"] == "test/dataset"

    def test_get_metadata_nonexistent(self, tmp_path, monkeypatch):
        """존재하지 않는 메타데이터"""
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir(parents=True)
        monkeypatch.setattr("datahub.processor.PROCESSED_DIR", processed_dir)

        result = get_process_metadata("nonexistent/dataset")

        assert result is None


class TestFormatProcessors:
    """FORMAT_PROCESSORS 매핑 테스트"""

    def test_all_formats_mapped(self):
        """모든 포맷에 프로세서 할당"""
        expected_formats = [
            "conversation",
            "qa",
            "intent-response",
            "ticket",
            "tweet",
            "audio+text",
        ]

        for fmt in expected_formats:
            assert fmt in FORMAT_PROCESSORS
            assert callable(FORMAT_PROCESSORS[fmt])
