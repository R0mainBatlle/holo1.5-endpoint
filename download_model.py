#!/usr/bin/env python3
"""
Download the Holo1.5-7B model and processor to the local cache.
This script is run during Docker build to bake the model into the image.
"""

import os
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

MODEL_NAME = "Hcompany/Holo1.5-7B"

def download_model():
    """Download model and processor to cache"""
    print(f"Downloading {MODEL_NAME}...")
    print(f"Cache directory: {os.environ.get('TRANSFORMERS_CACHE', '~/.cache/huggingface')}")

    # Download processor
    print("\n1. Downloading processor...")
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    print("✓ Processor downloaded")

    # Download model
    print("\n2. Downloading model (~14GB, this may take several minutes)...")
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        MODEL_NAME,
        torch_dtype="auto",
        device_map=None  # Don't load to device, just download
    )
    print("✓ Model downloaded")

    print(f"\n✓ Successfully downloaded {MODEL_NAME}")
    print(f"  Model is now cached and ready to use")

if __name__ == "__main__":
    download_model()
