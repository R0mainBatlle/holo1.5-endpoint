from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from PIL import Image
import io
from typing import Optional

app = FastAPI(title="Holo1.5-7B Vision Language Model API")

# Global variables for model and processor
model = None
processor = None
device = None


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
        "Hcompany/Holo1.5-7B",
        torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None
    )

    if device == "cpu":
        model = model.to(device)

    processor = AutoProcessor.from_pretrained("Hcompany/Holo1.5-7B")

    print("Model loaded successfully!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "model": "Holo1.5-7B",
        "device": device
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


@app.post("/predict")
async def predict(
    image: UploadFile = File(..., description="Image file to analyze"),
    text: str = Form(..., description="Text query/prompt for the model")
):
    """
    Make a prediction using the Holo1.5-7B model

    Args:
        image: Image file (PNG, JPG, etc.)
        text: Text query or instruction

    Returns:
        JSON response with the model's output
    """
    if model is None or processor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Read and process the image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if necessary
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')

        # Prepare messages in the format expected by Qwen2-VL
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": pil_image,
                    },
                    {
                        "type": "text",
                        "text": text
                    },
                ],
            }
        ]

        # Prepare inputs using processor
        text_prompt = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        image_inputs, video_inputs = process_vision_info(messages)

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
                max_new_tokens=512,
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

        return JSONResponse(content={
            "success": True,
            "text_input": text,
            "model_output": output_text
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
