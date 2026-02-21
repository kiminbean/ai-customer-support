# AI Customer Support Platform - API 문서

## 기본 정보

- **Base URL**: `http://localhost:8000`
- **인증**: `X-API-Key` 헤더 (선택)
- **포맷**: JSON

---

## 인증

API 키가 설정된 경우, 모든 요청에 `X-API-Key` 헤더를 포함해야 합니다.

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/health
```

---

## 엔드포인트

### 채팅

#### POST /api/chat

AI 고객지원 채팅 메시지를 전송합니다.

**요청 본문:**
```json
{
  "message": "배송 상태를 확인하고 싶습니다.",
  "conversation_id": "선택적 대화 ID"
}
```

**응답:**
```json
{
  "answer": "주문번호를 알려주시면 배송 상태를 확인해 드리겠습니다.",
  "confidence": 0.95,
  "conversation_id": "conv-123",
  "agent": "faq_agent",
  "intent": "FAQ",
  "mode": "demo",
  "source_documents": [
    {
      "title": "배송 안내",
      "content": "...",
      "score": 0.92
    }
  ]
}
```

---

### 문서 관리

#### POST /api/documents/upload

지식 베이스에 문서를 업로드합니다.

**지원 형식**: `.txt`, `.md`, `.pdf`

**요청**: `multipart/form-data`
- `file`: 업로드할 파일

**응답:**
```json
{
  "status": "success",
  "filename": "faq.txt",
  "chunks_created": 15,
  "message": "'faq.txt' 문서가 성공적으로 업로드되었습니다. (15개 청크)"
}
```

#### GET /api/documents

업로드된 문서 목록을 조회합니다.

**쿼리 파라미터:**
- `page`: 페이지 번호 (기본: 1)
- `limit`: 페이지당 항목 수 (기본: 50)

**응답:**
```json
{
  "documents": [
    {
      "id": "doc-1",
      "filename": "faq.txt",
      "uploaded_at": "2024-01-01T00:00:00",
      "chunk_count": 15
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50,
  "total_pages": 1
}
```

#### DELETE /api/documents/{doc_id}

문서를 삭제합니다.

---

### 대화 관리

#### GET /api/conversations

대화 목록을 조회합니다.

**쿼리 파라미터:**
- `page`: 페이지 번호 (기본: 1)
- `limit`: 페이지당 항목 수 (기본: 20)

#### GET /api/conversations/{conv_id}

특정 대화의 상세 정보를 조회합니다.

---

### 분석

#### GET /api/analytics

사용 분석 데이터를 조회합니다.

**응답:**
```json
{
  "total_conversations": 12847,
  "avg_response_time": "0.3초",
  "satisfaction_rate": "95%",
  "active_chats": 24,
  "ai_resolution_rate": 87.3,
  "escalation_rate": 12.7
}
```

---

### 설정

#### GET /api/settings

현재 AI 설정을 조회합니다.

#### POST /api/settings

AI 설정을 변경합니다.

**요청 본문:**
```json
{
  "model_name": "gpt-4o",
  "temperature": 0.5,
  "max_tokens": 2048
}
```

---

### 헬스 체크

#### GET /api/health

서비스 상태를 확인합니다.

**응답:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "demo_mode": true,
  "model": "gpt-4o-mini",
  "documents_loaded": 5,
  "timestamp": "2024-01-01T00:00:00"
}
```

---

## 서브 모듈 API

### 크롤러 (/api/crawler/*)

| Method | Path | 설명 |
|--------|------|------|
| POST | /start | 크롤링 시작 |
| GET | /status/{job_id} | 크롤링 상태 확인 |
| GET | /results/{job_id} | 크롤링 결과 조회 |
| POST | /results/{job_id}/import | 결과를 지식 베이스에 가져오기 |

### 데이터 허브 (/api/datahub/*)

| Method | Path | 설명 |
|--------|------|------|
| GET | /domains | 도메인 목록 |
| GET | /datasets | 데이터셋 목록 |
| POST | /download | 데이터셋 다운로드 |
| POST | /process | 데이터셋 처리 |
| POST | /import | 지식 베이스에 가져오기 |

### 음성 (/api/voice/*)

| Method | Path | 설명 |
|--------|------|------|
| POST | /upload | 음성 파일 업로드 |
| GET | /status/{job_id} | 처리 상태 확인 |
| GET | /transcript/{job_id} | 전사 결과 조회 |
| GET | /document/{job_id} | 생성된 문서 조회 |

---

## 에러 응답

모든 에러는 다음 형식을 따릅니다:

```json
{
  "detail": "에러 메시지"
}
```

### HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 404 | 리소스 없음 |
| 413 | 요청 크기 초과 |
| 429 | 요청 한도 초과 |
| 500 | 서버 오류 |

---

## Rate Limiting

- 기본: 60회/분
- 채팅: 30회/분
- 업로드: 10회/분
- 백업 생성: 2회/시간
