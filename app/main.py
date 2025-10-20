from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from PIL import Image
import io
import httpx
import base64
import time
import uuid
from typing import List, Dict, Any, Optional, Union


app = FastAPI(title="Holo1.5-7B Vision Language Model API (OpenAI Compatible)")

# Global variables for model and processor
model = None
processor = None
device = None
MODEL_NAME = "Hcompany/Holo1.5-7B"


# Pydantic models for OpenAI-compatible API
class ImageURL(BaseModel):
    url: str
    detail: Optional[str] = "auto"


class ContentPartText(BaseModel):
    type: str = "text"
    text: str


class ContentPartImageURL(BaseModel):
    type: str = "image_url"
    image_url: Union[ImageURL, Dict[str, str]]


class Message(BaseModel):
    role: str
    content: Union[str, List[Union[ContentPartText, ContentPartImageURL, Dict[str, Any]]]]


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


@app.on_event("startup")
async def load_model():
    """Load the Holo1.5-7B model on startup"""
    global model, processor, device

    print("Loading Holo1.5-7B model...")

    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load model and processor
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None
    )

    if device == "cpu":
        model = model.to(device)

    processor = AutoProcessor.from_pretrained(MODEL_NAME)

    print("Model loaded successfully!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "model": MODEL_NAME,
        "device": device,
        "api_version": "OpenAI Compatible"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "processor_loaded": processor is not None,
        "device": device
    }


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI compatible)"""
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "hcompany"
            }
        ]
    }


async def fetch_image_from_url(url: str) -> Image.Image:
    """Fetch an image from a URL or decode from base64"""
    try:
        # Check if it's a base64 data URL
        if url.startswith("data:image"):
            # Extract base64 data
            header, base64_data = url.split(",", 1)
            image_data = base64.b64decode(base64_data)
            return Image.open(io.BytesIO(image_data))

        # Otherwise, fetch from URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image: {str(e)}")


def parse_message_content(content: Union[str, List[Any]]) -> tuple[List[Image.Image], str]:
    """Parse message content and extract images and text"""
    images = []
    texts = []

    if isinstance(content, str):
        # Simple text message
        texts.append(content)
    elif isinstance(content, list):
        # Multimodal content
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    texts.append(item.get("text", ""))
                elif item.get("type") == "image_url":
                    # Will be processed later
                    pass

    return images, " ".join(texts)


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint

    Supports:
    - Image URLs (http/https)
    - Base64 encoded images (data:image/...)
    - Text prompts
    """
    if model is None or processor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if request.stream:
        raise HTTPException(status_code=400, detail="Streaming not supported yet")

    try:
        # Build messages in Qwen2-VL format
        qwen_messages = []

        for message in request.messages:
            if message.role not in ["user", "assistant", "system"]:
                continue

            content_parts = []

            if isinstance(message.content, str):
                # Simple text message
                content_parts.append({"type": "text", "text": message.content})
            elif isinstance(message.content, list):
                # Multimodal message
                for item in message.content:
                    item_dict = item if isinstance(item, dict) else item.dict()

                    if item_dict.get("type") == "text":
                        content_parts.append({"type": "text", "text": item_dict.get("text", "")})

                    elif item_dict.get("type") == "image_url":
                        # Fetch the image
                        image_url_data = item_dict.get("image_url", {})
                        if isinstance(image_url_data, dict):
                            url = image_url_data.get("url", "")
                        else:
                            url = image_url_data

                        if url:
                            pil_image = await fetch_image_from_url(url)

                            # Convert RGBA to RGB if necessary
                            if pil_image.mode == 'RGBA':
                                pil_image = pil_image.convert('RGB')

                            content_parts.append({"type": "image", "image": pil_image})

            if content_parts:
                qwen_messages.append({
                    "role": message.role,
                    "content": content_parts
                })

        if not qwen_messages:
            raise HTTPException(status_code=400, detail="No valid messages provided")

        # Prepare inputs using processor
        text_prompt = processor.apply_chat_template(
            qwen_messages, tokenize=False, add_generation_prompt=True
        )

        image_inputs, video_inputs = process_vision_info(qwen_messages)

        inputs = processor(
            text=[text_prompt],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )

        inputs = inputs.to(device)

        # Generate response
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
            )

        # Trim the input tokens from the generated output
        generated_ids_trimmed = [
            out_ids[len(in_ids):]
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        # Decode the output
        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        # Format response in OpenAI style
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": output_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(inputs.input_ids[0]),
                "completion_tokens": len(generated_ids_trimmed[0]),
                "total_tokens": len(inputs.input_ids[0]) + len(generated_ids_trimmed[0])
            }
        }

        return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
