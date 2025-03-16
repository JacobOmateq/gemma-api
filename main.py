from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import json
import logging
import asyncio
from typing import Optional

# Load LLM settings
with open('llm_settings.json', 'r') as f:
    llm_settings = json.load(f)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

OLLAMA_URL = "http://ollama:11434"

class TitleRequest(BaseModel):
    title: str

async def call_ollama_with_retry(client: httpx.AsyncClient, title: str, max_retries: int = 3) -> Optional[dict]:
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to call Ollama")
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": llm_settings["model"],
                    "prompt": f"{llm_settings['system_prompt']}\n\nTitel: {title}",
                    "stream": False
                },
                timeout=60.0  # Increased timeout to 60 seconds
            )
            
            if response.status_code == 200:
                return response.json()
            
            logger.error(f"Attempt {attempt + 1} failed with status {response.status_code}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                
        except httpx.TimeoutException as e:
            logger.error(f"Timeout on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
    
    return None

@app.post("/extract_department")
async def extract_department(request: TitleRequest):
    try:
        logger.info(f"Received request with title: {request.title}")
        
        async with httpx.AsyncClient(
            timeout=60.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            result = await call_ollama_with_retry(client, request.title)
            
            if result is None:
                raise HTTPException(
                    status_code=503,
                    detail="Failed to get response from Ollama after multiple attempts"
                )
            
            try:
                department_json = json.loads(result['response'])
                return department_json
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing response: {str(e)}")
                return {"enhet": "Okänd"}
                
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/version")
            if response.status_code == 200:
                return {"status": "healthy", "ollama": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}