"""
시맨틱 검색 리트리버
ChromaDB 벡터 스토어에서 유사 문서를 검색한다.
"""

from __future__ import annotations

import uuid
from typing import Dict, List, Optional

import chromadb

import config
from rag.embeddings import get_embedding_function

# ── 싱글턴 ChromaDB 클라이언트 ─────────────────────────────

_client: Optional[chromadb.PersistentClient] = None
_collection = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(config.CHROMA_DB_DIR))
    return _client


def get_collection():
    """knowledge_base 컬렉션을 반환 (없으면 생성)"""
    global _collection
    if _collection is None:
        client = _get_client()
        ef = get_embedding_function()
        _collection = client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def reset_collection():
    """컬렉션 캐시 초기화 (테스트용)"""
    global _collection
    _collection = None


# ── 문서 추가 ──────────────────────────────────────────────

def add_documents(
    texts: List[str],
    metadatas: Optional[List[Dict]] = None,
    ids: Optional[List[str]] = None,
) -> List[str]:
    """
    텍스트 청크를 벡터 스토어에 추가.
    Returns: 저장된 문서 ID 리스트
    """
    col = get_collection()
    if ids is None:
        ids = [str(uuid.uuid4()) for _ in texts]
    if metadatas is None:
        metadatas = [{} for _ in texts]
    col.add(documents=texts, metadatas=metadatas, ids=ids)
    return ids


# ── 시맨틱 검색 ────────────────────────────────────────────

def search(
    query: str,
    k: int = config.RETRIEVAL_K,
    min_similarity: float = config.MIN_SIMILARITY,
) -> List[Dict]:
    """
    쿼리와 유사한 문서를 검색.
    Returns: [{text, metadata, score}, ...]  (score = 1 - distance, 높을수록 유사)
    """
    col = get_collection()
    if col.count() == 0:
        return []

    results = col.query(query_texts=[query], n_results=min(k, col.count()))

    documents = []
    for i, doc_text in enumerate(results["documents"][0]):
        distance = results["distances"][0][i] if results.get("distances") else 0.5
        score = 1.0 - distance  # cosine distance → similarity
        if score < min_similarity:
            continue
        documents.append({
            "text": doc_text,
            "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
            "score": round(score, 4),
            "id": results["ids"][0][i] if results.get("ids") else "",
        })
    return documents


# ── 문서 삭제 ──────────────────────────────────────────────

def delete_by_source(source: str):
    """특정 소스의 모든 문서를 삭제"""
    col = get_collection()
    try:
        col.delete(where={"source": source})
    except Exception:
        pass  # 소스가 없으면 무시


def delete_by_ids(ids: List[str]):
    """ID로 문서 삭제"""
    col = get_collection()
    col.delete(ids=ids)


def list_sources() -> List[Dict]:
    """저장된 모든 소스(문서)를 나열"""
    col = get_collection()
    if col.count() == 0:
        return []
    all_data = col.get()
    sources: Dict[str, Dict] = {}
    for i, meta in enumerate(all_data["metadatas"]):
        src = meta.get("source", "unknown")
        if src not in sources:
            sources[src] = {
                "source": src,
                "chunk_count": 0,
                "doc_type": meta.get("doc_type", "unknown"),
            }
        sources[src]["chunk_count"] += 1
    return list(sources.values())
