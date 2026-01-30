"""
문서 업로드 및 처리 파이프라인
- 지원 형식: TXT, MD, PDF
- 텍스트 분할 → 메타데이터 추출 → 벡터 스토어 저장
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
from rag import retriever

# ── 텍스트 분할기 ──────────────────────────────────────────

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
    separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
)


# ── 문서 처리 ──────────────────────────────────────────────

def load_text_content(
    content: str,
    source: str,
    metadata: Optional[Dict] = None,
) -> List[Dict]:
    """
    텍스트 콘텐츠를 직접 받아 벡터 스토어에 저장.
    크롤러 등 외부 모듈에서 RAG 가져오기 시 사용하는 진입점.
    """
    doc_type = (metadata or {}).get("doc_type", "text")
    return load_text(content, source=source, doc_type=doc_type)


def load_text(text: str, source: str, doc_type: str = "text") -> List[Dict]:
    """
    원시 텍스트를 청크로 분할하여 벡터 스토어에 저장.
    Returns: 저장된 청크 정보 리스트
    """
    chunks = _splitter.split_text(text)
    metadatas = [
        {
            "source": source,
            "doc_type": doc_type,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "uploaded_at": datetime.now().isoformat(),
        }
        for i in range(len(chunks))
    ]
    ids = retriever.add_documents(texts=chunks, metadatas=metadatas)
    return [
        {"id": ids[i], "source": source, "chunk_index": i, "length": len(c)}
        for i, c in enumerate(chunks)
    ]


def load_file(file_path: Path) -> List[Dict]:
    """
    파일을 읽어 벡터 스토어에 저장.
    지원: .txt, .md, .pdf
    """
    suffix = file_path.suffix.lower()
    source = file_path.name

    if suffix in (".txt", ".md"):
        text = file_path.read_text(encoding="utf-8")
        doc_type = "markdown" if suffix == ".md" else "text"
        return load_text(text, source=source, doc_type=doc_type)

    elif suffix == ".pdf":
        text = _extract_pdf_text(file_path)
        return load_text(text, source=source, doc_type="pdf")

    else:
        raise ValueError(f"지원하지 않는 파일 형식: {suffix}")


def _extract_pdf_text(file_path: Path) -> str:
    """PDF에서 텍스트 추출 (PyPDF2 또는 폴백)"""
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    except ImportError:
        # PyPDF2 미설치 시 간단한 텍스트 추출 시도
        return file_path.read_text(encoding="utf-8", errors="ignore")


# ── 샘플 문서 로드 ─────────────────────────────────────────

def load_sample_docs() -> int:
    """data/sample_docs/ 내 모든 문서를 벡터 스토어에 로드"""
    loaded = 0
    sample_dir = config.SAMPLE_DOCS_DIR
    if not sample_dir.exists():
        return 0

    # 이미 로드된 소스 확인
    existing = {s["source"] for s in retriever.list_sources()}

    for f in sorted(sample_dir.iterdir()):
        if f.suffix.lower() in (".txt", ".md", ".pdf") and f.name not in existing:
            try:
                load_file(f)
                loaded += 1
            except Exception as e:
                print(f"[문서 로드 실패] {f.name}: {e}")
    return loaded


# ── 문서 관리 ──────────────────────────────────────────────

def list_documents() -> List[Dict]:
    """업로드된 문서 목록"""
    return retriever.list_sources()


def delete_document(source: str):
    """문서 삭제 (소스명 기준)"""
    retriever.delete_by_source(source)
    # 업로드 파일도 삭제
    upload_path = config.UPLOAD_DIR / source
    if upload_path.exists():
        upload_path.unlink()
