FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GIT_MCP_PORT=3012 \
    REPO_FUNDAMENTALS_REPO_ROOT=/workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN pip install --no-cache-dir \
    mcp==1.12.4 \
    uvicorn[standard]==0.27.0

EXPOSE 3012

CMD ["python", "-m", "apps.mcp.repo_fundamentals.git_server"]
