from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from modules.tools import generate_ollama_response, DEFAULT_MODEL
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/generate")
async def generate(
    request: PromptRequest,
    model: str = Query(default=DEFAULT_MODEL, description="The model to use for generation"),
    stream: bool = Query(default=False, description="Whether to stream the response")
):
    logger.info(f"Received request - Prompt: {request.prompt}, Model: {model}, Stream: {stream}")
    async def event_generator():
        async for chunk in generate_ollama_response(request.prompt, model, stream):
            if "error" in chunk:
                yield f"data: {json.dumps(chunk)}\n\n"
                break
            yield f"data: {json.dumps(chunk)}\n\n"

    if stream:
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        full_response = {}
        async for chunk in generate_ollama_response(request.prompt, model, stream):
            if "error" in chunk:
                raise HTTPException(status_code=500, detail=chunk["error"])
            full_response.update(chunk)
        return JSONResponse(content=full_response)

