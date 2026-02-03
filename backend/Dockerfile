FROM python:3.14-slim

# Create non-root user and group
RUN addgroup --system --group backend && \
    adduser --system --no-create-home --uid 1001 backend

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directories with proper ownership
RUN mkdir -p data/chroma_db data/uploads data/sample_docs data/backups && \
    chown -R backend:backend /app

# Switch to non-root user
USER backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
