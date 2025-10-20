# Holo1.5-7B FastAPI Service (OpenAI Compatible)

[![Runpod](https://api.runpod.io/badge/R0mainBatlle/holo1.5-endpoint)](https://console.runpod.io/hub/R0mainBatlle/holo1.5-endpoint)
[![Build](https://github.com/R0mainBatlle/holo1.5-endpoint/actions/workflows/docker-build.yml/badge.svg)](https://github.com/R0mainBatlle/holo1.5-endpoint/actions/workflows/docker-build.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://hub.docker.com)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI-Compatible-412991?style=for-the-badge&logo=openai)](https://platform.openai.com/docs/api-reference)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](LICENSE)

A dockerized FastAPI service providing an **OpenAI-compatible API** for the Holo1.5-7B Vision Language Model. The model is **baked into the Docker image** for instant startup with no downloads required.

## Model Information

**Holo1.5-7B** is a Vision Language Model (VLM) specialized for:
- UI localization and element detection
- Screen content understanding
- Answering questions about UI interfaces
- Supports up to 3840 × 2160 pixel resolution

Model page: [Hcompany/Holo1.5-7B](https://huggingface.co/Hcompany/Holo1.5-7B)

## Key Features

- **Model Baked Into Image** - No runtime downloads, instant startup
- **OpenAI-Compatible API** - Works with OpenAI SDKs and tools
- **RunPod Serverless Ready** - Configured for RunPod Hub with automated tests
- **Image URLs** - Fetch images directly from URLs
- **Base64 Images** - Support for embedded images
- **Standard Format** - Compatible with LangChain, OpenAI SDK, etc.
- **Docker Ready** - Easy deployment with GPU or CPU
- **No Volume Management** - Everything included in the image

## Architecture

**Build Time:**
- Model (~14GB) is downloaded during Docker build
- Added to image layers
- Only happens once when building the image

**Runtime:**
- Container starts instantly with model already loaded
- No volume mounts or downloads needed
- Predictable, fast startup every time

**Trade-offs:**
- ✅ Instant container startup (~30-60 seconds for model loading)
- ✅ No runtime dependencies or volume management
- ✅ Perfect for RunPod and serverless deployments
- ⚠️ Larger image size (~16-18GB vs ~2GB)
- ⚠️ Longer build time (5-10 minutes)
- ⚠️ Must rebuild image to update model

## Project Structure

```
holo-fastapi-service/
├── .runpod/
│   ├── hub.json             # RunPod Hub configuration
│   └── tests.json           # RunPod automated tests
├── app/
│   └── main.py              # FastAPI application
├── Dockerfile               # GPU-enabled Dockerfile (model baked in)
├── Dockerfile.cpu           # CPU-only Dockerfile (model baked in)
├── docker-compose.yml       # Docker Compose configuration
├── download_model.py        # Script to download model during build
├── handler.py               # RunPod serverless handler
├── start_runpod.sh          # RunPod startup script
├── requirements.txt         # Python dependencies
├── test_api.py              # Test script
└── README.md                # This file
```

## Requirements

### Hardware Requirements
- **GPU Version**: NVIDIA GPU with at least 16GB VRAM (recommended)
- **CPU Version**: Works but significantly slower (~10x)
- **Disk Space**: ~20GB for Docker image

### Software Requirements
- Docker
- Docker Compose (optional but recommended)
- NVIDIA Container Toolkit (for GPU support)

## Quick Start

### Automated Builds
✅ **Docker images are automatically built by GitHub Actions** on every release and push to main.
✅ **No local building required** - just pull and run!

Images are available at: `ghcr.io/r0mainbatlle/holo1.5-endpoint:latest`

### Build Notes (For Manual Builds)
⚠️ **First build takes 10-15 minutes** to download the ~14GB model.

⚠️ **Apple Silicon Users (M1/M2/M3):** Manual building requires 20-25GB disk space. **Recommended: Use pre-built images or GitHub Actions instead.**

See [BUILD.md](BUILD.md) for detailed manual build instructions.

### Option 1: Using Pre-built Image (Recommended - Fastest)

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/r0mainbatlle/holo1.5-endpoint:latest

# Run the container
docker run --gpus all -p 8000:8000 ghcr.io/r0mainbatlle/holo1.5-endpoint:latest
```

### Option 2: Docker Compose (GPU - Recommended)

```bash
# Build the image (downloads model during build)
docker-compose build

# Run the container (starts instantly)
docker-compose up
```

### Option 3: Docker Build (x86_64 Linux)

```bash
# Build the image (downloads model during build - takes 10-15 min)
docker build -t holo-api .

# Run the container (starts in seconds)
docker run --gpus all -p 8000:8000 holo-api
```

### Option 4: Docker Build (Apple Silicon)

```bash
# Build for AMD64 platform (required for GPU deployment)
docker buildx build --platform linux/amd64 -t holo-api --load .

# Run with emulation (slow, for testing only)
docker run --platform linux/amd64 -p 8000:8000 holo-api
```

**Note:** For production deployment, push to a registry and run on x86_64 hardware.

### Option 5: Docker (CPU only)

```bash
# Build the CPU image
docker build -f Dockerfile.cpu -t holo-api-cpu .

# Run the container
docker run -p 8000:8000 holo-api-cpu
```

### Option 6: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application (model downloads on first run)
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

With the model baked into the image, RunPod deployment is **extremely simple** - no network volumes needed!

### Quick Deploy

1. **Build and push your image** (or use GitHub Actions):
```bash
# Build
docker build -t your-registry/holo-api:latest .

# Push to registry
docker push your-registry/holo-api:latest
```

2. **Deploy on RunPod**:
```yaml
# Container Image
your-registry/holo-api:latest

# Container Ports
8000

# Environment Variables (optional)
# HF_TOKEN=your_token_here

# GPU Configuration
GPU: A40 (or any GPU with 16GB+ VRAM)
```

3. **That's it!** Container starts in 30-60 seconds with model ready.

### RunPod Docker Command

```bash
docker run --runtime nvidia --gpus all \
  -p 8000:8000 \
  --ipc=host \
  your-registry/holo-api:latest
```

### Benefits for RunPod

| Aspect | With Baked Model | With Network Volume |
|--------|-----------------|---------------------|
| **Startup Time** | 30-60 seconds | 30-60 seconds after first download |
| **First Start** | Same as every start | 5-10 min download |
| **Complexity** | Simple - just run | Need volume setup |
| **Cost** | Image storage only | Image + volume storage |
| **Reliability** | Always works | Depends on volume mount |
| **Portability** | Perfect | Volume tied to datacenter |

**Recommendation**: For RunPod, the baked-in model approach is simpler and more reliable.

### RunPod Serverless

This repository is configured for **RunPod Serverless** deployment with automatic testing and validation.

#### Files for RunPod Serverless

```
.runpod/
├── hub.json     # RunPod Hub configuration
└── tests.json   # Automated tests for validation

handler.py       # RunPod serverless handler
start_runpod.sh  # Startup script for serverless
```

#### Handler Usage

The RunPod serverless handler accepts two input formats:

**1. Simple Format:**
```json
{
  "input": {
    "image_url": "https://example.com/screenshot.png",
    "text": "Where is the login button?",
    "max_tokens": 512
  }
}
```

**2. OpenAI Format:**
```json
{
  "input": {
    "model": "Hcompany/Holo1.5-7B",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Describe this UI"},
          {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
      }
    ]
  }
}
```

**Response Format:**
```json
{
  "status": "success",
  "output": {
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "The model's response..."
        }
      }
    ]
  }
}
```

#### Deploying to RunPod Hub

1. **Push to GitHub**:
```bash
git add .
git commit -m "Add RunPod serverless support"
git push origin main
```

2. **Create a Release**:
```bash
# Create and push a tag
git tag -a v1.0.0 -m "Release v1.0.0 - RunPod Serverless"
git push origin v1.0.0
```

Or via GitHub UI:
- Go to your repository → Releases → Create new release
- Choose a tag (e.g., `v1.0.0`)
- Add release notes
- Publish release

3. **Submit to RunPod Hub**:
- Your repository will be automatically discovered by RunPod Hub
- The `.runpod/hub.json` and `.runpod/tests.json` files configure everything
- Tests will run automatically to validate the deployment

4. **Access on RunPod**:
- Once approved, your endpoint will be available on RunPod Hub
- Users can deploy with one click
- Automatic scaling and billing

#### Testing Handler Locally

```bash
# Start the FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Test the handler
python handler.py
```

#### Environment Variables for Serverless

```bash
API_BASE_URL=http://localhost:8000  # Usually localhost in serverless
HF_TOKEN=your_token_here            # Optional, for gated models
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
# Model cache is baked into image at /app/model_cache
# These are set in the Dockerfile and normally don't need changing

# Optional: Hugging Face token (if needed for gated models)
HF_TOKEN=your_token_here
```

### Model Configuration

Edit `app/main.py` to adjust:
- `max_tokens`: Maximum length of generated response (default: 512)
- `torch_dtype`: Precision (bfloat16 for GPU, float32 for CPU)
- `temperature`: Not currently used but accepted in API

## Build Customization

### To rebuild with updated model:

```bash
# Force rebuild (ignores cache)
docker build --no-cache -t holo-api .

# Or clear specific layer
docker build --pull -t holo-api .
```

### To skip model download during build (for testing):

Comment out the download step in `Dockerfile`:
```dockerfile
# RUN python3 download_model.py
```

## Troubleshooting

### Out of Memory (GPU)
- Reduce `max_tokens` in requests
- Use GPU with more VRAM (24GB+ recommended)
- Model requires ~16GB VRAM during inference

### Slow Performance (CPU)
- **Strongly recommend GPU** for production
- Reduce image resolution before sending
- Expected ~10x slower than GPU

### Build Fails During Model Download
- Check internet connection
- Ensure sufficient disk space (~20GB)
- Try increasing Docker memory limit
- Check Docker Hub rate limits

### Container Starts But Model Not Found
- Ensure build completed successfully
- Check build logs for download errors
- Verify `TRANSFORMERS_CACHE=/app/model_cache` is set

### Large Image Size
- This is expected (~16-18GB)
- Required to include the 14GB model
- Use registry with sufficient storage
- Consider using Docker layer caching

## Performance Notes

- **Container startup**: 30-60 seconds (model loading to GPU)
- **First request**: 1-5 seconds
- **Subsequent requests**: 1-5 seconds per request
- **GPU vs CPU**: GPU is ~10x faster
- **Image size**: ~16-18GB (includes 14GB model)
- **Build time**: 5-10 minutes (one-time per build)
- **VRAM usage**: ~16GB during inference

## Comparison: Baked-in vs Runtime Download

| Aspect | Baked Into Image (This Repo) | Runtime Download |
|--------|------------------------------|------------------|
| **Container Startup** | 30-60 sec | 30-60 sec (after download) |
| **First Start** | Same every time | 5-10 min download |
| **Image Size** | ~16-18GB | ~2GB |
| **Build Time** | 5-10 min | 1-2 min |
| **Volumes Needed** | None | Yes (for persistence) |
| **Network Required** | Only during build | Every first start |
| **RunPod Setup** | Simple | Need network volumes |
| **Best For** | Production, RunPod | Development |

## Model Cache Location

The model is baked into the image at:
```
/app/model_cache/
```

Environment variables set in Dockerfile:
```bash
TRANSFORMERS_CACHE=/app/model_cache
HF_HOME=/app/model_cache
```

## License

This project uses the Holo1.5-7B model which is licensed under Apache 2.0.

## Support

For issues specific to:
- **The model**: [Hcompany/Holo1.5-7B](https://huggingface.co/Hcompany/Holo1.5-7B)
- **This API service**: Create an issue in this repository
- **OpenAI API format**: [OpenAI API Documentation](https://platform.openai.com/docs/api-reference/chat)

## FAQ

**Q: Why is the image so large?**
A: The model is ~14GB, so the total image is ~16-18GB. This is the trade-off for instant startup.

**Q: Can I use network volumes instead?**
A: Yes, but it's not necessary with this setup. The model is already in the image.

**Q: Do I need to rebuild to update the model?**
A: Yes. When a new version is released, rebuild the image with `docker build --no-cache`.

**Q: Will this work on RunPod serverless?**
A: Yes! Perfect for serverless since there's no initialization delay.

**Q: How do I reduce image size?**
A: You can use model quantization or switch to runtime download approach, but you'll lose the instant startup benefit.
