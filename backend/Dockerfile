FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Optional: install CrossEncoder reranker (~22 MB model + PyTorch).
# Set INSTALL_RERANKER=true at build time to enable.
# Default: off (keeps image ~400 MB instead of ~3 GB).
ARG INSTALL_RERANKER=false
RUN if [ "$INSTALL_RERANKER" = "true" ]; then \
        pip install --no-cache-dir "sentence-transformers>=3.0.0"; \
    fi

COPY backend ./backend

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
