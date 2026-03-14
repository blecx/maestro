FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BASH_GATEWAY_MCP_PORT=3011 \
    BASH_GATEWAY_REPO_ROOT=/workspace \
    BASH_GATEWAY_POLICY_PATH=/workspace/configs/bash_gateway_policy.default.yml

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN pip install --no-cache-dir \
    mcp==1.12.4 \
    uvicorn[standard]==0.27.0 \
    pyyaml==6.0.1

EXPOSE 3011

CMD ["python", "-m", "apps.mcp.bash_gateway.mcp_server"]
