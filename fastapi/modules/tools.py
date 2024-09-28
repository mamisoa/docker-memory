import aiohttp
import asyncio
from typing import Dict, Any, AsyncGenerator, Union
import os
import json
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://192.168.68.76')
OLLAMA_PORT = os.getenv('OLLAMA_PORT','11435')
DEFAULT_MODEL = os.getenv('OLLAMA_DEFAULT_MODEL','ajindal/llama3.1-storm:8b-Q8_0')

async def generate_ollama_response(
    prompt: str, 
    model: str = DEFAULT_MODEL, 
    stream: bool = False,
    max_retries: int = 3
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Asynchronously generate a response from an Ollama model.
    
    :param prompt: The input prompt for the model
    :param model: The name of the Ollama model to use (default is from env or "phi-3")
    :param stream: Whether to stream the response or not (default is False)
    :param max_retries: Maximum number of retries on connection error
    :yield: Dictionaries containing parts of the model's response
    """
    url = f"{OLLAMA_URL}:{OLLAMA_PORT}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": stream}
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Sending request to Ollama server. Attempt {attempt + 1}")
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Successfully connected to Ollama server")
                        if stream:
                            async for line in response.content:
                                if line:
                                    try:
                                        yield json.loads(line)
                                    except json.JSONDecodeError:
                                        logger.error(f"Failed to decode JSON: {line}")
                        else:
                            full_response = await response.text()
                            parsed_response = [json.loads(line) for line in full_response.strip().split('\n')]
                            for resp in parsed_response:
                                yield resp
                    else:
                        logger.error(f"Failed to get response: HTTP {response.status}")
                        yield {"error": f"Failed to get response: HTTP {response.status}"}
                    return  # Exit after successful response
        except aiohttp.ClientConnectionError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Connection error: {e}. Retrying... (Attempt {attempt + 1})")
                await asyncio.sleep(1)  # Wait for 1 second before retrying
            else:
                logger.error(f"Max retries reached. Connection error: {e}")
                yield {"error": "Failed to connect to the Ollama server after multiple attempts"}

async def test_generate():
    prompt = "Explain the concept of artificial intelligence in simple terms."
    
    logger.info("Testing non-streaming response:")
    async for chunk in generate_ollama_response(prompt, stream=False):
        logger.info(chunk)
    
    logger.info("Testing streaming response:")
    async for chunk in generate_ollama_response(prompt, stream=True):
        logger.info(chunk)

if __name__ == "__main__":
    asyncio.run(test_generate())

