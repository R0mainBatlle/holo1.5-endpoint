# Holo1.5-7B FastAPI Service (OpenAI Compatible)

A dockerized FastAPI service providing an **OpenAI-compatible API** for the Holo1.5-7B Vision Language Model. Takes images (via URL or base64) and text as input, returns model predictions in OpenAI format.

## Model Information

**Holo1.5-7B** is a Vision Language Model (VLM) specialized for:
- UI localization and element detection
- Screen content understanding
- Answering questions about UI interfaces
- Supports up to 3840 × 2160 pixel resolution

Model page: [Hcompany/Holo1.5-7B](https://huggingface.co/Hcompany/Holo1.5-7B)

## Key Features

- **OpenAI-Compatible API** - Works with OpenAI SDKs and tools
- **Image URLs** - Fetch images directly from URLs
- **Base64 Images** - Support for embedded images
- **Standard Format** - Compatible with LangChain, OpenAI SDK, etc.
- **Docker Ready** - Easy deployment with GPU or CPU
- **RunPod Compatible** - Optimized for RunPod deployment

## Project Structure

```
holo-fastapi-service/
├── app/
│   └── main.py              # FastAPI application
├── Dockerfile               # GPU-enabled Dockerfile
├── Dockerfile.cpu           # CPU-only Dockerfile
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
├── test_api.py              # Test script
└── README.md               # This file
```

## Requirements

### Hardware Requirements
- **GPU Version**: NVIDIA GPU with at least 16GB VRAM (recommended)
- **CPU Version**: Works but significantly slower (~10x)

### Software Requirements
- Docker
- Docker Compose (optional but recommended)
- NVIDIA Container Toolkit (for GPU support)

## Quick Start

### Option 1: Docker Compose (GPU - Recommended)

```bash
docker-compose up --build
```

### Option 2: Docker (GPU)

```bash
# Build the image
docker build -t holo-api .

# Run the container
docker run --gpus all -p 8000:8000 holo-api
```

### Option 3: Docker (CPU only)

```bash
# Build the CPU image
docker build -f Dockerfile.cpu -t holo-api-cpu .

# Run the container
docker run -p 8000:8000 holo-api-cpu
```

### Option 4: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Usage

The API follows the **OpenAI Chat Completions format**, making it compatible with existing OpenAI tools and libraries.

### Health Check

```bash
curl http://localhost:8000/health
```

### Basic Example (with Image URL)

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Hcompany/Holo1.5-7B",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Describe this image in one sentence."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
            }
          }
        ]
      }
    ]
  }'
```

### Using Test Script

The included test script supports both URLs and local files:

```bash
# Test with a URL
python test_api.py "https://example.com/screenshot.png" "Where is the login button?"

# Test with a local file (automatically converts to base64)
python test_api.py screenshot.png "What elements are visible?"
```

### Python Example (Raw Requests)

```python
import requests

url = "http://localhost:8000/v1/chat/completions"

payload = {
    "model": "Hcompany/Holo1.5-7B",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Where is the search button?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/screenshot.png"
                    }
                }
            ]
        }
    ],
    "max_tokens": 512
}

response = requests.post(url, json=payload)
result = response.json()

print(result['choices'][0]['message']['content'])
```

### Python Example (OpenAI SDK)

```python
from openai import OpenAI

# Point to your local server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # API key not required but SDK needs something
)

response = client.chat.completions.create(
    model="Hcompany/Holo1.5-7B",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What do you see in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

### Using Base64 Images

```python
import base64
import requests

# Read and encode image
with open("screenshot.png", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

payload = {
    "model": "Hcompany/Holo1.5-7B",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this UI"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
}

response = requests.post("http://localhost:8000/v1/chat/completions", json=payload)
print(response.json())
```

## API Endpoints

### `GET /`
Health check endpoint
- Returns basic service status and API version

### `GET /health`
Detailed health check
- Returns model loading status and device information

### `GET /v1/models`
List available models (OpenAI compatible)
- Returns list of available models

### `POST /v1/chat/completions`
Main prediction endpoint (OpenAI compatible)

**Request Body:**
```json
{
  "model": "Hcompany/Holo1.5-7B",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Your question"},
        {"type": "image_url", "image_url": {"url": "image URL or data URI"}}
      ]
    }
  ],
  "max_tokens": 512,
  "temperature": 0.7
}
```

**Response Format:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "Hcompany/Holo1.5-7B",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Model's response here"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

## RunPod Deployment

RunPod uses ephemeral storage for containers, so you need to use **Network Volumes** to persist the model cache between pod restarts.

### Setup Network Volume

1. **Create a Network Volume in RunPod**
   - Go to RunPod dashboard → Storage → Network Volumes
   - Create a new volume (recommended: 50GB+ to store model)
   - Note the volume name

2. **Deploy with Network Volume**

When deploying your pod:

```yaml
# In RunPod template/deployment settings:

# Container Image
ghcr.io/your-username/holo-api:latest

# Volume Mount
Container Path: /workspace/cache
Volume: your-network-volume-name

# Environment Variables
TRANSFORMERS_CACHE=/workspace/cache
```

3. **Docker Command for RunPod**

```bash
docker run --gpus all \
  -p 8000:8000 \
  -v /runpod-volume:/workspace/cache \
  -e TRANSFORMERS_CACHE=/workspace/cache \
  holo-api
```

### Model Caching Behavior on RunPod

| Scenario | Model Download | Startup Time | Cost |
|----------|---------------|--------------|------|
| **With Network Volume** | First run only (~5-10 min) | <2 min subsequent | Volume storage fee |
| **Without Network Volume** | Every pod start (~5-10 min) | Always slow | No extra storage |

**Recommendation**: Use Network Volumes for production. The storage cost (~$0.10/GB/month) is minimal compared to re-downloading 14GB on every pod restart.

### RunPod Example docker-compose Override

```yaml
# docker-compose.runpod.yml
version: '3.8'

services:
  holo-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - TRANSFORMERS_CACHE=/workspace/cache
      - HF_HOME=/workspace/cache
    volumes:
      - /runpod-volume:/workspace/cache  # RunPod network volume
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## What Image Input to Provide

The Holo1.5-7B model is optimized for **UI/interface screenshots**:

### Recommended Image Types:
1. **Web page screenshots** - Browser interfaces, websites
2. **Desktop application screenshots** - Windows, Mac, or Linux UIs
3. **Mobile app screenshots** - iOS or Android interfaces
4. **UI mockups** - Design files showing interfaces

### Supported Input Methods:
- **HTTP/HTTPS URLs** - Direct image URLs
- **Base64 Data URIs** - `data:image/png;base64,...`
- **Local files** - Use test script (converts to base64)

### Supported Formats:
- PNG, JPG/JPEG, WEBP, GIF
- Any format supported by PIL/Pillow

### Resolution:
- Up to 3840 × 2160 pixels natively supported
- Higher resolutions automatically resized

### Example Use Cases:

**1. Element Localization**
```json
{
  "text": "Where is the login button?",
  "image": "https://example.com/webapp-screenshot.png"
}
```

**2. UI Understanding**
```json
{
  "text": "What options are available in the settings menu?",
  "image": "https://example.com/mobile-app.png"
}
```

**3. Screen Content QA**
```json
{
  "text": "What is the text in the notification area?",
  "image": "https://example.com/desktop-app.png"
}
```

## Configuration

### Environment Variables

```bash
# Cache directory for model files (important for RunPod)
TRANSFORMERS_CACHE=/workspace/cache
HF_HOME=/workspace/cache

# Hugging Face token (if needed for gated models)
HF_TOKEN=your_token_here
```

### Model Configuration

Edit `app/main.py` to adjust:
- `max_tokens`: Maximum length of generated response (default: 512)
- `torch_dtype`: Precision (bfloat16 for GPU, float32 for CPU)
- `temperature`: Not currently used but accepted in API

## Troubleshooting

### Out of Memory (GPU)
- Reduce `max_tokens` in requests
- Use smaller batch sizes
- Enable model quantization
- Use GPU with more VRAM (24GB+ recommended)

### Slow Performance (CPU)
- **Strongly recommend GPU** for production
- Reduce image resolution before sending
- Consider using model quantization
- Expected ~10x slower than GPU

### Model Download Issues
- Ensure stable internet connection
- First run downloads ~14GB
- Check disk space (need ~20GB free)
- On RunPod: Ensure network volume is mounted correctly

### RunPod Specific Issues

**Model re-downloads every time:**
- Check that network volume is properly mounted
- Verify `TRANSFORMERS_CACHE` environment variable is set
- Ensure volume has sufficient space (50GB+)

**Connection timeouts:**
- Increase client timeout (first request takes 1-2 minutes for model loading)
- Check RunPod pod logs for errors

## Performance Notes

- **First request**: Slow due to model loading (~1-2 minutes)
- **Subsequent requests**: Fast (~1-5 seconds depending on image size)
- **GPU vs CPU**: GPU is ~10x faster
- **Model size**: ~14GB download on first run
- **VRAM usage**: ~16GB during inference

## Model Cache Location Priority

The service checks for cache in this order:
1. `TRANSFORMERS_CACHE` environment variable
2. `HF_HOME` environment variable
3. Default: `~/.cache/huggingface/`

For RunPod, always set `TRANSFORMERS_CACHE=/workspace/cache`

## License

This project uses the Holo1.5-7B model which is licensed under Apache 2.0.

## Support

For issues specific to:
- **The model**: [Hcompany/Holo1.5-7B](https://huggingface.co/Hcompany/Holo1.5-7B)
- **This API service**: Create an issue in this repository
- **OpenAI API format**: [OpenAI API Documentation](https://platform.openai.com/docs/api-reference/chat)
