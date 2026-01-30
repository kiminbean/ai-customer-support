# Order Lookup Skill

## 이름
order_lookup — 주문 조회

## 설명
주문번호 또는 고객 정보로 주문 상태, 배송 추적, 반품/환불 현황을 조회합니다.

## 입력
- `order_id` (string, 선택): 주문번호 (예: ORD-2024-001)
- `query` (string, 선택): 자연어 주문 관련 질문

## 출력
```json
{
  "order_data": {
    "order_id": "ORD-2024-001",
    "status": "배송중",
    "product": "상품명",
    "tracking_number": "CJ1234567890",
    "carrier": "CJ대한통운"
  },
  "answer": "주문 상태 안내 메시지...",
  "confidence": 0.95
}
```

## 동작
1. 쿼리에서 주문번호 패턴(ORD-YYYY-NNN) 추출
2. 주문번호가 있으면 상세 조회
3. 없으면 키워드 기반 안내 (반품, 교환, 취소 등)
4. 주문 상태별 맞춤 메시지 생성

## 데모 모드
- 미리 정의된 목업 주문 데이터 사용
- 4개의 샘플 주문 (배송중, 배송완료, 결제완료, 반품처리중)

## 사용 에이전트
- `order_agent`: 주문 관련 모든 쿼리 처리
