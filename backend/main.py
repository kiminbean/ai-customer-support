"""
AI 고객지원 플랫폼 — FastAPI 백엔드
RAG + Deep Agents 기반 지능형 고객지원 시스템

실행: uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from agents.orchestrator import (
    get_analytics,
    get_conversation,
    list_conversations,
    process_message,
)
from crawler.routes import router as crawler_router
from rag.document_loader import delete_document, list_documents, load_file, load_sample_docs
from datahub.routes import router as datahub_router
from voice.routes import router as voice_router

# ── FastAPI 앱 ─────────────────────────────────────────────

app = FastAPI(
    title=config.APP_TITLE,
    version=config.APP_VERSION,
    description="RAG + Deep Agents 기반 AI 고객지원 API",
)

# 크롤러 라우터 등록
app.include_router(crawler_router)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터 허브 라우터 등록
app.include_router(datahub_router)

# 음성 라우터 등록
app.include_router(voice_router)


# ── Pydantic 모델 ─────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    conversation_id: str
    agent: str
    intent: str
    mode: str
    source_documents: Optional[List[dict]] = []
    escalation: Optional[dict] = None
    order_data: Optional[dict | list] = None


class SettingsRequest(BaseModel):
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tone: Optional[str] = None


# ── 시작 이벤트 ────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 샘플 문서 로드"""
    loaded = load_sample_docs()
    mode = "🎮 데모 모드" if config.DEMO_MODE else "🚀 프로덕션 모드"
    print(f"\n{'='*50}")
    print(f"  {config.APP_TITLE} v{config.APP_VERSION}")
    print(f"  모드: {mode}")
    print(f"  샘플 문서 로드: {loaded}개")
    print(f"{'='*50}\n")


# ── API 엔드포인트 ─────────────────────────────────────────

# 1. 채팅
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI 고객지원 채팅.
    사용자 메시지를 받아 적절한 에이전트가 응답을 생성한다.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해 주세요.")

    result = process_message(
        message=request.message,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        answer=result["answer"],
        confidence=result.get("confidence", 0.0),
        conversation_id=result.get("conversation_id", ""),
        agent=result.get("agent", "unknown"),
        intent=result.get("intent", "unknown"),
        mode=result.get("mode", "demo"),
        source_documents=result.get("source_documents", []),
        escalation=result.get("escalation"),
        order_data=result.get("order_data"),
    )


# 2. 문서 업로드
@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    지식 베이스 문서 업로드.
    지원 형식: .txt, .md, .pdf
    """
    # 확장자 검사
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".txt", ".md", ".pdf"):
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식: {suffix}. (.txt, .md, .pdf만 가능)",
        )

    # 파일명 sanitize (경로 순회 방지)
    safe_name = Path(file.filename or "").name  # 디렉토리 성분 제거
    if not safe_name:
        safe_name = f"upload_{uuid.uuid4()}{suffix}"
    save_path = config.UPLOAD_DIR / safe_name
    if not save_path.resolve().is_relative_to(config.UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=400, detail="잘못된 파일명입니다.")

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 벡터 스토어에 저장
    try:
        chunks = load_file(save_path)
        return {
            "status": "success",
            "filename": save_path.name,
            "chunks_created": len(chunks),
            "message": f"'{save_path.name}' 문서가 성공적으로 업로드되었습니다. ({len(chunks)}개 청크)",
        }
    except Exception as e:
        # 실패 시 파일 삭제
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"문서 처리 실패: {str(e)}")


# 3. 문서 목록
@app.get("/api/documents")
async def get_documents():
    """업로드된 문서 목록 조회"""
    docs = list_documents()
    return {
        "documents": docs,
        "total": len(docs),
    }


# 4. 문서 삭제
@app.delete("/api/documents/{doc_id}")
async def remove_document(doc_id: str):
    """문서 삭제 (소스명 기준)"""
    delete_document(doc_id)
    return {
        "status": "success",
        "message": f"'{doc_id}' 문서가 삭제되었습니다.",
    }


# 5. 대화 목록
@app.get("/api/conversations")
async def get_conversations():
    """대화 목록 조회"""
    convs = list_conversations()
    return {
        "conversations": convs,
        "total": len(convs),
    }


# 6. 대화 상세
@app.get("/api/conversations/{conv_id}")
async def get_conversation_detail(conv_id: str):
    """대화 이력 상세 조회"""
    conv = get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return conv


# 7. 분석
@app.get("/api/analytics")
async def analytics():
    """사용 분석 데이터"""
    return get_analytics()


# 8. 설정
@app.post("/api/settings")
async def update_settings(settings: SettingsRequest):
    """AI 설정 변경 (모델, 온도, 톤 등)"""
    if settings.model_name:
        if settings.model_name not in config.ALLOWED_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 모델입니다: {settings.model_name}. "
                       f"허용 모델: {', '.join(sorted(config.ALLOWED_MODELS))}",
            )
        config.MODEL_NAME = settings.model_name
    if settings.temperature is not None:
        config.TEMPERATURE = max(0.0, min(2.0, settings.temperature))
    if settings.max_tokens is not None:
        config.MAX_TOKENS = max(100, min(4096, settings.max_tokens))

    return {
        "status": "success",
        "settings": config.get_settings_dict(),
        "message": "설정이 업데이트되었습니다.",
    }


@app.get("/api/settings")
async def get_settings():
    """현재 설정 조회"""
    return config.get_settings_dict()


# 9. 헬스 체크
@app.get("/api/health")
async def health():
    """서비스 상태 확인"""
    docs = list_documents()
    return {
        "status": "healthy",
        "version": config.APP_VERSION,
        "demo_mode": config.DEMO_MODE,
        "model": config.MODEL_NAME,
        "documents_loaded": len(docs),
        "timestamp": datetime.now().isoformat(),
    }


# ── 로컬 실행 ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
