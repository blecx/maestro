from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import hashlib

app = FastAPI(title="Mock LLM Gateway")


@app.post("/admin/set-live-key")
async def set_live_key(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    api_key = data.get("api_key")
    if api_key:
        import os, json
        override_path = os.getenv("LLM_OVERRIDE_PATH", "configs/runtime_override.json")
        os.makedirs(os.path.dirname(override_path), exist_ok=True)
        with open(override_path, "w") as f:
            json.dump({"api_key": api_key, "base_url": "https://api.openai.com/v1"}, f)
        return {"status": "success", "message": "Live key updated natively via Gateway"}
    return {"status": "error", "message": "No api_key provided"}


# In-memory store for mocks: request fingerprint -> mock response
mock_responses: Dict[str, Any] = {}

class MockData(BaseModel):
    fingerprint: Optional[str] = None
    prompt_match: Optional[str] = None
    response: Any

def _get_fingerprint(request_data: dict) -> str:
    # A simple fingerprint using the messages content
    content = ""
    for msg in request_data.get("messages", []):
        content += msg.get("content", "") + "|"
    return hashlib.md5(content.encode("utf-8")).hexdigest()

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    fingerprint = _get_fingerprint(body)
    
    # Check for exact fingerprint
    if fingerprint in mock_responses:
        return mock_responses[fingerprint]

    # Fallback checking for prompt_match substring
    messages_content = "".join(msg.get("content", "") for msg in body.get("messages", []) if isinstance(msg.get("content"), str))
    for mf, mock_val in mock_responses.items():
        if mock_val.get("_metadata", {}).get("prompt_match") and mock_val["_metadata"]["prompt_match"] in messages_content:
            return mock_val["response"]
            
    # Default mock response if not found
    return {
        "id": "chatcmpl-mock",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "mock-model",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a default mock response from the Mock LLM Gateway."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

@app.post("/admin/mocks")
async def add_mock(mock_data: MockData):
    fingerprint = mock_data.fingerprint or "default_fingerprint_for_" + str(len(mock_responses))
    mock_payload = {
        "response": mock_data.response,
        "_metadata": {}
    }
    if mock_data.prompt_match:
        mock_payload["_metadata"]["prompt_match"] = mock_data.prompt_match
        
    mock_responses[fingerprint] = mock_payload
    return {"status": "success", "fingerprint": fingerprint}

@app.get("/admin/mocks")
async def get_mocks():
    return mock_responses

@app.delete("/admin/mocks")
async def flush_mocks():
    mock_responses.clear()
    return {"status": "flushed"}
