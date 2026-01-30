"""
FAQ 에이전트 — RAG 기반 지식 검색
벡터 스토어에서 관련 문서를 검색하고 답변을 생성한다.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import config
from rag.retriever import search

# ── 데모 모드 키워드 매핑 (한국어) ─────────────────────────

_DEMO_RESPONSES = {
    "배송": {
        "answer": "국내 배송은 결제 완료 후 1~3 영업일 이내에 발송되며, "
                  "도서산간 지역은 1~2일 추가 소요될 수 있습니다. "
                  "해외 배송은 7~14 영업일이 소요됩니다. "
                  "배송 조회는 마이페이지 > 주문내역에서 확인 가능합니다.",
        "confidence": 0.85,
    },
    "반품": {
        "answer": "상품 수령 후 7일 이내에 반품 신청이 가능합니다. "
                  "단, 고객 단순 변심의 경우 반품 배송비(편도 3,000원)가 부과됩니다. "
                  "상품 하자 시 무료 반품이 가능하며, 환불은 반품 상품 확인 후 "
                  "3~5 영업일 내에 처리됩니다.",
        "confidence": 0.82,
    },
    "교환": {
        "answer": "교환은 동일 상품의 색상/사이즈 변경만 가능하며, "
                  "상품 수령 후 7일 이내에 신청해 주세요. "
                  "교환 배송비는 고객 부담이며, 상품 하자 시 무료입니다.",
        "confidence": 0.80,
    },
    "환불": {
        "answer": "환불은 반품 상품이 물류센터에 도착하여 검수 완료 후 처리됩니다. "
                  "카드 결제 시 3~5 영업일, 무통장입금 시 1~2 영업일 이내에 "
                  "환불 금액이 입금됩니다.",
        "confidence": 0.83,
    },
    "회원": {
        "answer": "회원 가입은 이메일 또는 소셜 계정(카카오, 네이버, 구글)으로 "
                  "가능합니다. 신규 가입 시 2,000원 적립금이 지급되며, "
                  "비밀번호 분실 시 '비밀번호 찾기'에서 재설정할 수 있습니다.",
        "confidence": 0.78,
    },
    "포인트": {
        "answer": "포인트는 상품 구매 확정 시 결제 금액의 1%가 적립됩니다. "
                  "적립된 포인트는 1,000포인트 이상부터 사용 가능하며, "
                  "유효기간은 적립일로부터 1년입니다.",
        "confidence": 0.81,
    },
    "쿠폰": {
        "answer": "쿠폰은 마이페이지 > 쿠폰함에서 확인 가능합니다. "
                  "다른 할인과 중복 적용은 불가하며, "
                  "유효기간이 지난 쿠폰은 자동 소멸됩니다.",
        "confidence": 0.79,
    },
    "결제": {
        "answer": "결제 수단은 신용카드, 체크카드, 무통장입금, 카카오페이, "
                  "네이버페이, 토스 등을 지원합니다. "
                  "결제 오류 시 브라우저 캐시 삭제 후 재시도하거나 "
                  "고객센터로 문의해 주세요.",
        "confidence": 0.80,
    },
}


# ── FAQ 에이전트 ───────────────────────────────────────────

def handle(query: str, conversation_id: Optional[str] = None) -> Dict:
    """
    FAQ 쿼리 처리.
    1) RAG 검색으로 관련 문서 조회
    2) 문서 기반 답변 생성 (데모 모드: 키워드 매칭)
    """
    # 1. RAG 검색
    docs = search(query, k=config.RETRIEVAL_K)

    # 2. 답변 생성
    if not config.DEMO_MODE:
        return _llm_answer(query, docs)
    else:
        return _demo_answer(query, docs)


def _demo_answer(query: str, docs: List[Dict]) -> Dict:
    """데모 모드: 키워드 매칭 + 검색 결과 조합"""
    # 키워드 매칭
    for keyword, resp in _DEMO_RESPONSES.items():
        if keyword in query:
            return {
                "answer": resp["answer"],
                "confidence": resp["confidence"],
                "source_documents": docs[:3],
                "agent": "faq_agent",
                "mode": "demo",
            }

    # 검색 결과가 있으면 문서 내용 기반 답변
    if docs:
        top_doc = docs[0]
        snippet = top_doc["text"][:300]
        return {
            "answer": f"관련 정보를 찾았습니다:\n\n{snippet}...\n\n"
                      f"더 자세한 내용은 고객센터(1588-0000)로 문의해 주세요.",
            "confidence": top_doc["score"],
            "source_documents": docs[:3],
            "agent": "faq_agent",
            "mode": "demo",
        }

    # 폴백
    return {
        "answer": "죄송합니다, 해당 질문에 대한 정보를 찾지 못했습니다. "
                  "고객센터(1588-0000)로 문의해 주시면 빠르게 도와드리겠습니다.",
        "confidence": 0.2,
        "source_documents": [],
        "agent": "faq_agent",
        "mode": "demo",
    }


def _llm_answer(query: str, docs: List[Dict]) -> Dict:
    """프로덕션 모드: LLM 기반 답변 생성"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate

        context = "\n\n---\n\n".join([d["text"] for d in docs]) if docs else "관련 문서 없음"

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "당신은 친절한 한국어 고객지원 AI입니다. "
                "아래 참고 문서를 바탕으로 고객의 질문에 정확하고 친절하게 답변하세요. "
                "문서에 없는 내용은 추측하지 말고, 고객센터 연락을 안내하세요.\n\n"
                "참고 문서:\n{context}"
            )),
            ("human", "{query}"),
        ])

        llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            openai_api_key=config.OPENAI_API_KEY,
        )

        chain = prompt | llm
        result = chain.invoke({"context": context, "query": query})

        avg_score = sum(d["score"] for d in docs) / len(docs) if docs else 0.5

        return {
            "answer": result.content,
            "confidence": round(avg_score, 4),
            "source_documents": docs[:3],
            "agent": "faq_agent",
            "mode": "production",
        }
    except Exception as e:
        return {
            "answer": f"답변 생성 중 오류가 발생했습니다: {str(e)}",
            "confidence": 0.0,
            "source_documents": docs[:3],
            "agent": "faq_agent",
            "mode": "error",
        }
