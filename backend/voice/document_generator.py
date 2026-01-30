"""
전사 텍스트 → RAG 지식베이스 문서 변환기

기능:
- 고객 질문 / 상담원 답변 쌍 추출
- 카테고리 자동 분류 (배송, 반품/교환, 결제, 회원, 상품문의, 기타)
- 구조화된 마크다운 문서 생성
- 데모 모드: 키워드 기반 추출 (LLM API 불필요)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import List, Optional, Tuple

from voice.transcriber import TranscriptResult, TranscriptSegment


# ── 카테고리 정의 ──────────────────────────────────────────

CATEGORIES = {
    "배송": [
        "배송", "택배", "도착", "운송", "발송", "배달", "물류",
        "지연", "추적", "송장", "일반배송", "빠른배송", "당일배송",
    ],
    "반품/교환": [
        "반품", "교환", "환불", "반송", "불량", "하자", "변심",
        "반품신청", "교환신청", "반품비", "반품배송비",
    ],
    "결제": [
        "결제", "카드", "계좌", "이체", "포인트", "쿠폰", "할인",
        "가격", "금액", "청구", "영수증", "결제수단", "무통장",
    ],
    "회원": [
        "회원", "등급", "멤버십", "가입", "탈퇴", "비밀번호",
        "아이디", "로그인", "VIP", "실버", "골드", "혜택", "마일리지",
    ],
    "상품문의": [
        "상품", "제품", "사이즈", "색상", "재고", "입고", "품절",
        "원산지", "성분", "소재", "리뷰", "후기",
    ],
}


@dataclass
class QAPair:
    """추출된 질문-답변 쌍"""
    question: str
    answer: str
    category: str = "기타"
    confidence: float = 0.8

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GeneratedDocument:
    """생성된 RAG 문서"""
    markdown: str
    qa_pairs: List[QAPair] = field(default_factory=list)
    primary_category: str = "기타"
    source_file: str = ""
    generated_date: str = ""
    qa_count: int = 0
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "markdown": self.markdown,
            "qa_pairs": [qa.to_dict() for qa in self.qa_pairs],
            "primary_category": self.primary_category,
            "source_file": self.source_file,
            "generated_date": self.generated_date,
            "qa_count": self.qa_count,
            "confidence": round(self.confidence, 2),
        }


class DocumentGenerator:
    """
    전사 결과를 구조화된 RAG 문서로 변환.
    
    모드:
    - LLM 모드: OpenAI GPT를 사용한 고품질 Q&A 추출
    - 데모 모드: 키워드 기반 + 템플릿 추출 (API 불필요)
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        if self._api_key is None:
            import os
            self._api_key = os.getenv("OPENAI_API_KEY", "")

    def generate(self, transcript: TranscriptResult) -> GeneratedDocument:
        """
        전사 결과를 RAG 문서로 변환.
        
        Args:
            transcript: 전사 결과
            
        Returns:
            GeneratedDocument: 생성된 문서 (마크다운 + 메타데이터)
        """
        # Q&A 추출
        if self._api_key:
            try:
                qa_pairs = self._extract_qa_with_llm(transcript)
            except Exception as e:
                print(f"[LLM Q&A 추출 실패] {e} — 키워드 모드로 전환")
                qa_pairs = self._extract_qa_keyword(transcript)
        else:
            qa_pairs = self._extract_qa_keyword(transcript)

        # 주요 카테고리 결정
        primary_category = self._determine_primary_category(qa_pairs)

        # 마크다운 문서 생성
        today = date.today().isoformat()
        markdown = self._build_markdown(
            qa_pairs=qa_pairs,
            category=primary_category,
            source_file=transcript.source_file,
            date_str=today,
        )

        # 평균 신뢰도 계산
        avg_confidence = (
            sum(qa.confidence for qa in qa_pairs) / len(qa_pairs)
            if qa_pairs
            else 0.0
        )

        return GeneratedDocument(
            markdown=markdown,
            qa_pairs=qa_pairs,
            primary_category=primary_category,
            source_file=transcript.source_file,
            generated_date=today,
            qa_count=len(qa_pairs),
            confidence=avg_confidence,
        )

    # ── LLM 기반 Q&A 추출 ─────────────────────────────────

    def _extract_qa_with_llm(self, transcript: TranscriptResult) -> List[QAPair]:
        """OpenAI GPT를 사용한 Q&A 추출"""
        from openai import OpenAI

        client = OpenAI(api_key=self._api_key)

        conversation_text = transcript.full_text
        categories_str = ", ".join(CATEGORIES.keys()) + ", 기타"

        prompt = f"""다음은 고객센터 전화 상담 전사 내용입니다. 
이 대화에서 고객의 질문과 상담원의 답변을 Q&A 쌍으로 추출해 주세요.

규칙:
1. 각 Q&A 쌍은 독립적인 FAQ 항목으로 사용할 수 있어야 합니다.
2. 질문은 일반적인 형태로 바꿔 주세요 (특정 주문번호 등 제거).
3. 답변은 핵심 정보만 간결하게 정리해 주세요.
4. 각 Q&A의 카테고리를 지정해 주세요: {categories_str}
5. JSON 배열 형식으로 반환해 주세요.

대화 내용:
{conversation_text}

JSON 형식:
[
  {{"question": "질문", "answer": "답변", "category": "카테고리"}},
  ...
]

JSON만 반환하세요:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )

        import json
        content = response.choices[0].message.content.strip()
        # JSON 블록 추출 (```json ... ``` 형태 대응)
        json_match = re.search(r"\[.*\]", content, re.DOTALL)
        if json_match:
            raw_pairs = json.loads(json_match.group())
        else:
            raw_pairs = json.loads(content)

        return [
            QAPair(
                question=pair["question"],
                answer=pair["answer"],
                category=pair.get("category", "기타"),
                confidence=0.9,
            )
            for pair in raw_pairs
        ]

    # ── 키워드 기반 Q&A 추출 (데모 모드) ──────────────────

    def _extract_qa_keyword(self, transcript: TranscriptResult) -> List[QAPair]:
        """
        키워드 기반 Q&A 추출.
        고객 발화에서 질문을 감지하고, 그에 대응하는 상담원 답변을 추출.
        """
        segments = transcript.segments
        qa_pairs: List[QAPair] = []

        # 질문 감지 패턴
        question_patterns = [
            r".*\?$",
            r".*인가요",
            r".*인가요\?",
            r".*일까요",
            r".*나요",
            r".*되나요",
            r".*가능한가요",
            r".*할 수 있나요",
            r".*어떻게",
            r".*얼마",
            r".*언제",
            r".*왜",
            r".*안 [왔오]",
            r".*몇",
            r".*어디",
        ]

        i = 0
        while i < len(segments):
            seg = segments[i]
            # 고객 발화에서 질문 패턴 찾기
            if seg.speaker == "고객" and self._is_question(seg.text, question_patterns):
                # 질문 텍스트 정제
                question = self._normalize_question(seg.text)

                # 다음 상담원 답변 찾기
                answer_parts: List[str] = []
                j = i + 1
                while j < len(segments):
                    if segments[j].speaker == "상담원":
                        answer_parts.append(segments[j].text)
                        # 연속된 상담원 발화도 포함
                        k = j + 1
                        while k < len(segments) and segments[k].speaker == "상담원":
                            answer_parts.append(segments[k].text)
                            k += 1
                        break
                    j += 1

                if answer_parts:
                    answer = " ".join(answer_parts)
                    category = self._categorize_text(question + " " + answer)
                    qa_pairs.append(
                        QAPair(
                            question=question,
                            answer=answer,
                            category=category,
                            confidence=0.7,
                        )
                    )
            i += 1

        return qa_pairs

    def _is_question(self, text: str, patterns: List[str]) -> bool:
        """텍스트가 질문인지 판단"""
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    def _normalize_question(self, text: str) -> str:
        """
        질문을 일반적인 FAQ 형태로 정제.
        개인정보(주문번호 등)를 제거.
        """
        # 주문번호 패턴 제거
        text = re.sub(r"ORD-\d{4}-\d+", "", text)
        # "제가", "저는" 등 → 일반형
        text = re.sub(r"제가|저는|저의|제", "", text)
        text = text.strip()
        # 질문형 종결이 없으면 추가
        if text and not text.endswith("?") and not text.endswith("요"):
            text += "?"
        return text

    # ── 카테고리 분류 ──────────────────────────────────────

    def _categorize_text(self, text: str) -> str:
        """텍스트의 키워드를 기반으로 카테고리 분류"""
        scores: dict[str, int] = {}
        text_lower = text.lower()

        for category, keywords in CATEGORIES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score

        if not scores:
            return "기타"
        return max(scores, key=scores.get)  # type: ignore[arg-type]

    def _determine_primary_category(self, qa_pairs: List[QAPair]) -> str:
        """Q&A 쌍들의 주요 카테고리 결정"""
        if not qa_pairs:
            return "기타"
        category_counts: dict[str, int] = {}
        for qa in qa_pairs:
            category_counts[qa.category] = category_counts.get(qa.category, 0) + 1
        return max(category_counts, key=category_counts.get)  # type: ignore[arg-type]

    # ── 마크다운 문서 생성 ─────────────────────────────────

    def _build_markdown(
        self,
        qa_pairs: List[QAPair],
        category: str,
        source_file: str,
        date_str: str,
    ) -> str:
        """구조화된 마크다운 문서 생성"""
        lines = [
            f"# [{category}] - 자동 생성 문서",
            f"원본: {source_file} | 생성일: {date_str}",
            "",
        ]

        if not qa_pairs:
            lines.append("_추출된 Q&A가 없습니다._")
            return "\n".join(lines)

        for i, qa in enumerate(qa_pairs, 1):
            lines.extend([
                f"## Q&A {i}",
                f"**카테고리:** {qa.category}",
                f"**질문:** {qa.question}",
                f"**답변:** {qa.answer}",
                "",
            ])

        # 문서 하단 메타데이터
        lines.extend([
            "---",
            f"총 Q&A 수: {len(qa_pairs)}",
            f"주요 카테고리: {category}",
            f"생성 방식: 자동 추출",
        ])

        return "\n".join(lines)
