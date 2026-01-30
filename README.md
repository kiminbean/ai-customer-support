# AI Customer Support Platform

> RAG + Deep Agents 기반 AI 고객지원 SaaS 플랫폼

---

## 현재 구현 상태

| 기능 | 상태 | 설명 |
|------|------|------|
| AI 채팅 | 구현 완료 | RAG 검색 + 의도 분류 + 에이전트 라우팅 |
| 지식베이스 | 구현 완료 | TXT/MD/PDF 업로드, TF-IDF 벡터 검색 |
| 웹 크롤러 | 구현 완료 | URL 입력 → FAQ/콘텐츠 추출 → RAG 가져오기 |
| 데이터 허브 | 구현 완료 | HuggingFace 데이터셋 탐색/다운로드/변환 |
| 음성 파이프라인 | 구현 완료 | 음성 → STT → Q&A 문서 생성 |
| 관리 대시보드 | 구현 완료 | 통계, 대화 관리, 지식베이스, 설정 |
| 데모 모드 | 구현 완료 | API 키 없이 모든 기능 동작 |

---

## 기술 스택

### Backend
| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.14 | 백엔드 언어 |
| FastAPI | 0.115 | REST API 서버 |
| scikit-learn | 1.6+ | TF-IDF 벡터 검색 (RAG) |
| LangChain | 0.3+ | 텍스트 분할, LLM 연동 |
| Pydantic | 2.x | 요청/응답 모델 검증 |

### Frontend
| 기술 | 버전 | 용도 |
|------|------|------|
| Next.js | 16 | React 프레임워크 |
| React | 19 | UI 라이브러리 |
| TypeScript | strict | 타입 안전성 |
| Tailwind CSS | v4 | 스타일링 |

### 저장소
- 인메모리 + JSON 파일 영속화 (MVP 단계)
- 벡터 스토어: TF-IDF + cosine similarity

---

## 프로젝트 구조

```
ai-customer-support/
├── app/                          # Next.js 16 프론트엔드
│   ├── src/app/                  # App Router 페이지
│   │   ├── page.tsx              # 랜딩 페이지
│   │   ├── demo/page.tsx         # 채팅 데모
│   │   ├── dashboard/page.tsx    # 관리 대시보드
│   │   ├── datahub/page.tsx      # 데이터 허브
│   │   ├── crawler/page.tsx      # 웹 크롤러
│   │   └── widget/page.tsx       # 위젯 미리보기
│   └── src/lib/api.ts            # 백엔드 API 클라이언트
│
├── backend/                      # FastAPI 백엔드
│   ├── main.py                   # 앱 진입점 + 라우트 등록
│   ├── config.py                 # 설정 (환경변수, 경로, RAG 파라미터)
│   ├── agents/                   # Deep Agent (orchestrator → sub-agents)
│   ├── rag/                      # RAG 파이프라인 (loader → retriever → vector_store)
│   ├── crawler/                  # 웹 크롤링 → 콘텐츠 추출 → RAG 변환
│   ├── datahub/                  # HuggingFace 데이터셋 탐색/처리/가져오기
│   ├── voice/                    # 음성 → STT → Q&A 문서 생성
│   └── tests/                    # 통합 테스트 (FastAPI TestClient)
│
└── docs/                         # 사업 문서
    ├── 사업계획서.md
    ├── 시장분석.md
    └── 경쟁사_분석.md
```

---

## 시작하기

### 사전 요구사항

- Python 3.12+
- Node.js 20+

### Backend 설정

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 환경변수 설정 (선택 — 없으면 데모 모드)
cp .env.example .env
# .env 파일에서 OPENAI_API_KEY 설정 (선택)

# 서버 실행
uvicorn main:app --reload --port 8000
```

Swagger 문서: http://localhost:8000/docs

### Frontend 설정

```bash
cd app
npm install
npm run dev
```

http://localhost:3000 에서 접속

### 데모 모드

**API 키 없이도 모든 기능이 동작합니다.**
- 채팅: 한국어 키워드 기반 자동 응답 (배송, 반품, 교환 등)
- 크롤러: SmartMall 데모 데이터
- 데이터 허브: 샘플 데이터셋
- 음성: 데모 통화 녹취록

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/chat` | AI 채팅 (의도 분류 → 에이전트 라우팅) |
| POST | `/api/documents/upload` | 문서 업로드 (.txt, .md, .pdf) |
| GET | `/api/documents` | 문서 목록 |
| GET | `/api/conversations` | 대화 목록 |
| GET | `/api/analytics` | 분석 통계 |
| GET | `/api/health` | 헬스 체크 |
| | `/api/crawler/*` | 웹 크롤링 (9개 엔드포인트) |
| | `/api/datahub/*` | 데이터 허브 (12개 엔드포인트) |
| | `/api/voice/*` | 음성 파이프라인 (7개 엔드포인트) |

전체 API 문서: http://localhost:8000/docs

---

## 테스트

```bash
cd backend
source venv/bin/activate
pytest -v                    # 전체 테스트
pytest tests/test_api.py     # API 통합 테스트
```

---

## 사업 문서

| 문서 | 링크 |
|------|------|
| 사업계획서 | [docs/사업계획서.md](docs/사업계획서.md) |
| 시장분석 | [docs/시장분석.md](docs/시장분석.md) |
| 경쟁사 분석 | [docs/경쟁사_분석.md](docs/경쟁사_분석.md) |
| 기술 아키텍처 | [docs/기술_아키텍처.md](docs/기술_아키텍처.md) |
| 수익모델/재무전망 | [docs/수익모델_재무전망.md](docs/수익모델_재무전망.md) |
| GTM 전략 | [docs/GTM_전략.md](docs/GTM_전략.md) |
| 실행 로드맵 | [docs/실행_로드맵.md](docs/실행_로드맵.md) |
| 피치덱 스크립트 | [docs/피치덱_스크립트.md](docs/피치덱_스크립트.md) |
| 법률/규제 가이드 | [docs/법률_규제_가이드.md](docs/법률_규제_가이드.md) |
