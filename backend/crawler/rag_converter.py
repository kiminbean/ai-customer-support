"""
RAG 문서 변환기 — 추출된 콘텐츠를 RAG 지식베이스 문서로 변환

추출된 FAQ, 상품정보, 정책, 가이드 등을 마크다운 형식의
RAG 문서로 변환하여 벡터 스토어에 저장할 수 있게 한다.

기능:
- 자동 카테고리 분류
- Q&A 쌍 생성
- 중복 제거
- 출처 URL 추적
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from crawler.extractor import (
    ArticleItem,
    ContactInfo,
    ExtractedContent,
    FAQItem,
    PolicyItem,
    ProductItem,
)


# ── 카테고리 정의 ──────────────────────────────────────────

CATEGORIES = {
    "faq": "자주 묻는 질문 (FAQ)",
    "product": "상품정보",
    "shipping": "배송/반품",
    "usage": "이용안내",
    "tech": "기술지원",
    "contact": "고객센터/연락처",
    "general": "일반 안내",
}


# ── 데이터 모델 ────────────────────────────────────────────


@dataclass
class QAPair:
    """하나의 질문-답변 쌍"""
    question: str
    answer: str
    source_url: str = ""
    category: str = "general"

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "answer": self.answer,
            "source_url": self.source_url,
            "category": self.category,
        }


@dataclass
class RAGDocument:
    """RAG 지식베이스 문서"""
    id: str = ""
    title: str = ""
    category: str = "general"
    site_name: str = ""
    source_url: str = ""
    crawl_date: str = ""
    qa_pairs: list[QAPair] = field(default_factory=list)
    markdown: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.crawl_date:
            self.crawl_date = date.today().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "category_label": CATEGORIES.get(self.category, self.category),
            "site_name": self.site_name,
            "source_url": self.source_url,
            "crawl_date": self.crawl_date,
            "qa_pairs": [qa.to_dict() for qa in self.qa_pairs],
            "qa_count": len(self.qa_pairs),
            "markdown_length": len(self.markdown),
        }

    def to_markdown(self) -> str:
        """RAG 문서를 마크다운 형식으로 생성"""
        if self.markdown:
            return self.markdown

        lines: list[str] = []
        cat_label = CATEGORIES.get(self.category, self.category)

        lines.append(f"# [{cat_label}] — {self.site_name}에서 추출한 지식베이스")
        lines.append(f"출처: {self.source_url}")
        lines.append(f"크롤링일: {self.crawl_date}")
        lines.append("")

        for i, qa in enumerate(self.qa_pairs, 1):
            lines.append(f"## Q&A {i}")
            lines.append(f"**질문:** {qa.question}")
            lines.append(f"**답변:** {qa.answer}")
            if qa.source_url:
                lines.append(f"**출처 URL:** {qa.source_url}")
            lines.append("")

        self.markdown = "\n".join(lines)
        return self.markdown


# ── 변환기 ─────────────────────────────────────────────────


class RAGConverter:
    """추출된 콘텐츠를 RAG 문서로 변환"""

    def __init__(self, site_name: str = "", base_url: str = ""):
        self.site_name = site_name or "웹사이트"
        self.base_url = base_url
        self._seen_hashes: set[str] = set()

    def convert(
        self,
        extracted_contents: list[ExtractedContent],
        auto_categorize: bool = True,
        selected_items: list[int] | None = None,
    ) -> list[RAGDocument]:
        """추출된 콘텐츠 목록을 RAG 문서로 변환"""
        all_qa: list[QAPair] = []

        for content in extracted_contents:
            # FAQ → Q&A
            for faq in content.faqs:
                qa = QAPair(
                    question=faq.question,
                    answer=faq.answer,
                    source_url=faq.source_url or content.url,
                    category=self._categorize_faq(faq) if auto_categorize else "faq",
                )
                all_qa.append(qa)

            # 정책 → Q&A
            for policy in content.policies:
                qa_pairs = self._policy_to_qa(policy)
                all_qa.extend(qa_pairs)

            # 도움말 → Q&A
            for article in content.articles:
                qa_pairs = self._article_to_qa(article)
                all_qa.extend(qa_pairs)

            # 상품 → Q&A
            for product in content.products:
                qa_pairs = self._product_to_qa(product)
                all_qa.extend(qa_pairs)

            # 연락처 → Q&A
            if content.contact:
                qa_pairs = self._contact_to_qa(content.contact)
                all_qa.extend(qa_pairs)

        # 선택된 항목만 포함
        if selected_items is not None:
            all_qa = [all_qa[i] for i in selected_items if i < len(all_qa)]

        # 중복 제거
        all_qa = self._deduplicate(all_qa)

        # 카테고리별 문서 생성
        if auto_categorize:
            return self._group_by_category(all_qa)
        else:
            # 단일 문서로
            doc = RAGDocument(
                title=f"{self.site_name} 지식베이스",
                category="general",
                site_name=self.site_name,
                source_url=self.base_url,
                qa_pairs=all_qa,
            )
            doc.to_markdown()
            return [doc]

    # ── 카테고리 분류 ──

    def _categorize_faq(self, faq: FAQItem) -> str:
        """FAQ 항목 자동 카테고리 분류"""
        text = f"{faq.question} {faq.answer}".lower()

        if any(kw in text for kw in ["배송", "택배", "발송", "반품", "교환", "환불", "반송"]):
            return "shipping"
        if any(kw in text for kw in ["설치", "오류", "에러", "작동", "연결", "업데이트", "다운로드"]):
            return "tech"
        if any(kw in text for kw in ["가격", "할인", "쿠폰", "포인트", "결제", "상품", "사이즈"]):
            return "product"
        if any(kw in text for kw in ["회원", "가입", "탈퇴", "로그인", "비밀번호", "이용", "약관"]):
            return "usage"
        if any(kw in text for kw in ["연락", "전화", "이메일", "고객센터", "상담"]):
            return "contact"

        return "faq"

    # ── 콘텐츠 유형별 Q&A 변환 ──

    def _policy_to_qa(self, policy: PolicyItem) -> list[QAPair]:
        """정책 콘텐츠 → Q&A 쌍 생성"""
        qa_pairs: list[QAPair] = []
        content = policy.content

        category = "shipping" if policy.policy_type in ("shipping", "return") else "usage"

        # 정책 유형별 기본 질문 생성
        policy_questions = {
            "shipping": [
                ("배송은 얼마나 걸리나요?", ["배송", "소요", "기간", "일"]),
                ("배송비는 얼마인가요?", ["배송비", "무료배송", "배송 비용"]),
                ("해외 배송도 가능한가요?", ["해외", "국제", "overseas"]),
            ],
            "return": [
                ("반품은 어떻게 하나요?", ["반품", "방법", "절차"]),
                ("교환은 어떻게 하나요?", ["교환", "방법"]),
                ("환불은 언제 되나요?", ["환불", "기간", "처리"]),
                ("반품 기한은 언제까지인가요?", ["기한", "기간", "일 이내"]),
            ],
            "terms": [
                ("이용약관은 어떻게 되나요?", ["이용", "약관"]),
            ],
            "privacy": [
                ("개인정보는 어떻게 처리되나요?", ["개인정보", "수집", "이용"]),
            ],
            "payment": [
                ("결제 방법은 어떤 것이 있나요?", ["결제", "카드", "계좌", "방법"]),
            ],
        }

        questions = policy_questions.get(policy.policy_type, [])

        for question, keywords in questions:
            # 관련 내용이 있는 경우만 Q&A 생성
            if any(kw in content for kw in keywords):
                # 관련 문단 추출
                answer = self._extract_relevant_text(content, keywords, max_len=500)
                if answer and len(answer) > 30:
                    qa_pairs.append(QAPair(
                        question=question,
                        answer=answer,
                        source_url=policy.source_url,
                        category=category,
                    ))

        # 전체 정책을 하나의 Q&A로도 추가
        if content and len(content) > 50:
            title_q = {
                "shipping": "배송 정책은 어떻게 되나요?",
                "return": "반품/교환 정책은 어떻게 되나요?",
                "terms": "이용약관 내용이 궁금합니다.",
                "privacy": "개인정보처리방침은 어떻게 되나요?",
                "payment": "결제 관련 안내를 알려주세요.",
            }
            q = title_q.get(policy.policy_type, f"{policy.title}에 대해 알려주세요.")
            qa_pairs.append(QAPair(
                question=q,
                answer=content[:1000],
                source_url=policy.source_url,
                category=category,
            ))

        return qa_pairs

    def _article_to_qa(self, article: ArticleItem) -> list[QAPair]:
        """도움말/가이드 → Q&A 쌍 생성"""
        qa_pairs: list[QAPair] = []

        # 제목으로부터 질문 생성
        title = article.title
        question_prefixes = {
            "guide": "에 대해 알려주세요.",
            "troubleshoot": "에 문제가 있을 때 어떻게 하나요?",
            "how-to": "하는 방법을 알려주세요.",
        }
        suffix = question_prefixes.get(article.article_type, "에 대해 알려주세요.")
        question = f"{title}{suffix}"

        if article.content and len(article.content) > 50:
            qa_pairs.append(QAPair(
                question=question,
                answer=article.content[:1000],
                source_url=article.source_url,
                category="tech" if article.article_type == "troubleshoot" else "usage",
            ))

        return qa_pairs

    def _product_to_qa(self, product: ProductItem) -> list[QAPair]:
        """상품 정보 → Q&A 쌍 생성"""
        qa_pairs: list[QAPair] = []

        # 상품 설명
        if product.description:
            qa_pairs.append(QAPair(
                question=f"{product.name}은(는) 어떤 상품인가요?",
                answer=product.description[:800],
                source_url=product.source_url,
                category="product",
            ))

        # 가격 정보
        if product.price:
            qa_pairs.append(QAPair(
                question=f"{product.name}의 가격은 얼마인가요?",
                answer=f"{product.name}의 가격은 {product.price}입니다.",
                source_url=product.source_url,
                category="product",
            ))

        # 스펙/사양
        if product.specs:
            specs_text = "\n".join(f"- {k}: {v}" for k, v in product.specs.items())
            qa_pairs.append(QAPair(
                question=f"{product.name}의 상세 사양을 알려주세요.",
                answer=f"{product.name} 상세 사양:\n{specs_text}",
                source_url=product.source_url,
                category="product",
            ))

        return qa_pairs

    def _contact_to_qa(self, contact: ContactInfo) -> list[QAPair]:
        """연락처 정보 → Q&A 쌍 생성"""
        qa_pairs: list[QAPair] = []

        parts: list[str] = []

        if contact.phone:
            parts.append(f"전화: {', '.join(contact.phone)}")
        if contact.email:
            parts.append(f"이메일: {', '.join(contact.email)}")
        if contact.business_hours:
            parts.append(f"운영시간: {contact.business_hours}")
        if contact.address:
            parts.append(f"주소: {contact.address}")

        if parts:
            qa_pairs.append(QAPair(
                question="고객센터 연락처를 알려주세요.",
                answer="\n".join(parts),
                source_url=contact.source_url,
                category="contact",
            ))

        if contact.business_hours:
            qa_pairs.append(QAPair(
                question="고객센터 운영시간은 언제인가요?",
                answer=f"고객센터 운영시간: {contact.business_hours}",
                source_url=contact.source_url,
                category="contact",
            ))

        return qa_pairs

    # ── 유틸리티 ──

    def _extract_relevant_text(
        self, content: str, keywords: list[str], max_len: int = 500
    ) -> str:
        """키워드와 관련된 문단을 추출"""
        paragraphs = content.split("\n")
        relevant: list[str] = []

        for i, para in enumerate(paragraphs):
            if any(kw in para for kw in keywords):
                # 해당 문단 + 앞뒤 1개 문단
                start = max(0, i - 1)
                end = min(len(paragraphs), i + 2)
                chunk = "\n".join(paragraphs[start:end])
                relevant.append(chunk.strip())

        result = "\n".join(relevant)
        return result[:max_len] if result else ""

    def _deduplicate(self, qa_pairs: list[QAPair]) -> list[QAPair]:
        """Q&A 중복 제거"""
        unique: list[QAPair] = []

        for qa in qa_pairs:
            h = hashlib.md5(
                re.sub(r"\s+", "", qa.question.lower()).encode()
            ).hexdigest()
            if h not in self._seen_hashes:
                self._seen_hashes.add(h)
                unique.append(qa)

        return unique

    def _group_by_category(self, qa_pairs: list[QAPair]) -> list[RAGDocument]:
        """카테고리별로 문서 그룹화"""
        groups: dict[str, list[QAPair]] = {}
        for qa in qa_pairs:
            groups.setdefault(qa.category, []).append(qa)

        documents: list[RAGDocument] = []
        for category, pairs in groups.items():
            cat_label = CATEGORIES.get(category, category)
            doc = RAGDocument(
                title=f"{cat_label} — {self.site_name}",
                category=category,
                site_name=self.site_name,
                source_url=self.base_url,
                qa_pairs=pairs,
            )
            doc.to_markdown()
            documents.append(doc)

        return documents
