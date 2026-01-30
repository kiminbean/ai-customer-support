"""
벡터 임베딩 파이프라인
- 프로덕션: OpenAI Embeddings
- 데모 모드: scikit-learn TF-IDF 기반 임베딩 (API 키 불필요)
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

import config

# ── 데모용 TF-IDF 임베딩 ───────────────────────────────────

class TfidfEmbeddings:
    """
    API 키 없이 동작하는 TF-IDF 기반 임베딩.
    ChromaDB의 EmbeddingFunction 프로토콜을 따른다.
    """

    def __init__(self, dim: int = 384):
        self.dim = dim
        self._vectorizer = TfidfVectorizer(max_features=dim, analyzer="char_wb", ngram_range=(2, 4))
        self._fitted = False
        self._corpus: List[str] = []

    # ── ChromaDB EmbeddingFunction 프로토콜 ────────────────
    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.embed_documents(input)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """문서 리스트를 임베딩 벡터로 변환"""
        self._corpus.extend(texts)
        self._vectorizer.fit(self._corpus)
        self._fitted = True
        raw = self._vectorizer.transform(texts).toarray()
        return self._pad_or_truncate(raw).tolist()

    def embed_query(self, text: str) -> List[float]:
        """단일 쿼리를 임베딩 벡터로 변환"""
        if not self._fitted:
            # 코퍼스가 비어있으면 해시 기반 폴백
            return self._hash_embed(text)
        raw = self._vectorizer.transform([text]).toarray()
        return self._pad_or_truncate(raw)[0].tolist()

    # ── 내부 헬퍼 ──────────────────────────────────────────
    def _pad_or_truncate(self, arr: np.ndarray) -> np.ndarray:
        """차원을 self.dim에 맞춤"""
        n, d = arr.shape
        if d >= self.dim:
            return arr[:, : self.dim]
        padded = np.zeros((n, self.dim))
        padded[:, :d] = arr
        return padded

    @staticmethod
    def _hash_embed(text: str, dim: int = 384) -> List[float]:
        """해시 기반 결정적 임베딩 (폴백용)"""
        h = hashlib.sha256(text.encode()).hexdigest()
        nums = [int(h[i : i + 2], 16) / 255.0 for i in range(0, len(h), 2)]
        while len(nums) < dim:
            nums.extend(nums)
        return nums[:dim]


# ── 임베딩 팩토리 ──────────────────────────────────────────

def get_embedding_function():
    """
    설정에 따라 적절한 임베딩 함수를 반환.
    - OPENAI_API_KEY 있으면 → OpenAI Embeddings
    - 없으면 → TF-IDF 임베딩 (데모 모드)
    """
    if not config.DEMO_MODE:
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                openai_api_key=config.OPENAI_API_KEY,
                model="text-embedding-3-small",
            )
        except Exception:
            pass
    return TfidfEmbeddings()
