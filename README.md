# AI Customer Support Platform

> 🤖 RAG + Multi-Agent 기반 차세대 AI 고객지원 SaaS 플랫폼

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)

[🇰🇷 한국어](#한국어) | [🇺🇸 English](#english)

---

## 한국어

### ✨ 주요 기능

| 기능 | 설명 | 상태 |
|------|------|:----:|
| 🤖 **AI 채팅** | RAG 검색 + 의도 분류 + 멀티에이전트 라우팅 | ✅ |
| 📚 **지식베이스** | TXT/MD/PDF 업로드, TF-IDF 벡터 검색 | ✅ |
| 🌐 **웹 크롤러** | URL → FAQ/콘텐츠 자동 추출 → RAG 가져오기 | ✅ |
| 📊 **데이터 허브** | HuggingFace 데이터셋 탐색/다운로드/변환 | ✅ |
| 🎙️ **음성 파이프라인** | 음성 → STT → Q&A 문서 자동 생성 | ✅ |
| 📈 **관리 대시보드** | 통계, 대화 관리, 지식베이스, 설정 | ✅ |
| 🌍 **다국어 지원** | 한국어/영어 UI (자동 감지) | ✅ |
| 🎭 **데모 모드** | API 키 없이 모든 기능 동작 | ✅ |

### 🛠️ 기술 스택

**Backend**
- Python 3.12+ / FastAPI 0.115
- scikit-learn (TF-IDF 벡터 검색)
- LangChain (텍스트 분할, LLM 연동)
- SQLite + aiosqlite (비동기 영속화)

**Frontend**
- Next.js 16 (App Router)
- React 19 + TypeScript
- Tailwind CSS v4

### 🚀 빠른 시작

#### 사전 요구사항
- Python 3.12+
- Node.js 20+

#### Backend 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# (선택) 환경변수 설정 — 없으면 데모 모드
cp .env.example .env
# OPENAI_API_KEY=sk-xxx

# 서버 실행
uvicorn main:app --reload --port 8000
```

#### Frontend 설정
```bash
cd app
npm install
npm run dev
```

- 프론트엔드: http://localhost:3000
- API 문서 (Swagger): http://localhost:8000/docs

### 🔐 데모 모드

**API 키 없이도 모든 기능이 완전히 동작합니다:**
- 채팅: 한국어 키워드 기반 자동 응답 (배송, 반품, 교환 등)
- 크롤러: SmartMall 데모 데이터
- 데이터 허브: 샘플 데이터셋
- 음성: 데모 통화 녹취록

### 📁 프로젝트 구조

```
ai-customer-support/
├── app/                          # Next.js 프론트엔드
│   ├── src/app/                  # App Router 페이지
│   │   ├── (admin)/              # 관리자 페이지 그룹
│   │   │   ├── dashboard/        # 대시보드
│   │   │   ├── datahub/          # 데이터 허브
│   │   │   ├── crawler/          # 웹 크롤러
│   │   │   └── voice/            # 음성 분석
│   │   ├── demo/                 # 채팅 데모
│   │   └── widget/               # 위젯 미리보기
│   └── src/lib/                  # 유틸리티
│       ├── api.ts                # API 클라이언트
│       └── i18n/                 # 다국어 지원
│
├── backend/                      # FastAPI 백엔드
│   ├── main.py                   # 앱 진입점
│   ├── agents/                   # 멀티에이전트 시스템
│   ├── rag/                      # RAG 파이프라인
│   ├── crawler/                  # 웹 크롤링
│   ├── datahub/                  # 데이터 허브
│   ├── voice/                    # 음성 처리
│   └── tests/                    # 테스트 (93개)
│
└── docs/                         # 사업 문서
```

### 🧪 테스트

```bash
cd backend
source venv/bin/activate
pytest -v                    # 전체 테스트 (93개)
pytest tests/test_api.py     # API 테스트 (18개)
pytest tests/test_crawler.py # 크롤러 테스트 (30개)
```

### 📡 API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/chat` | AI 채팅 |
| POST | `/api/documents/upload` | 문서 업로드 |
| GET | `/api/documents` | 문서 목록 |
| GET | `/api/conversations` | 대화 목록 |
| GET | `/api/analytics` | 분석 통계 |
| GET | `/api/health` | 헬스 체크 |
| | `/api/crawler/*` | 웹 크롤링 (9개) |
| | `/api/datahub/*` | 데이터 허브 (12개) |
| | `/api/voice/*` | 음성 처리 (7개) |

### 🔧 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | 없음 (데모 모드) |
| `NEXT_PUBLIC_API_URL` | 백엔드 URL | http://localhost:8000 |
| `API_KEY` | 백엔드 인증 키 | 없음 (인증 없음) |
| `SENTRY_DSN` | 에러 트래킹 | 없음 |

---

## English

### ✨ Key Features

| Feature | Description | Status |
|---------|-------------|:------:|
| 🤖 **AI Chat** | RAG search + Intent classification + Multi-agent routing | ✅ |
| 📚 **Knowledge Base** | TXT/MD/PDF upload, TF-IDF vector search | ✅ |
| 🌐 **Web Crawler** | URL → Auto FAQ/content extraction → RAG import | ✅ |
| 📊 **Data Hub** | HuggingFace dataset explore/download/transform | ✅ |
| 🎙️ **Voice Pipeline** | Voice → STT → Auto Q&A document generation | ✅ |
| 📈 **Admin Dashboard** | Statistics, conversation management, settings | ✅ |
| 🌍 **Multilingual** | Korean/English UI (auto-detect) | ✅ |
| 🎭 **Demo Mode** | All features work without API key | ✅ |

### 🚀 Quick Start

#### Prerequisites
- Python 3.12+
- Node.js 20+

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd app
npm install
npm run dev
```

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### 🧪 Testing

```bash
cd backend
pytest -v  # 93 tests
```

### 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for modern customer support
</p>
