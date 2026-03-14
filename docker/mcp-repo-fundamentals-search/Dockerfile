FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SEARCH_MCP_PORT=3013 \
    REPO_FUNDAMENTALS_REPO_ROOT=/workspace

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y --no-install-recommends ripgrep && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    mcp==1.12.4 \
    uvicorn[standard]==0.27.0

EXPOSE 3013

CMD ["python", "-m", "apps.mcp.repo_fundamentals.search_server"]
