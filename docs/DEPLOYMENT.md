# AI Customer Support Platform - 배포 가이드

## 목차
1. [환경 요구사항](#환경-요구사항)
2. [로컬 개발 환경](#로컬-개발-환경)
3. [Docker 배포](#docker-배포)
4. [프로덕션 배포](#프로덕션-배포)
5. [환경 변수](#환경-변수)

---

## 환경 요구사항

### 최소 요구사항
- Python 3.12+
- Node.js 20+
- 2GB RAM
- 10GB 디스크 공간

### 권장 사양
- Python 3.14
- Node.js 22 LTS
- 4GB RAM
- 20GB 디스크 공간

---

## 로컬 개발 환경

### Backend 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn main:app --reload --port 8000
```

### Frontend 설정

```bash
cd app

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 접속 URL
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## Docker 배포

### Docker Compose 사용

```bash
# 전체 스택 실행
docker compose up -d

# 로그 확인
docker compose logs -f

# 중지
docker compose down
```

### 개별 컨테이너 빌드

```bash
# Backend
cd backend
docker build -t ai-support-backend .
docker run -p 8000:8000 ai-support-backend

# Frontend
cd app
docker build -t ai-support-frontend .
docker run -p 3000:3000 ai-support-frontend
```

---

## 프로덕션 배포

### 1. 환경 변수 설정

```bash
# .env 파일 생성
cp backend/.env.example backend/.env

# 필수 변수 설정
OPENAI_API_KEY=sk-xxx
API_KEY=your-secure-api-key
CORS_ORIGINS=https://yourdomain.com
```

### 2. Backend 배포

```bash
cd backend

# 의존성 설치
pip install -r requirements.txt

# Gunicorn으로 실행 (권장)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 3. Frontend 배포

```bash
cd app

# 프로덕션 빌드
npm run build

# 실행
npm start
```

### 4. Nginx 리버스 프록시 (선택)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 환경 변수

### Backend

| 변수 | 설명 | 기본값 | 필수 |
|------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 키 | 없음 (데모 모드) | 아니요 |
| `API_KEY` | 백엔드 인증 키 | 없음 (인증 없음) | 아니요 |
| `MODEL_NAME` | 사용할 LLM 모델 | gpt-4o-mini | 아니요 |
| `TEMPERATURE` | 모델 온도 | 0.3 | 아니요 |
| `MAX_TOKENS` | 최대 토큰 수 | 1024 | 아니요 |
| `CORS_ORIGINS` | 허용 CORS 출처 | localhost:3000 | 아니요 |
| `SENTRY_DSN` | Sentry 에러 추적 | 없음 | 아니요 |

### Frontend

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `NEXT_PUBLIC_API_URL` | 백엔드 URL | http://localhost:8000 |
| `NEXT_PUBLIC_API_KEY` | API 인증 키 | 없음 |

---

## 헬스 체크

```bash
# Backend 헬스 체크
curl http://localhost:8000/api/health

# 응답 예시
{
  "status": "healthy",
  "version": "1.0.0",
  "demo_mode": true,
  "model": "gpt-4o-mini",
  "documents_loaded": 5
}
```

---

## 트러블슈팅

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 사용 중인 포트 확인
   lsof -i :8000
   lsof -i :3000
   ```

2. **Python 버전 문제**
   ```bash
   python --version  # 3.12+ 확인
   ```

3. **Node 버전 문제**
   ```bash
   node --version  # 20+ 확인
   ```

4. **의존성 문제**
   ```bash
   # Backend
   pip install -r requirements.txt --upgrade

   # Frontend
   rm -rf node_modules package-lock.json
   npm install
   ```
