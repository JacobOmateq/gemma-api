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
    system_prompt: Optional[str] = None

class ResponseModel(BaseModel):
    content: Optional[dict] = None

def clean_json_response(text: str) -> str:
    """Clean the response text by removing markdown code blocks and extra whitespace."""
    # Remove markdown code blocks if present
    cleaned = text.replace('```json', '').replace('```', '').strip()
    return cleaned

async def call_ollama_with_retry(client: httpx.AsyncClient, title: str, system_prompt: Optional[str] = None, max_retries: int = 3) -> Optional[dict]:
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to call Ollama")
            
            # Use provided system prompt or fall back to default
            prompt_to_use = system_prompt or llm_settings['system_prompt']
            
            # Complete the prompt with the input text
            full_prompt = f"{prompt_to_use}{title}\nOutput:"
            
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": llm_settings["model"],
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60.0  # Increased timeout to 60 seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Ollama raw response: {result}")
                return result
            
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

@app.post("/extract_department", response_model=ResponseModel)
async def extract_department(request: TitleRequest):
    try:
        logger.info(f"Received request with title: {request.title}")
        if request.system_prompt:
            logger.info(f"Using custom system prompt")
        
        async with httpx.AsyncClient(
            timeout=60.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            result = await call_ollama_with_retry(client, request.title, request.system_prompt)
            
            if result is None:
                raise HTTPException(
                    status_code=503,
                    detail="Failed to get response from Ollama after multiple attempts"
                )
            
            try:
                response_text = result.get('response', '{}')
                logger.info(f"Response text to parse: {response_text}")
                
                # Clean the response before parsing
                cleaned_text = clean_json_response(response_text)
                logger.info(f"Cleaned text to parse: {cleaned_text}")
                
                department_json = json.loads(cleaned_text)
                return ResponseModel(content=department_json)
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing response: {str(e)}")
                logger.error(f"Failed to parse response text: {response_text}")
                return ResponseModel(content=None)
                
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