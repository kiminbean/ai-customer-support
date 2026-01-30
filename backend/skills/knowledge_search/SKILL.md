# Knowledge Search Skill

## 이름
knowledge_search — 지식 베이스 검색

## 설명
ChromaDB 벡터 스토어에서 고객 질문과 관련된 문서를 시맨틱 검색합니다.
RAG(Retrieval-Augmented Generation) 파이프라인의 핵심 스킬입니다.

## 입력
- `query` (string, 필수): 검색할 질문 또는 키워드
- `k` (integer, 선택, 기본값: 3): 반환할 최대 문서 수
- `min_similarity` (float, 선택, 기본값: 0.3): 최소 유사도 임계값

## 출력
```json
{
  "documents": [
    {
      "text": "문서 내용...",
      "metadata": {"source": "파일명", "chunk_index": 0},
      "score": 0.87
    }
  ],
  "total_found": 3
}
```

## 동작
1. 사용자 쿼리를 벡터 임베딩으로 변환
2. ChromaDB에서 코사인 유사도 기반 검색
3. 최소 유사도 이상인 문서만 필터링
4. 점수 내림차순으로 정렬하여 반환

## 데모 모드
- API 키 없이 TF-IDF 기반 임베딩 사용
- 동일한 인터페이스, 낮은 정확도

## 사용 에이전트
- `faq_agent`: FAQ 답변 생성 시 문서 검색
- `orchestrator`: 의도 분류 보조 정보
