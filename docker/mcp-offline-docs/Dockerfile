FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OFFLINE_DOCS_MCP_PORT=3017 \
    OFFLINE_DOCS_MCP_REPO_ROOT=/workspace

WORKDIR /workspace

RUN pip install --no-cache-dir \
    mcp==1.12.4 \
    uvicorn[standard]==0.27.0

EXPOSE 3017

CMD ["python", "-m", "apps.mcp.offline_docs.server"]
