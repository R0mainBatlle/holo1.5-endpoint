"""
RunPod Serverless Handler for Holo1.5-7B VLM API

This handler allows the FastAPI service to work with RunPod Serverless.
It accepts requests in RunPod format and forwards them to the FastAPI app.
"""

import asyncio
import httpx
import time
import os
from typing import Dict, Any


# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


async def wait_for_service(url: str, max_wait: int = 60) -> bool:
    """Wait for the FastAPI service to be ready"""
    start_time = time.time()
    async with httpx.AsyncClient(timeout=5.0) as client:
        while time.time() - start_time < max_wait:
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy" and data.get("model_loaded"):
                        print("✓ Service is ready")
                        return True
            except Exception as e:
                print(f"Waiting for service... ({e})")
            await asyncio.sleep(2)
    return False


async def process_request(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a request through the FastAPI service

    Expected input format:
    {
        "image_url": "https://example.com/image.jpg",
        "text": "What do you see?",
        "max_tokens": 512  # optional
    }

    Or OpenAI format:
    {
        "model": "Hcompany/Holo1.5-7B",
        "messages": [...]
    }
    """

    # Detect if input is already in OpenAI format
    if "messages" in input_data:
        # Direct OpenAI format
        payload = input_data
    else:
        # Convert simple format to OpenAI format
        image_url = input_data.get("image_url")
        text = input_data.get("text", "Describe this image")
        max_tokens = input_data.get("max_tokens", 512)

        if not image_url:
            return {
                "error": "Missing required field: image_url",
                "status": "failed"
            }

        # Build OpenAI-compatible request
        payload = {
            "model": "Hcompany/Holo1.5-7B",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens
        }

    # Make request to FastAPI service
    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.post(
                    f"{API_BASE_URL}/v1/chat/completions",
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "output": result
                    }
                else:
                    error_msg = f"API returned status {response.status_code}: {response.text}"
                    print(f"Attempt {attempt + 1} failed: {error_msg}")

                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAY)
                    else:
                        return {
                            "error": error_msg,
                            "status": "failed"
                        }

            except Exception as e:
                error_msg = f"Request failed: {str(e)}"
                print(f"Attempt {attempt + 1} failed: {error_msg}")

                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    return {
                        "error": error_msg,
                        "status": "failed"
                    }

    return {
        "error": "All retry attempts failed",
        "status": "failed"
    }


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main RunPod handler function

    Args:
        event: Input event from RunPod with format:
            {
                "input": {
                    "image_url": "...",
                    "text": "..."
                }
            }

    Returns:
        Response in RunPod format:
            {
                "output": {...},
                "status": "success"
            }
    """
    print(f"Received event: {event.keys()}")

    # Extract input from event
    input_data = event.get("input", {})

    if not input_data:
        return {
            "error": "No input provided",
            "status": "failed"
        }

    # Run async processing
    try:
        result = asyncio.run(process_request(input_data))
        return result
    except Exception as e:
        return {
            "error": f"Handler error: {str(e)}",
            "status": "failed"
        }


# For testing locally
if __name__ == "__main__":
    import sys

    # Test with a simple request
    test_input = {
        "input": {
            "image_url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg",
            "text": "What do you see in this image?",
            "max_tokens": 100
        }
    }

    print("Testing handler...")
    result = handler(test_input)
    print("\nResult:")
    print(result)
