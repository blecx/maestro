FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FILESYSTEM_MCP_PORT=3014 \
    REPO_FUNDAMENTALS_REPO_ROOT=/workspace

WORKDIR /workspace

RUN pip install --no-cache-dir \
    mcp==1.12.4 \
    uvicorn[standard]==0.27.0

EXPOSE 3014

CMD ["python", "-m", "apps.mcp.repo_fundamentals.filesystem_server"]
