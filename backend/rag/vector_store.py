"""
인메모리 벡터 스토어 — ChromaDB 대체
Python 3.14 호환, 외부 의존성 없음.
scikit-learn TF-IDF + 코사인 유사도 기반.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config

# ── 벡터 스토어 클래스 ─────────────────────────────────────

class InMemoryVectorStore:
    """
    TF-IDF 기반 인메모리 벡터 스토어.
    - 문서 추가/삭제
    - 코사인 유사도 검색
    - JSON 파일로 영속화
    """

    def __init__(self, persist_path: Optional[Path] = None):
        self._documents: Dict[str, Dict] = {}  # id → {text, metadata}
        self._vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            max_features=5000,
        )
        self._matrix = None
        self._ids_order: List[str] = []
        self._fitted = False
        self._persist_path = persist_path or (config.DATA_DIR / "vector_store.json")

        # 저장된 데이터 로드
        self._load()

    # ── 문서 추가 ──────────────────────────────────────────

    def add(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """텍스트와 메타데이터를 스토어에 추가"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        if metadatas is None:
            metadatas = [{} for _ in texts]

        for i, text in enumerate(texts):
            self._documents[ids[i]] = {
                "text": text,
                "metadata": metadatas[i],
            }

        self._rebuild_index()
        self._save()
        return ids

    # ── 검색 ───────────────────────────────────────────────

    def search(
        self,
        query: str,
        k: int = 3,
        min_similarity: float = 0.0,
    ) -> List[Dict]:
        """코사인 유사도 기반 검색"""
        if not self._fitted or not self._ids_order:
            return []

        query_vec = self._vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self._matrix)[0]

        # 상위 k개 선택
        indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in indices:
            score = float(similarities[idx])
            if score < min_similarity:
                continue
            doc_id = self._ids_order[idx]
            doc = self._documents[doc_id]
            results.append({
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": round(score, 4),
                "id": doc_id,
            })
        return results

    # ── 삭제 ───────────────────────────────────────────────

    def delete_by_ids(self, ids: List[str]):
        """ID로 문서 삭제"""
        for doc_id in ids:
            self._documents.pop(doc_id, None)
        self._rebuild_index()
        self._save()

    def delete_by_source(self, source: str):
        """소스명으로 문서 삭제"""
        to_delete = [
            doc_id for doc_id, doc in self._documents.items()
            if doc["metadata"].get("source") == source
        ]
        for doc_id in to_delete:
            del self._documents[doc_id]
        self._rebuild_index()
        self._save()

    # ── 조회 ───────────────────────────────────────────────

    def count(self) -> int:
        return len(self._documents)

    def list_sources(self) -> List[Dict]:
        """저장된 소스(문서) 목록"""
        sources: Dict[str, Dict] = {}
        for doc_id, doc in self._documents.items():
            src = doc["metadata"].get("source", "unknown")
            if src not in sources:
                sources[src] = {
                    "source": src,
                    "chunk_count": 0,
                    "doc_type": doc["metadata"].get("doc_type", "unknown"),
                }
            sources[src]["chunk_count"] += 1
        return list(sources.values())

    def get_all(self) -> Dict:
        """전체 문서 반환"""
        return dict(self._documents)

    # ── 인덱스 재구축 ─────────────────────────────────────

    def _rebuild_index(self):
        """TF-IDF 인덱스 재구축"""
        if not self._documents:
            self._fitted = False
            self._matrix = None
            self._ids_order = []
            return

        self._ids_order = list(self._documents.keys())
        texts = [self._documents[doc_id]["text"] for doc_id in self._ids_order]
        self._matrix = self._vectorizer.fit_transform(texts)
        self._fitted = True

    # ── 영속화 ─────────────────────────────────────────────

    def _save(self):
        """JSON으로 저장"""
        try:
            data = {
                doc_id: {"text": doc["text"], "metadata": doc["metadata"]}
                for doc_id, doc in self._documents.items()
            }
            self._persist_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning("벡터 스토어 저장 실패: %s", e)

    def _load(self):
        """JSON에서 로드"""
        try:
            if self._persist_path.exists():
                data = json.loads(self._persist_path.read_text(encoding="utf-8"))
                self._documents = data
                self._rebuild_index()
        except Exception as e:
            logger.warning("벡터 스토어 로드 실패 (빈 스토어로 시작): %s", e)


# ── 싱글턴 인스턴스 ────────────────────────────────────────

_store: Optional[InMemoryVectorStore] = None


def get_store() -> InMemoryVectorStore:
    """벡터 스토어 싱글턴 반환"""
    global _store
    if _store is None:
        _store = InMemoryVectorStore()
    return _store


def reset_store():
    """스토어 리셋 (테스트용)"""
    global _store
    _store = None
