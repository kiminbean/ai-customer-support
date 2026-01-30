"""
데이터 허브 레지스트리 — 큐레이션된 고객지원 데이터셋 목록

도메인별로 분류된 HuggingFace 데이터셋 메타데이터를 관리한다.
각 데이터셋은 품질 점수, 용도, 포맷 등 상세 정보를 포함.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# ── 도메인별 데이터셋 레지스트리 ───────────────────────────

DOMAIN_DATASETS: Dict[str, List[Dict]] = {
    "이커머스": [
        {
            "id": "NebulaByte/E-Commerce_Customer_Support_Conversations",
            "name": "이커머스 고객지원 대화",
            "description": "1,000개 이커머스 고객-상담원 대화 데이터",
            "size": "1K conversations",
            "language": "en",
            "format": "conversation",
            "quality_score": 4.5,
            "use_cases": ["FAQ 생성", "대화 학습", "의도 분류"],
        },
        {
            "id": "rjac/e-commerce-customer-support-qa",
            "name": "이커머스 고객지원 Q&A",
            "description": "1,000개 이커머스 질문-답변 쌍",
            "size": "1K QA pairs",
            "language": "en",
            "format": "qa",
            "quality_score": 4.0,
            "use_cases": ["RAG 지식베이스", "FAQ 자동생성"],
        },
        {
            "id": "dltdojo/ecommerce-faq-chatbot-dataset",
            "name": "이커머스 FAQ 챗봇 데이터",
            "description": "이커머스 FAQ 챗봇 훈련용 데이터",
            "size": "79 entries",
            "language": "en",
            "format": "qa",
            "quality_score": 3.5,
            "use_cases": ["FAQ 챗봇"],
        },
    ],
    "금융/은행": [
        {
            "id": "KAI-KratosAI/banking-customersupport-english-audio",
            "name": "은행 고객지원 (음성+텍스트)",
            "description": "은행 고객지원 대화 음성 및 텍스트 데이터",
            "size": "21 conversations",
            "language": "en",
            "format": "audio+text",
            "quality_score": 4.0,
            "use_cases": ["Voice-to-RAG", "금융 FAQ"],
        },
    ],
    "종합/멀티도메인": [
        {
            "id": "bitext/Bitext-customer-support-llm-chatbot-training-dataset",
            "name": "Bitext LLM 챗봇 훈련 데이터",
            "description": "26,900개 고객지원 의도-응답 쌍, 27개 의도 카테고리",
            "size": "26.9K entries",
            "language": "en",
            "format": "intent-response",
            "quality_score": 5.0,
            "use_cases": ["의도 분류", "응답 생성", "챗봇 훈련"],
        },
        {
            "id": "Lakshan2003/customer-support-client-agent-conversations",
            "name": "고객-상담원 대화 대규모 데이터",
            "description": "183,000개 고객-상담원 대화 데이터셋",
            "size": "183K conversations",
            "language": "en",
            "format": "conversation",
            "quality_score": 4.5,
            "use_cases": ["대화 분석", "응답 학습", "에이전트 훈련"],
        },
        {
            "id": "Tobi-Bueck/customer-support-tickets",
            "name": "고객지원 티켓 데이터",
            "description": "61,800개 고객지원 티켓 (분류, 우선순위, 해결)",
            "size": "61.8K tickets",
            "language": "en",
            "format": "ticket",
            "quality_score": 4.5,
            "use_cases": ["티켓 분류", "우선순위 예측", "자동 라우팅"],
        },
        {
            "id": "MakTek/Customer_support_faqs_dataset",
            "name": "고객지원 FAQ 데이터",
            "description": "200개 고객지원 FAQ 질문-답변",
            "size": "200 QA pairs",
            "language": "en",
            "format": "qa",
            "quality_score": 3.5,
            "use_cases": ["FAQ 지식베이스"],
        },
    ],
    "SNS/소셜미디어": [
        {
            "id": "TNE-AI/customer-support-on-twitter-conversation",
            "name": "트위터 고객지원 대화",
            "description": "794,000개 트위터 기반 고객지원 대화",
            "size": "794K conversations",
            "language": "en",
            "format": "conversation",
            "quality_score": 4.0,
            "use_cases": ["SNS 응대", "감성 분석", "실시간 응답"],
        },
        {
            "id": "MohammadOthman/mo-customer-support-tweets-945k",
            "name": "고객지원 트윗 대규모 데이터",
            "description": "945,000개 고객지원 트윗",
            "size": "945K tweets",
            "language": "en",
            "format": "tweet",
            "quality_score": 3.5,
            "use_cases": ["SNS 분석", "감성 분류"],
        },
    ],
    "의료/헬스케어": [
        {
            "id": "aibabyshark/insurance_customer_support_conversation",
            "name": "보험 고객지원 대화",
            "description": "보험 관련 고객지원 대화 데이터",
            "size": "100 conversations",
            "language": "en",
            "format": "conversation",
            "quality_score": 3.5,
            "use_cases": ["보험 FAQ", "의료 상담"],
        },
    ],
    "IT/SaaS": [
        {
            "id": "sutro/synthetic-customer-support-dialogues-20k",
            "name": "SaaS 고객지원 합성 대화",
            "description": "20,000개 기술지원 대화 (합성 데이터)",
            "size": "20K dialogues",
            "language": "en",
            "format": "conversation",
            "quality_score": 4.0,
            "use_cases": ["기술지원", "트러블슈팅"],
        },
    ],
}


# ── 조회 함수 ──────────────────────────────────────────────


def get_domains() -> List[Dict]:
    """
    전체 도메인 목록과 각 도메인의 데이터셋 개수를 반환한다.

    Returns:
        [{"domain": "이커머스", "dataset_count": 3, "total_quality": 12.0}, ...]
    """
    result = []
    for domain, datasets in DOMAIN_DATASETS.items():
        total_quality = sum(ds.get("quality_score", 0) for ds in datasets)
        avg_quality = total_quality / len(datasets) if datasets else 0
        result.append({
            "domain": domain,
            "dataset_count": len(datasets),
            "avg_quality_score": round(avg_quality, 1),
        })
    return result


def get_datasets_by_domain(domain: str) -> List[Dict]:
    """
    특정 도메인의 데이터셋 목록을 반환한다.

    Args:
        domain: 도메인 이름 (예: "이커머스", "금융/은행")

    Returns:
        해당 도메인의 데이터셋 리스트 (없으면 빈 리스트)
    """
    return DOMAIN_DATASETS.get(domain, [])


def get_dataset_info(dataset_id: str) -> Optional[Dict]:
    """
    데이터셋 ID로 상세 정보를 조회한다.

    Args:
        dataset_id: HuggingFace 데이터셋 ID (예: "bitext/Bitext-customer-support-llm-chatbot-training-dataset")

    Returns:
        데이터셋 정보 딕셔너리 또는 None
    """
    for domain, datasets in DOMAIN_DATASETS.items():
        for ds in datasets:
            if ds["id"] == dataset_id:
                return {**ds, "domain": domain}
    return None


def search_datasets(query: str) -> List[Dict]:
    """
    데이터셋을 검색한다 (이름, 설명, 용도, ID에서 키워드 매칭).

    Args:
        query: 검색어 (한국어 또는 영어)

    Returns:
        매칭되는 데이터셋 리스트 (도메인 정보 포함)
    """
    query_lower = query.lower()
    results = []

    for domain, datasets in DOMAIN_DATASETS.items():
        for ds in datasets:
            # 검색 대상 필드들
            searchable = " ".join([
                ds.get("id", ""),
                ds.get("name", ""),
                ds.get("description", ""),
                ds.get("format", ""),
                ds.get("size", ""),
                " ".join(ds.get("use_cases", [])),
            ]).lower()

            if query_lower in searchable:
                results.append({**ds, "domain": domain})

    # 품질 점수 기준 정렬
    results.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    return results


def get_all_datasets() -> List[Dict]:
    """
    전체 데이터셋 목록을 반환한다 (도메인 정보 포함).

    Returns:
        모든 데이터셋 리스트
    """
    results = []
    for domain, datasets in DOMAIN_DATASETS.items():
        for ds in datasets:
            results.append({**ds, "domain": domain})
    return results
