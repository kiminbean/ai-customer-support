import type { CrawlResults, CrawlJob } from "@/lib/api";

export const MOCK_CRAWL_RESULTS: CrawlResults = {
  pages: 47,
  faqs: [
    { question: "배송은 얼마나 걸리나요?", answer: "일반배송 2-3일, 제주/도서산간 3-5일 소요됩니다.", sourceUrl: "https://example.com/faq" },
    { question: "반품은 어떻게 하나요?", answer: "수령 후 7일 이내 마이페이지에서 반품 신청 가능합니다.", sourceUrl: "https://example.com/faq" },
    { question: "교환 절차는 어떻게 되나요?", answer: "반품 신청 후 새 상품으로 재주문하거나, 고객센터에서 동일 상품 교환이 가능합니다.", sourceUrl: "https://example.com/faq" },
    { question: "배송비는 얼마인가요?", answer: "3만원 이상 무료배송, 미만 시 3,000원 부과됩니다.", sourceUrl: "https://example.com/faq" },
    { question: "주문 취소는 어떻게 하나요?", answer: "배송 준비 전까지 마이페이지에서 취소 가능합니다. 이후에는 고객센터로 연락해주세요.", sourceUrl: "https://example.com/faq" },
    { question: "포인트는 어떻게 적립되나요?", answer: "구매 확정 시 결제금액의 1%가 자동 적립됩니다.", sourceUrl: "https://example.com/faq/point" },
    { question: "회원 등급은 어떻게 올라가나요?", answer: "최근 6개월 구매금액에 따라 브론즈/실버/골드/VIP로 자동 변경됩니다.", sourceUrl: "https://example.com/faq/membership" },
    { question: "쿠폰은 중복 사용이 가능한가요?", answer: "쿠폰은 주문 당 1개만 사용 가능합니다. 단, 적립금과는 중복 사용 가능합니다.", sourceUrl: "https://example.com/faq/coupon" },
    { question: "해외 배송이 가능한가요?", answer: "현재 해외 배송은 지원하지 않습니다. 추후 서비스 예정입니다.", sourceUrl: "https://example.com/faq" },
    { question: "결제 수단은 어떤 것이 있나요?", answer: "신용카드, 체크카드, 네이버페이, 카카오페이, 토스페이, 무통장입금을 지원합니다.", sourceUrl: "https://example.com/faq/payment" },
    { question: "비회원 주문이 가능한가요?", answer: "네, 비회원 주문이 가능합니다. 단, 포인트 적립 및 회원 혜택은 제공되지 않습니다.", sourceUrl: "https://example.com/faq" },
    { question: "영수증 발급은 어디서 하나요?", answer: "마이페이지 > 주문내역에서 전자영수증 출력이 가능합니다.", sourceUrl: "https://example.com/faq/receipt" },
  ],
  articles: [
    { title: "회원가입 방법", content: "1. 홈페이지 우측 상단 '회원가입' 클릭\n2. 이메일 또는 소셜 계정으로 가입\n3. 본인인증 완료 후 가입 완료\n4. 가입 즉시 2,000원 쿠폰 발급", sourceUrl: "https://example.com/help/signup" },
    { title: "주문 방법 안내", content: "상품 선택 → 장바구니 담기 → 주문서 작성 → 결제 완료. 주문 확인 이메일이 자동 발송됩니다.", sourceUrl: "https://example.com/help/order" },
    { title: "배송 조회 방법", content: "마이페이지 > 주문내역에서 배송 상태를 확인할 수 있습니다. 운송장 번호 클릭 시 택배사 추적 페이지로 이동합니다.", sourceUrl: "https://example.com/help/delivery" },
    { title: "비밀번호 재설정", content: "로그인 페이지에서 '비밀번호 찾기' 클릭 후, 가입 이메일로 재설정 링크가 발송됩니다.", sourceUrl: "https://example.com/help/password" },
    { title: "앱 설치 안내", content: "앱스토어 또는 플레이스토어에서 'SupportAI Shop'을 검색하여 설치하세요. 앱 전용 할인 혜택이 제공됩니다.", sourceUrl: "https://example.com/help/app" },
    { title: "포인트 사용 방법", content: "주문서 결제 단계에서 보유 포인트를 입력하여 사용할 수 있습니다. 최소 1,000포인트부터 사용 가능합니다.", sourceUrl: "https://example.com/help/point" },
  ],
  products: [
    { name: "프리미엄 무선 이어폰 Pro", description: "노이즈 캔슬링, 48시간 배터리, IPX5 방수. 고해상도 오디오 코덱 지원.", sourceUrl: "https://example.com/product/earphone-pro" },
    { name: "스마트 공기청정기 S200", description: "AI 자동 모드, HEPA 13 필터, 60평형 커버리지. 실시간 공기질 모니터링.", sourceUrl: "https://example.com/product/air-purifier" },
    { name: "에르고 메시 의자 V3", description: "인체공학 설계, 메시 시트, 4D 팔걸이 조절. 허리 받침 높이 조절 가능.", sourceUrl: "https://example.com/product/ergo-chair" },
    { name: "울트라 슬림 노트북 15", description: "14세대 i7, 16GB RAM, 512GB SSD, 1.2kg 초경량. 20시간 배터리.", sourceUrl: "https://example.com/product/laptop-15" },
  ],
  policies: [
    { title: "개인정보 처리방침", content: "당사는 「개인정보 보호법」에 따라 이용자의 개인정보를 보호하고 관련된 고충을 신속하고 원활하게 처리할 수 있도록 다음과 같이 개인정보 처리방침을 수립·공개합니다.", sourceUrl: "https://example.com/policy/privacy" },
    { title: "이용약관", content: "본 약관은 SupportAI Shop(이하 '회사')이 제공하는 온라인 쇼핑 서비스의 이용조건 및 절차에 관한 기본사항을 규정합니다.", sourceUrl: "https://example.com/policy/terms" },
    { title: "반품/교환/환불 정책", content: "상품 수령 후 7일 이내 반품 가능. 고객 변심 시 배송비 부담. 상품 하자 시 무료 반품. 환불은 반품 완료 후 3영업일 이내 처리.", sourceUrl: "https://example.com/policy/return" },
    { title: "배송 정책", content: "평일 오후 2시 이전 주문 시 당일 출고. 배송 소요일: 수도권 1-2일, 기타 지역 2-3일, 제주/도서산간 3-5일.", sourceUrl: "https://example.com/policy/shipping" },
    { title: "포인트 정책", content: "구매 확정 시 결제금액의 1% 적립. 유효기간 12개월. 최소 사용 단위 1,000P. 탈퇴 시 소멸.", sourceUrl: "https://example.com/policy/point" },
  ],
};

export const MOCK_CRAWL_JOBS: CrawlJob[] = [
  { job_id: "mock-1", url: "https://shop.example.com", status: "completed", created_at: "2025-01-15T09:30:00Z", pages_crawled: 47, items_found: 32 },
  { job_id: "mock-2", url: "https://help.example.co.kr", status: "completed", created_at: "2025-01-14T14:20:00Z", pages_crawled: 23, items_found: 15 },
  { job_id: "mock-3", url: "https://faq.mystore.com", status: "failed", created_at: "2025-01-13T11:00:00Z", pages_crawled: 3, items_found: 0 },
];
