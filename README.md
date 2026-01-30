# 🤖 AI Customer Support Platform

> **모든 기업에게 24/7 AI 고객지원을** — RAG + Deep Agents 기반 차세대 고객지원 플랫폼

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 프로젝트 개요

AI Customer Support는 **RAG(Retrieval-Augmented Generation)**과 **Deep Agents(멀티에이전트 시스템)**을 결합한 AI 고객지원 SaaS 플랫폼입니다.

기업들이 직면한 3대 고객지원 과제를 해결합니다:
- 💰 **비용 증가** — AI 자동화로 CS 비용 70~80% 절감
- ⏰ **24/7 대응 불가** — AI가 365일 24시간 즉각 응답
- 📊 **응답 일관성 부족** — RAG 기반 정확하고 일관된 답변

### 핵심 차별점

| 차별점 | 설명 |
|--------|------|
| 🧠 **Deep Agents** | 멀티에이전트 시스템으로 복합 문의 처리 (Routing → Answer → Escalation → Feedback) |
| 📚 **RAG Engine** | 기업 문서 기반 정확한 답변, 환각(Hallucination) 최소화 |
| 🇰🇷 **한국어 특화** | 존댓말/반말 자동 조절, 한국 비즈니스 맥락 이해 |
| 💸 **합리적 가격** | Free 플랜 제공, 경쟁사 대비 50~80% 저렴 |

---

## 📁 프로젝트 구조

```
ai-customer-support/
├── README.md                  # 프로젝트 개요 (현재 파일)
├── docs/                      # 사업 문서
│   ├── 사업계획서.md           # Full Business Plan
│   ├── 시장분석.md             # Market Analysis (TAM/SAM/SOM)
│   └── 경쟁사_분석.md          # Competitor Analysis & SWOT
├── src/                       # 소스 코드 (예정)
│   ├── agents/                # Deep Agents (Routing, Answer, Escalation, Feedback)
│   ├── rag/                   # RAG 파이프라인 (임베딩, 검색, 생성)
│   ├── api/                   # REST API 서버
│   ├── widget/                # 웹 위젯 (채팅 UI)
│   └── dashboard/             # 관리자 대시보드
├── infra/                     # 인프라 설정 (예정)
│   ├── docker/
│   └── k8s/
└── tests/                     # 테스트 코드 (예정)
```

---

## 🛠 기술 스택

### Backend
| 기술 | 용도 |
|------|------|
| **Python 3.12+** | 메인 백엔드 언어 |
| **FastAPI** | REST API 서버 |
| **LangChain / LangGraph** | LLM 오케스트레이션, 에이전트 프레임워크 |
| **PostgreSQL** | 메인 데이터베이스 |
| **Redis** | 캐싱, 세션 관리, 메시지 큐 |
| **Celery** | 비동기 작업 처리 |

### AI / ML
| 기술 | 용도 |
|------|------|
| **OpenAI GPT-4o / Claude** | 기본 LLM (답변 생성) |
| **OpenAI Embeddings / Cohere** | 텍스트 임베딩 |
| **Pinecone / Weaviate** | 벡터 데이터베이스 (RAG) |
| **LangGraph** | 멀티에이전트 오케스트레이션 (Deep Agents) |
| **Hugging Face** | 한국어 NLP 모델, 감정 분석 |

### Frontend
| 기술 | 용도 |
|------|------|
| **Next.js 14+** | 관리자 대시보드 |
| **React** | 채팅 위젯 |
| **TypeScript** | 타입 안전성 |
| **Tailwind CSS** | UI 스타일링 |
| **Shadcn/ui** | UI 컴포넌트 |

### Infrastructure
| 기술 | 용도 |
|------|------|
| **AWS / GCP** | 클라우드 인프라 |
| **Docker** | 컨테이너화 |
| **Kubernetes** | 오케스트레이션 |
| **Terraform** | IaC (Infrastructure as Code) |
| **GitHub Actions** | CI/CD |

### Integrations
| 연동 | 상태 |
|------|------|
| 웹 위젯 (JavaScript) | 🔜 Phase 1 |
| Kakao 비즈챗 | 🔜 Phase 2 |
| Slack | 🔜 Phase 2 |
| Microsoft Teams | 🔜 Phase 3 |
| Shopify / 카페24 | 🔜 Phase 2 |
| REST API / Webhook | 🔜 Phase 1 |

---

## 🚀 시작하기 (Setup)

### 사전 요구사항

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/your-org/ai-customer-support.git
cd ai-customer-support

# 2. Python 가상환경 생성 및 의존성 설치
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 등 설정

# 4. 데이터베이스 마이그레이션
python manage.py migrate

# 5. 프론트엔드 의존성 설치
cd src/dashboard
npm install

# 6. 개발 서버 실행
# 터미널 1: Backend
python -m uvicorn src.api.main:app --reload --port 8000

# 터미널 2: Frontend
cd src/dashboard && npm run dev
```

### Docker로 실행

```bash
docker-compose up -d
```

### 환경 변수

```env
# LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_cs
REDIS_URL=redis://localhost:6379

# Vector DB
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...

# Integrations
KAKAO_API_KEY=...
SLACK_BOT_TOKEN=xoxb-...
```

---

## 📊 비즈니스 문서

| 문서 | 내용 | 링크 |
|------|------|------|
| 📋 사업계획서 | 비즈니스 모델, 수익 전망, 투자 계획 | [docs/사업계획서.md](docs/사업계획서.md) |
| 📈 시장분석 | TAM/SAM/SOM, 성장 동인, 트렌드 | [docs/시장분석.md](docs/시장분석.md) |
| 🔍 경쟁사 분석 | 기능 비교, 차별화, SWOT | [docs/경쟁사_분석.md](docs/경쟁사_분석.md) |

---

## 🗺 로드맵

| 단계 | 시기 | 목표 |
|------|------|------|
| **Phase 1** | M1~M3 | MVP (RAG + 웹 위젯 + 기본 대시보드) |
| **Phase 2** | M4~M6 | 클로즈드 베타, 카카오/Slack 연동 |
| **Phase 3** | M7~M9 | 퍼블릭 런칭, Free/Pro 플랜 |
| **Phase 4** | M10~M12 | Deep Agents v2, Enterprise 플랜 |
| **Phase 5** | M13~M18 | 음성 AI, 일본 시장 진출 |

---

## 🤝 기여 방법

1. 이 저장소를 Fork 합니다
2. Feature 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'feat: add amazing feature'`)
4. 브랜치에 Push 합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📬 문의

- **이메일**: contact@ai-customer-support.com
- **웹사이트**: https://ai-customer-support.com (준비 중)

---

*Built with ❤️ and AI*
