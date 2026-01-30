"""
시맨틱 검색 리트리버
InMemoryVectorStore에서 유사 문서를 검색한다.
"""

from __future__ import annotations

from typing import Dict, List

import config
from rag.vector_store import get_store


# ── 문서 추가 ──────────────────────────────────────────────

def add_documents(
    texts: List[str],
    metadatas: List[Dict] | None = None,
    ids: List[str] | None = None,
) -> List[str]:
    """텍스트 청크를 벡터 스토어에 추가"""
    store = get_store()
    return store.add(texts=texts, metadatas=metadatas, ids=ids)


# ── 시맨틱 검색 ────────────────────────────────────────────

def search(
    query: str,
    k: int = config.RETRIEVAL_K,
    min_similarity: float = config.MIN_SIMILARITY,
) -> List[Dict]:
    """
    쿼리와 유사한 문서를 검색.
    Returns: [{text, metadata, score, id}, ...]
    """
    store = get_store()
    return store.search(query=query, k=k, min_similarity=min_similarity)


# ── 문서 삭제 ──────────────────────────────────────────────

def delete_by_source(source: str):
    """특정 소스의 모든 문서를 삭제"""
    store = get_store()
    store.delete_by_source(source)


def delete_by_ids(ids: List[str]):
    """ID로 문서 삭제"""
    store = get_store()
    store.delete_by_ids(ids)


# ── 문서 목록 ──────────────────────────────────────────────

def list_sources() -> List[Dict]:
    """저장된 모든 소스(문서)를 나열"""
    store = get_store()
    return store.list_sources()
