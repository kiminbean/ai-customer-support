"""
콘텐츠 추출기 — HTML에서 고객지원 데이터 지능형 추출

크롤링된 HTML 페이지에서 다음을 자동 감지·추출한다:
- FAQ / Q&A 섹션
- 상품 정보
- 도움말 / 가이드 문서
- 정책 (배송, 반품, 이용약관 등)
- 연락처 정보
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup, Tag


# ── 데이터 모델 ────────────────────────────────────────────


@dataclass
class FAQItem:
    """추출된 FAQ 항목"""
    question: str
    answer: str
    source_url: str = ""
    category: str = ""

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "answer": self.answer,
            "source_url": self.source_url,
            "category": self.category,
        }


@dataclass
class ArticleItem:
    """추출된 도움말/가이드 문서"""
    title: str
    content: str
    article_type: str = ""      # guide, troubleshoot, how-to
    source_url: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "article_type": self.article_type,
            "source_url": self.source_url,
        }


@dataclass
class ProductItem:
    """추출된 상품 정보"""
    name: str
    description: str = ""
    price: str = ""
    specs: dict = field(default_factory=dict)
    source_url: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "specs": self.specs,
            "source_url": self.source_url,
        }


@dataclass
class PolicyItem:
    """추출된 정책/안내 정보"""
    title: str
    content: str
    policy_type: str = ""       # shipping, return, terms, privacy
    source_url: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "policy_type": self.policy_type,
            "source_url": self.source_url,
        }


@dataclass
class ContactInfo:
    """추출된 연락처 정보"""
    phone: list[str] = field(default_factory=list)
    email: list[str] = field(default_factory=list)
    business_hours: str = ""
    address: str = ""
    source_url: str = ""

    def to_dict(self) -> dict:
        return {
            "phone": self.phone,
            "email": self.email,
            "business_hours": self.business_hours,
            "address": self.address,
            "source_url": self.source_url,
        }


@dataclass
class ExtractedContent:
    """하나의 페이지에서 추출된 모든 콘텐츠"""
    url: str
    title: str = ""
    faqs: list[FAQItem] = field(default_factory=list)
    articles: list[ArticleItem] = field(default_factory=list)
    products: list[ProductItem] = field(default_factory=list)
    policies: list[PolicyItem] = field(default_factory=list)
    contact: ContactInfo | None = None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "faqs": [f.to_dict() for f in self.faqs],
            "articles": [a.to_dict() for a in self.articles],
            "products": [p.to_dict() for p in self.products],
            "policies": [p.to_dict() for p in self.policies],
            "contact": self.contact.to_dict() if self.contact else None,
        }

    @property
    def total_items(self) -> int:
        return len(self.faqs) + len(self.articles) + len(self.products) + len(self.policies)


# ── FAQ 감지 패턴 ──────────────────────────────────────────

FAQ_HEADING_PATTERNS = [
    r"자주\s*묻는\s*질문",
    r"FAQ",
    r"Q\s*&\s*A",
    r"도움말",
    r"질문과\s*답변",
    r"자주\s*하는\s*질문",
    r"궁금한\s*점",
    r"frequently\s*asked",
    r"common\s*questions",
]

FAQ_CLASS_PATTERNS = [
    "faq", "accordion", "qa", "question", "answer",
    "help", "support", "toggle", "collapse",
]

POLICY_KEYWORDS = {
    "shipping": ["배송", "shipping", "delivery", "택배", "발송"],
    "return": ["반품", "교환", "환불", "return", "refund", "exchange"],
    "terms": ["이용약관", "이용 약관", "terms", "서비스 약관"],
    "privacy": ["개인정보", "privacy", "프라이버시"],
    "payment": ["결제", "payment", "카드", "계좌"],
}

ARTICLE_KEYWORDS = [
    "가이드", "guide", "how to", "사용법", "사용 방법", "설치",
    "설정", "튜토리얼", "tutorial", "시작하기", "getting started",
    "문제 해결", "troubleshoot", "오류", "에러",
]


# ── 추출기 ─────────────────────────────────────────────────


class ContentExtractor:
    """HTML에서 고객지원 콘텐츠를 지능적으로 추출"""

    def extract(self, html: str, url: str = "", title: str = "") -> ExtractedContent:
        """HTML 콘텐츠에서 모든 유형의 고객지원 데이터 추출"""
        soup = BeautifulSoup(html, "lxml")
        result = ExtractedContent(url=url, title=title)

        # 1. Schema.org FAQPage JSON-LD 데이터
        result.faqs.extend(self._extract_jsonld_faq(soup, url))

        # 2. HTML 구조 기반 FAQ 감지
        result.faqs.extend(self._extract_html_faq(soup, url))

        # 3. 정책 페이지 감지
        result.policies.extend(self._extract_policies(soup, url, title))

        # 4. 도움말/가이드 문서
        result.articles.extend(self._extract_articles(soup, url, title))

        # 5. 상품 정보
        result.products.extend(self._extract_products(soup, url))

        # 6. 연락처 정보
        contact = self._extract_contact(soup, url)
        if contact and (contact.phone or contact.email or contact.business_hours):
            result.contact = contact

        # FAQ 중복 제거
        result.faqs = self._deduplicate_faqs(result.faqs)

        return result

    # ── FAQ 추출 ──

    def _extract_jsonld_faq(self, soup: BeautifulSoup, url: str) -> list[FAQItem]:
        """Schema.org FAQPage JSON-LD 데이터에서 FAQ 추출"""
        faqs: list[FAQItem] = []

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, list):
                    for item in data:
                        faqs.extend(self._parse_jsonld_item(item, url))
                else:
                    faqs.extend(self._parse_jsonld_item(data, url))
            except (json.JSONDecodeError, TypeError):
                continue

        return faqs

    def _parse_jsonld_item(self, data: dict, url: str) -> list[FAQItem]:
        """JSON-LD 아이템에서 FAQ 추출"""
        faqs: list[FAQItem] = []
        schema_type = data.get("@type", "")

        if schema_type == "FAQPage":
            for entity in data.get("mainEntity", []):
                if entity.get("@type") == "Question":
                    q = entity.get("name", "")
                    a = ""
                    accepted = entity.get("acceptedAnswer", {})
                    if isinstance(accepted, dict):
                        a = accepted.get("text", "")
                    if q and a:
                        faqs.append(FAQItem(question=q, answer=a, source_url=url))

        return faqs

    def _extract_html_faq(self, soup: BeautifulSoup, url: str) -> list[FAQItem]:
        """HTML 구조에서 FAQ 패턴 감지하여 추출"""
        faqs: list[FAQItem] = []

        # 방법 1: dl/dt/dd 패턴
        faqs.extend(self._extract_dl_faq(soup, url))

        # 방법 2: details/summary 패턴
        faqs.extend(self._extract_details_faq(soup, url))

        # 방법 3: FAQ 관련 CSS 클래스를 가진 요소
        faqs.extend(self._extract_class_faq(soup, url))

        # 방법 4: FAQ 헤딩 아래 내용
        faqs.extend(self._extract_heading_faq(soup, url))

        return faqs

    def _extract_dl_faq(self, soup: BeautifulSoup, url: str) -> list[FAQItem]:
        """dl/dt/dd 패턴에서 FAQ 추출"""
        faqs: list[FAQItem] = []
        for dl in soup.find_all("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                q = dt.get_text(strip=True)
                a = dd.get_text(strip=True)
                if q and a and len(q) > 5:
                    faqs.append(FAQItem(question=q, answer=a, source_url=url))
        return faqs

    def _extract_details_faq(self, soup: BeautifulSoup, url: str) -> list[FAQItem]:
        """details/summary 패턴에서 FAQ 추출"""
        faqs: list[FAQItem] = []
        for details in soup.find_all("details"):
            summary = details.find("summary")
            if summary:
                q = summary.get_text(strip=True)
                # summary 이후의 텍스트를 답변으로
                summary.decompose()
                a = details.get_text(strip=True)
                if q and a and len(q) > 5:
                    faqs.append(FAQItem(question=q, answer=a, source_url=url))
        return faqs

    def _extract_class_faq(self, soup: BeautifulSoup, url: str) -> list[FAQItem]:
        """FAQ 관련 CSS 클래스를 가진 요소에서 추출"""
        faqs: list[FAQItem] = []

        # question + answer 쌍 찾기
        for pattern in FAQ_CLASS_PATTERNS:
            # question 클래스
            questions = soup.find_all(
                class_=lambda c: c and pattern in str(c).lower() and "question" in str(c).lower()
            )
            for q_el in questions:
                q = q_el.get_text(strip=True)
                # 다음 형제 요소에서 답변 찾기
                a_el = q_el.find_next_sibling()
                if a_el:
                    a = a_el.get_text(strip=True)
                    if q and a and len(q) > 5:
                        faqs.append(FAQItem(question=q, answer=a, source_url=url))

            # accordion 패턴
            accordions = soup.find_all(
                class_=lambda c: c and ("accordion" in str(c).lower() or "faq" in str(c).lower())
            )
            for accordion in accordions:
                # 아코디언 내부에서 제목+내용 쌍 찾기
                items = accordion.find_all(
                    class_=lambda c: c and ("item" in str(c).lower() or "panel" in str(c).lower())
                )
                if not items:
                    items = accordion.find_all(recursive=False)

                for item in items:
                    # 첫 번째 헤딩이나 버튼 = 질문
                    header = item.find(["h1", "h2", "h3", "h4", "h5", "h6", "button"])
                    if header:
                        q = header.get_text(strip=True)
                        header.decompose()
                        a = item.get_text(strip=True)
                        if q and a and len(q) > 5 and len(a) > 5:
                            faqs.append(FAQItem(question=q, answer=a, source_url=url))

        return faqs

    def _extract_heading_faq(self, soup: BeautifulSoup, url: str) -> list[FAQItem]:
        """FAQ 헤딩 아래의 Q&A 패턴 추출"""
        faqs: list[FAQItem] = []

        for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
            text = heading.get_text(strip=True).lower()
            is_faq_heading = any(
                re.search(p, text, re.IGNORECASE) for p in FAQ_HEADING_PATTERNS
            )
            if not is_faq_heading:
                continue

            # 이 헤딩 이후의 형제 요소에서 Q&A 추출
            current: Tag | None = heading.find_next_sibling()
            current_q: str = ""

            while current and current.name not in ["h1", "h2"]:
                el_text = current.get_text(strip=True)

                # Q: / 질문: 패턴
                if el_text and re.match(r"^(Q[:\.]|질문[:\.]|문[:\.])", el_text):
                    if current_q:
                        # 이전 질문이 있으면 빈 답변이라도 저장 안 함
                        pass
                    current_q = re.sub(r"^(Q[:\.]|질문[:\.]|문[:\.])\s*", "", el_text)

                elif el_text and re.match(r"^(A[:\.]|답변[:\.]|답[:\.])", el_text):
                    a = re.sub(r"^(A[:\.]|답변[:\.]|답[:\.])\s*", "", el_text)
                    if current_q and a:
                        faqs.append(FAQItem(question=current_q, answer=a, source_url=url))
                    current_q = ""

                # 번호 매긴 질문 패턴
                elif el_text and re.match(r"^\d+\.\s*", el_text) and "?" in el_text:
                    if current_q:
                        pass
                    current_q = re.sub(r"^\d+\.\s*", "", el_text)

                current = current.find_next_sibling()

        return faqs

    # ── 정책 추출 ──

    def _extract_policies(
        self, soup: BeautifulSoup, url: str, title: str
    ) -> list[PolicyItem]:
        """정책/안내 페이지 콘텐츠 추출"""
        policies: list[PolicyItem] = []
        combined = f"{title} {url}".lower()

        for policy_type, keywords in POLICY_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                # 본문 텍스트 추출
                body = soup.find("main") or soup.find("article") or soup.find("body")
                if body:
                    # 불필요한 요소 제거
                    for tag in body.find_all(["script", "style", "nav", "footer"]):
                        tag.decompose()
                    content = body.get_text(separator="\n", strip=True)
                    content = re.sub(r"\n{3,}", "\n\n", content)
                    if content and len(content) > 50:
                        policies.append(PolicyItem(
                            title=title or f"{policy_type} 정책",
                            content=content[:3000],
                            policy_type=policy_type,
                            source_url=url,
                        ))
                break  # 한 페이지에서 하나의 정책 유형만

        return policies

    # ── 도움말/가이드 추출 ──

    def _extract_articles(
        self, soup: BeautifulSoup, url: str, title: str
    ) -> list[ArticleItem]:
        """도움말/가이드 문서 추출"""
        articles: list[ArticleItem] = []
        combined = f"{title} {url}".lower()

        is_article = any(kw in combined for kw in ARTICLE_KEYWORDS)
        if not is_article:
            return articles

        # 기사 본문
        body = soup.find("article") or soup.find("main") or soup.find("body")
        if body:
            for tag in body.find_all(["script", "style", "nav", "footer"]):
                tag.decompose()
            content = body.get_text(separator="\n", strip=True)
            content = re.sub(r"\n{3,}", "\n\n", content)

            # 기사 유형 판별
            article_type = "guide"
            if any(k in combined for k in ["문제", "troubleshoot", "오류", "에러"]):
                article_type = "troubleshoot"
            elif any(k in combined for k in ["how to", "사용법", "방법"]):
                article_type = "how-to"

            if content and len(content) > 100:
                articles.append(ArticleItem(
                    title=title or "도움말 문서",
                    content=content[:3000],
                    article_type=article_type,
                    source_url=url,
                ))

        return articles

    # ── 상품 정보 추출 ──

    def _extract_products(self, soup: BeautifulSoup, url: str) -> list[ProductItem]:
        """상품 정보 추출 (JSON-LD + HTML)"""
        products: list[ProductItem] = []

        # Schema.org Product JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, dict) and data.get("@type") == "Product":
                    name = data.get("name", "")
                    desc = data.get("description", "")
                    price = ""
                    offers = data.get("offers", {})
                    if isinstance(offers, dict):
                        price = f"{offers.get('price', '')} {offers.get('priceCurrency', '')}".strip()
                    if name:
                        products.append(ProductItem(
                            name=name, description=desc, price=price, source_url=url,
                        ))
            except (json.JSONDecodeError, TypeError):
                continue

        # 상품 관련 HTML 구조 감지
        product_elements = soup.find_all(
            class_=lambda c: c and any(
                kw in str(c).lower()
                for kw in ["product", "item", "goods", "상품"]
            )
        )
        for el in product_elements[:5]:  # 최대 5개
            name_el = el.find(["h1", "h2", "h3"])
            if name_el:
                name = name_el.get_text(strip=True)
                desc = el.get_text(strip=True)[:500]
                # 가격 패턴
                price_match = re.search(r"[\d,]+\s*원", el.get_text())
                price = price_match.group() if price_match else ""
                if name and len(name) > 2:
                    products.append(ProductItem(
                        name=name, description=desc, price=price, source_url=url,
                    ))

        return products

    # ── 연락처 추출 ──

    def _extract_contact(self, soup: BeautifulSoup, url: str) -> ContactInfo:
        """연락처 정보 추출"""
        contact = ContactInfo(source_url=url)
        full_text = soup.get_text()

        # 전화번호
        phone_patterns = [
            r"(?:전화|TEL|Tel|☎|📞)[:\s]*([0-9\-]+(?:\s*~\s*[0-9\-]+)?)",
            r"(\d{2,3}[-\s]?\d{3,4}[-\s]?\d{4})",
            r"(1\d{3}[-\s]?\d{4})",  # 대표번호
        ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, full_text)
            for m in matches:
                phone = m.strip()
                if len(phone) >= 8 and phone not in contact.phone:
                    contact.phone.append(phone)

        # 이메일
        email_pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, full_text)
        contact.email = list(set(emails))[:5]

        # 영업시간
        hour_patterns = [
            r"(?:영업시간|운영시간|상담시간|고객센터\s*운영)[:\s]*([^\n]{5,50})",
            r"(?:평일|월~금|월요일)[:\s]*([^\n]{5,50})",
        ]
        for pattern in hour_patterns:
            match = re.search(pattern, full_text)
            if match:
                contact.business_hours = match.group(1).strip()
                break

        # 주소
        addr_patterns = [
            r"(?:주소|Address)[:\s]*([^\n]{10,100})",
        ]
        for pattern in addr_patterns:
            match = re.search(pattern, full_text)
            if match:
                contact.address = match.group(1).strip()
                break

        return contact

    # ── 유틸리티 ──

    @staticmethod
    def _deduplicate_faqs(faqs: list[FAQItem]) -> list[FAQItem]:
        """FAQ 중복 제거 (질문 텍스트 유사도 기반)"""
        seen: set[str] = set()
        unique: list[FAQItem] = []

        for faq in faqs:
            # 정규화: 공백/구두점 제거 후 비교
            key = re.sub(r"[\s?？.。!！,，]", "", faq.question.lower())
            if key not in seen and len(key) > 3:
                seen.add(key)
                unique.append(faq)

        return unique
