"""
데모 모드 — 샘플 크롤링 결과 데이터

실제 크롤링 없이 오프라인으로 동작하는 데모 데이터.
가상의 이커머스 사이트 "스마트몰"의 FAQ, 상품정보, 정책 등을 포함한다.

30+ Q&A 쌍을 다양한 카테고리로 제공.
"""

from __future__ import annotations

from datetime import date

from crawler.extractor import (
    ArticleItem,
    ContactInfo,
    ExtractedContent,
    FAQItem,
    PolicyItem,
    ProductItem,
)
from crawler.rag_converter import QAPair, RAGConverter, RAGDocument


DEMO_SITE_NAME = "스마트몰"
DEMO_SITE_URL = "https://www.smartmall.co.kr"


# ── 데모 추출 결과 ─────────────────────────────────────────


def get_demo_results() -> list[ExtractedContent]:
    """데모 크롤링 결과 반환 (오프라인, 즉시 사용 가능)"""

    pages: list[ExtractedContent] = []

    # ── 1. FAQ 페이지 ──

    faq_page = ExtractedContent(
        url=f"{DEMO_SITE_URL}/faq",
        title="자주 묻는 질문 — 스마트몰",
        faqs=[
            FAQItem(
                question="주문 후 배송까지 얼마나 걸리나요?",
                answer="일반배송은 결제 완료 후 2~3영업일, 빠른배송은 당일 또는 익일 도착합니다. "
                       "도서산간 지역은 1~2일 추가 소요될 수 있습니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="배송",
            ),
            FAQItem(
                question="배송비는 얼마인가요?",
                answer="3만원 이상 구매 시 무료배송이며, 3만원 미만 주문 시 배송비 3,000원이 부과됩니다. "
                       "제주/도서산간 지역은 추가 배송비 3,000원이 발생합니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="배송",
            ),
            FAQItem(
                question="반품/교환은 어떻게 하나요?",
                answer="상품 수령 후 7일 이내에 마이페이지 > 주문내역에서 반품/교환 신청이 가능합니다. "
                       "단, 고객 변심의 경우 반품 배송비 5,000원(왕복)이 부과됩니다. "
                       "상품 하자의 경우 배송비는 스마트몰이 부담합니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="반품/교환",
            ),
            FAQItem(
                question="환불은 언제 처리되나요?",
                answer="반품 상품이 물류센터에 도착하여 검수 완료 후 1~3영업일 내 환불 처리됩니다. "
                       "카드 결제의 경우 카드사 처리 기간에 따라 3~7일 추가 소요될 수 있습니다. "
                       "현금 결제(무통장입금)는 환불 계좌로 입금됩니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="반품/교환",
            ),
            FAQItem(
                question="회원 가입은 어떻게 하나요?",
                answer="홈페이지 우측 상단 '회원가입' 버튼을 클릭하시면 됩니다. "
                       "이메일, 카카오, 네이버 계정으로 간편 가입이 가능합니다. "
                       "가입 시 2,000원 적립금을 드립니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="회원",
            ),
            FAQItem(
                question="비밀번호를 잊어버렸어요.",
                answer="로그인 페이지에서 '비밀번호 찾기'를 클릭하시면 가입 시 등록한 이메일로 "
                       "비밀번호 재설정 링크가 발송됩니다. 10분 이내에 메일이 도착하지 않으면 "
                       "스팸함을 확인해 주세요.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="회원",
            ),
            FAQItem(
                question="적립금은 어떻게 사용하나요?",
                answer="주문 시 결제 단계에서 보유 적립금을 사용할 수 있습니다. "
                       "최소 사용 금액은 1,000원이며, 상품 금액의 최대 10%까지 사용 가능합니다. "
                       "적립금 유효기간은 적립일로부터 1년입니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="결제",
            ),
            FAQItem(
                question="결제 수단은 어떤 것이 있나요?",
                answer="신용카드, 체크카드, 무통장입금, 카카오페이, 네이버페이, 토스페이를 지원합니다. "
                       "신용카드는 최대 12개월 무이자 할부가 가능합니다 (카드사별 상이).",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="결제",
            ),
            FAQItem(
                question="주문을 취소하고 싶어요.",
                answer="배송 시작 전이라면 마이페이지 > 주문내역에서 직접 취소가 가능합니다. "
                       "'배송중' 상태라면 고객센터(1588-0000)로 연락해 주세요. "
                       "취소 완료 후 결제 수단에 따라 1~7영업일 내 환불됩니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="주문",
            ),
            FAQItem(
                question="배송 조회는 어떻게 하나요?",
                answer="마이페이지 > 주문내역에서 해당 주문의 '배송조회' 버튼을 클릭하시면 "
                       "실시간 배송 상태를 확인할 수 있습니다. 송장번호가 등록되면 "
                       "카카오 알림톡으로도 안내해 드립니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="배송",
            ),
            FAQItem(
                question="해외 배송도 가능한가요?",
                answer="현재 스마트몰은 국내 배송만 지원하고 있습니다. "
                       "해외 배송 서비스는 2025년 하반기 오픈 예정입니다. "
                       "해외에서 구매를 원하시면 배송 대행 서비스를 이용해 주세요.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="배송",
            ),
            FAQItem(
                question="쿠폰은 어떻게 사용하나요?",
                answer="결제 시 쿠폰 입력란에 쿠폰 코드를 입력하거나, "
                       "마이쿠폰함에서 보유 쿠폰을 선택하여 적용하실 수 있습니다. "
                       "쿠폰은 중복 사용이 불가하며, 최소 주문 금액 조건이 있을 수 있습니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="결제",
            ),
            FAQItem(
                question="상품이 품절이에요. 재입고 알림을 받을 수 있나요?",
                answer="품절 상품 페이지에서 '재입고 알림 신청' 버튼을 클릭하시면 "
                       "상품이 재입고될 때 카카오 알림톡과 이메일로 알려드립니다.",
                source_url=f"{DEMO_SITE_URL}/faq",
                category="상품",
            ),
        ],
    )
    pages.append(faq_page)

    # ── 2. 배송 정책 페이지 ──

    shipping_page = ExtractedContent(
        url=f"{DEMO_SITE_URL}/policy/shipping",
        title="배송 안내 — 스마트몰",
        policies=[
            PolicyItem(
                title="배송 안내",
                content=(
                    "■ 배송 방법\n"
                    "- 일반배송: CJ대한통운 (2~3영업일)\n"
                    "- 빠른배송: 당일/익일 배송 (서울/경기 지역, 오후 2시 이전 주문)\n\n"
                    "■ 배송비\n"
                    "- 3만원 이상 구매 시 무료배송\n"
                    "- 3만원 미만: 3,000원\n"
                    "- 제주/도서산간: 추가 3,000원\n\n"
                    "■ 배송 추적\n"
                    "- 상품 발송 후 카카오 알림톡으로 송장번호를 안내드립니다.\n"
                    "- 마이페이지 > 주문내역에서 실시간 배송 조회가 가능합니다.\n\n"
                    "■ 주의사항\n"
                    "- 공휴일/주말에는 배송이 진행되지 않습니다.\n"
                    "- 일부 대형 상품은 별도 배송비가 부과될 수 있습니다.\n"
                    "- 천재지변, 물류 사정에 따라 배송이 지연될 수 있습니다."
                ),
                policy_type="shipping",
                source_url=f"{DEMO_SITE_URL}/policy/shipping",
            ),
        ],
    )
    pages.append(shipping_page)

    # ── 3. 반품/교환 정책 페이지 ──

    return_page = ExtractedContent(
        url=f"{DEMO_SITE_URL}/policy/return",
        title="반품/교환 안내 — 스마트몰",
        policies=[
            PolicyItem(
                title="반품/교환 안내",
                content=(
                    "■ 반품/교환 기간\n"
                    "- 상품 수령 후 7일 이내 신청 가능\n"
                    "- 상품 하자의 경우 수령 후 30일 이내\n\n"
                    "■ 반품/교환 방법\n"
                    "1. 마이페이지 > 주문내역에서 반품/교환 신청\n"
                    "2. 반품 사유 선택 및 상세 내용 입력\n"
                    "3. 수거 기사 방문 (1~2영업일 이내)\n"
                    "4. 물류센터 도착 후 검수 (1~2영업일)\n"
                    "5. 환불 또는 교환 상품 발송\n\n"
                    "■ 반품 배송비\n"
                    "- 고객 변심: 왕복 5,000원 (고객 부담)\n"
                    "- 상품 하자/오배송: 무료 (스마트몰 부담)\n\n"
                    "■ 반품 불가 사유\n"
                    "- 사용 흔적이 있는 상품\n"
                    "- 포장이 훼손된 상품\n"
                    "- 세탁 또는 수선한 상품\n"
                    "- 반품 기한이 초과된 상품"
                ),
                policy_type="return",
                source_url=f"{DEMO_SITE_URL}/policy/return",
            ),
        ],
    )
    pages.append(return_page)

    # ── 4. 상품 페이지들 ──

    product_page = ExtractedContent(
        url=f"{DEMO_SITE_URL}/products/smart-air-purifier",
        title="스마트 공기청정기 Pro — 스마트몰",
        products=[
            ProductItem(
                name="스마트 공기청정기 Pro",
                description=(
                    "헤파 H13 필터 탑재 프리미엄 공기청정기. "
                    "40평형까지 사용 가능하며, 스마트폰 앱으로 원격 제어가 가능합니다. "
                    "PM2.5, 포름알데히드 실시간 수치 표시. "
                    "저소음 수면 모드 (25dB)로 취침 시에도 쾌적하게."
                ),
                price="329,000원",
                specs={
                    "적용 면적": "최대 40평",
                    "필터": "HEPA H13 + 활성탄 복합 필터",
                    "소음": "수면모드 25dB / 최대 52dB",
                    "크기": "280 x 280 x 650mm",
                    "무게": "8.5kg",
                    "소비전력": "50W",
                    "필터 수명": "약 12개월",
                },
                source_url=f"{DEMO_SITE_URL}/products/smart-air-purifier",
            ),
        ],
    )
    pages.append(product_page)

    product_page2 = ExtractedContent(
        url=f"{DEMO_SITE_URL}/products/wireless-earbuds",
        title="프리미엄 무선이어폰 SmartBuds — 스마트몰",
        products=[
            ProductItem(
                name="프리미엄 무선이어폰 SmartBuds",
                description=(
                    "액티브 노이즈 캔슬링(ANC) 탑재 무선이어폰. "
                    "총 30시간 재생 (이어폰 8시간 + 충전케이스 22시간). "
                    "IPX5 방수 등급으로 운동 시에도 안심. "
                    "블루투스 5.3 지원, 멀티포인트 연결 가능."
                ),
                price="89,000원",
                specs={
                    "드라이버": "10mm 다이나믹 드라이버",
                    "블루투스": "5.3",
                    "배터리": "이어폰 8시간 / 케이스 포함 30시간",
                    "방수": "IPX5",
                    "무게": "5.2g (이어폰 한쪽)",
                    "코덱": "AAC, SBC, aptX",
                    "ANC": "하이브리드 액티브 노이즈 캔슬링",
                },
                source_url=f"{DEMO_SITE_URL}/products/wireless-earbuds",
            ),
        ],
    )
    pages.append(product_page2)

    # ── 5. 도움말/가이드 페이지 ──

    guide_page = ExtractedContent(
        url=f"{DEMO_SITE_URL}/help/smart-air-purifier-guide",
        title="스마트 공기청정기 사용 가이드 — 스마트몰",
        articles=[
            ArticleItem(
                title="스마트 공기청정기 Pro 사용 가이드",
                content=(
                    "■ 초기 설정\n"
                    "1. 박스에서 본체를 꺼내고 보호 필름을 제거합니다.\n"
                    "2. 뒷면 필터 커버를 열고 필터의 비닐 포장을 제거합니다.\n"
                    "3. 전원 코드를 연결합니다.\n"
                    "4. 전원 버튼을 3초간 길게 누르면 부팅됩니다.\n\n"
                    "■ 앱 연동\n"
                    "1. 'SmartMall Home' 앱을 설치합니다 (iOS/Android).\n"
                    "2. 앱에서 '기기 추가' > '공기청정기'를 선택합니다.\n"
                    "3. 본체 상단의 Wi-Fi 버튼을 5초간 길게 눌러 페어링 모드를 활성화합니다.\n"
                    "4. 앱의 안내에 따라 Wi-Fi 연결을 완료합니다.\n\n"
                    "■ 필터 교체\n"
                    "- 필터 교체 주기: 약 12개월 (사용환경에 따라 다름)\n"
                    "- 앱에서 필터 잔여 수명을 확인할 수 있습니다.\n"
                    "- 교체 시 전원을 끄고 뒷면 커버를 열어 교체합니다.\n\n"
                    "■ 문제 해결\n"
                    "- 전원이 안 켜져요: 전원 코드 연결 상태를 확인하세요.\n"
                    "- Wi-Fi 연결이 안 돼요: 2.4GHz 네트워크만 지원합니다. 5GHz는 지원하지 않습니다.\n"
                    "- 소음이 크게 느껴져요: 필터 교체 시기인지 확인하세요."
                ),
                article_type="guide",
                source_url=f"{DEMO_SITE_URL}/help/smart-air-purifier-guide",
            ),
        ],
    )
    pages.append(guide_page)

    # ── 6. 고객센터 페이지 ──

    contact_page = ExtractedContent(
        url=f"{DEMO_SITE_URL}/contact",
        title="고객센터 — 스마트몰",
        faqs=[
            FAQItem(
                question="고객센터 운영시간이 어떻게 되나요?",
                answer="평일 오전 9시~오후 6시 (점심 12시~1시 제외). "
                       "주말 및 공휴일은 휴무이며, 카카오톡 챗봇은 24시간 이용 가능합니다.",
                source_url=f"{DEMO_SITE_URL}/contact",
                category="고객센터",
            ),
            FAQItem(
                question="1:1 문의는 어디서 하나요?",
                answer="마이페이지 > 1:1 문의에서 문의글을 작성하시면 "
                       "평균 24시간 이내에 답변을 드립니다. "
                       "긴급한 문의는 전화(1588-0000)로 연락해 주세요.",
                source_url=f"{DEMO_SITE_URL}/contact",
                category="고객센터",
            ),
        ],
        contact=ContactInfo(
            phone=["1588-0000", "02-1234-5678"],
            email=["cs@smartmall.co.kr", "help@smartmall.co.kr"],
            business_hours="평일 09:00~18:00 (점심 12:00~13:00 제외), 주말/공휴일 휴무",
            address="서울특별시 강남구 테헤란로 123 스마트빌딩 5층",
            source_url=f"{DEMO_SITE_URL}/contact",
        ),
    )
    pages.append(contact_page)

    # ── 7. 추가 FAQ (이용안내) ──

    usage_page = ExtractedContent(
        url=f"{DEMO_SITE_URL}/help/membership",
        title="멤버십 안내 — 스마트몰",
        faqs=[
            FAQItem(
                question="멤버십 등급은 어떻게 결정되나요?",
                answer="최근 6개월 누적 구매 금액에 따라 매월 1일 자동 산정됩니다.\n"
                       "- 실버: 가입 즉시\n"
                       "- 골드: 30만원 이상\n"
                       "- VIP: 100만원 이상\n"
                       "- VVIP: 300만원 이상\n"
                       "등급별 추가 적립, 쿠폰, 무료배송 등 혜택이 제공됩니다.",
                source_url=f"{DEMO_SITE_URL}/help/membership",
                category="멤버십",
            ),
            FAQItem(
                question="포인트 적립률은 얼마인가요?",
                answer="기본 적립률은 구매 금액의 1%이며, 멤버십 등급에 따라 추가 적립됩니다.\n"
                       "- 실버: 1%\n"
                       "- 골드: 2%\n"
                       "- VIP: 3%\n"
                       "- VVIP: 5%\n"
                       "리뷰 작성 시 추가 500포인트, 사진 리뷰 시 1,000포인트가 적립됩니다.",
                source_url=f"{DEMO_SITE_URL}/help/membership",
                category="멤버십",
            ),
            FAQItem(
                question="회원 탈퇴는 어떻게 하나요?",
                answer="마이페이지 > 회원정보 > 회원탈퇴에서 탈퇴할 수 있습니다. "
                       "탈퇴 시 보유 적립금, 쿠폰은 모두 소멸되며 복구가 불가합니다. "
                       "진행 중인 주문이 있을 경우 탈퇴가 제한됩니다.",
                source_url=f"{DEMO_SITE_URL}/help/membership",
                category="회원",
            ),
        ],
        articles=[
            ArticleItem(
                title="스마트몰 앱 사용 가이드",
                content=(
                    "스마트몰 앱을 설치하면 더 편리하게 쇼핑할 수 있습니다.\n\n"
                    "■ 앱 설치\n"
                    "- iOS: App Store에서 '스마트몰' 검색\n"
                    "- Android: Google Play에서 '스마트몰' 검색\n\n"
                    "■ 주요 기능\n"
                    "- 바코드 스캔으로 빠른 상품 검색\n"
                    "- 실시간 배송 알림 (푸시 알림)\n"
                    "- 앱 전용 할인 쿠폰\n"
                    "- 간편결제 (지문/Face ID)\n"
                    "- AR로 가구/인테리어 미리보기"
                ),
                article_type="guide",
                source_url=f"{DEMO_SITE_URL}/help/membership",
            ),
        ],
    )
    pages.append(usage_page)

    return pages


# ── 데모 RAG 문서 변환 ─────────────────────────────────────


def get_demo_documents() -> list[RAGDocument]:
    """데모 추출 결과를 RAG 문서로 변환하여 반환"""
    converter = RAGConverter(site_name=DEMO_SITE_NAME, base_url=DEMO_SITE_URL)
    results = get_demo_results()
    documents = converter.convert(results, auto_categorize=True)
    return documents


# ── 요약 통계 ──────────────────────────────────────────────


def get_demo_summary() -> dict:
    """데모 결과 요약 통계"""
    results = get_demo_results()

    total_faqs = sum(len(p.faqs) for p in results)
    total_articles = sum(len(p.articles) for p in results)
    total_products = sum(len(p.products) for p in results)
    total_policies = sum(len(p.policies) for p in results)
    has_contact = any(p.contact for p in results)

    documents = get_demo_documents()
    total_qa = sum(len(d.qa_pairs) for d in documents)

    return {
        "site_name": DEMO_SITE_NAME,
        "site_url": DEMO_SITE_URL,
        "pages_crawled": len(results),
        "total_faqs": total_faqs,
        "total_articles": total_articles,
        "total_products": total_products,
        "total_policies": total_policies,
        "has_contact": has_contact,
        "total_extracted_items": total_faqs + total_articles + total_products + total_policies,
        "rag_documents": len(documents),
        "total_qa_pairs": total_qa,
        "categories": [d.category for d in documents],
    }
