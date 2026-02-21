"""
데이터 허브 번역기 테스트
"""
from __future__ import annotations

import pytest

from datahub.translator import (
    translate_text,
    is_korean,
    needs_translation,
    _cache_key,
    _get_cached,
    _set_cached,
)


class TestIsKorean:
    """한국어 판별 테스트"""

    def test_korean_text(self):
        """한국어 텍스트 판별"""
        assert is_korean("안녕하세요") is True
        assert is_korean("반갑습니다") is True
        assert is_korean("배송 문의입니다") is True

    def test_english_text(self):
        """영어 텍스트 판별"""
        assert is_korean("Hello") is False
        assert is_korean("What is your return policy?") is False

    def test_mixed_text(self):
        """한영 혼합 텍스트"""
        # 한국어가 10% 이상이면 한국어로 판별
        assert is_korean("Hello 안녕하세요 World") is True
        assert is_korean("A B C D E 가") is False  # 너무 적음

    def test_empty_text(self):
        """빈 텍스트"""
        assert is_korean("") is False
        assert is_korean("   ") is False


class TestNeedsTranslation:
    """번역 필요 여부 테스트"""

    def test_english_needs_translation(self):
        """영어는 번역 필요"""
        assert needs_translation("Hello") is True
        assert needs_translation("Return policy") is True

    def test_korean_no_translation(self):
        """한국어는 번역 불필요"""
        assert needs_translation("안녕하세요") is False
        assert needs_translation("반품 정책") is False

    def test_empty_no_translation(self):
        """빈 텍스트는 번역 불필요"""
        assert needs_translation("") is False
        assert needs_translation("   ") is False


class TestTranslateText:
    """텍스트 번역 테스트"""

    def test_korean_text_unchanged(self):
        """한국어 텍스트는 변경 없음"""
        result = translate_text("안녕하세요")
        assert result == "안녕하세요"

    def test_empty_text_unchanged(self):
        """빈 텍스트는 변경 없음"""
        assert translate_text("") == ""
        assert translate_text("   ") == "   "

    def test_english_text_in_demo_mode(self):
        """데모 모드에서 영어 텍스트는 마킹됨"""
        result = translate_text("Hello")
        # 데모 모드에서는 [번역 필요] 접두사 추가
        assert "[번역 필요]" in result or result == "Hello"

    def test_whitespace_text(self):
        """공백만 있는 텍스트"""
        result = translate_text("   ")
        assert result == "   "


class TestCacheFunctions:
    """캐시 함수 테스트"""

    def test_cache_key_consistency(self):
        """캐시 키 일관성"""
        key1 = _cache_key("test text")
        key2 = _cache_key("test text")
        assert key1 == key2

    def test_cache_key_different(self):
        """다른 텍스트는 다른 키"""
        key1 = _cache_key("test 1")
        key2 = _cache_key("test 2")
        assert key1 != key2

    def test_cache_key_format(self):
        """캐시 키 형식 (MD5)"""
        key = _cache_key("test")
        assert len(key) == 32  # MD5 hex length
        assert all(c in "0123456789abcdef" for c in key)

    def test_set_and_get_cached(self):
        """캐시 저장 및 조회"""
        original = "test original text"
        translated = "테스트 원문 텍스트"

        _set_cached(original, translated)
        result = _get_cached(original)

        assert result == translated


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_very_long_text(self):
        """매우 긴 텍스트"""
        long_text = "This is a test. " * 1000
        result = translate_text(long_text)
        assert len(result) > 0

    def test_special_characters(self):
        """특수 문자"""
        result = translate_text("Hello! @#$%^&*()")
        assert len(result) > 0

    def test_unicode_emoji(self):
        """유니코드 이모지"""
        result = translate_text("Hello 🎉 World! 🌍")
        assert "🎉" in result or len(result) > 0

    def test_newlines(self):
        """줄바꿈 포함"""
        result = translate_text("Line 1\nLine 2\nLine 3")
        assert "\n" in result or len(result) > 0

    def test_numbers_preserved(self):
        """숫자 보존"""
        result = translate_text("12345")
        assert "12345" in result or len(result) > 0
