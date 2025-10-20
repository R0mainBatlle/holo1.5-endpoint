# Holo1.5-7B FastAPI Service

A dockerized FastAPI endpoint for the Holo1.5-7B Vision Language Model, which takes an image and text as input and returns model predictions.

## Model Information

**Holo1.5-7B** is a Vision Language Model (VLM) specialized for:
- UI localization and element detection
- Screen content understanding
- Answering questions about UI interfaces
- Supports up to 3840 × 2160 pixel resolution

Model page: [Hcompany/Holo1.5-7B](https://huggingface.co/Hcompany/Holo1.5-7B)

## Project Structure

```
holo-fastapi-service/
├── app/
│   └── main.py              # FastAPI application
├── Dockerfile               # GPU-enabled Dockerfile
├── Dockerfile.cpu           # CPU-only Dockerfile
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Requirements

### Hardware Requirements
- **GPU Version**: NVIDIA GPU with at least 16GB VRAM (recommended)
- **CPU Version**: Works but will be significantly slower

### Software Requirements
- Docker
- Docker Compose (optional but recommended)
- NVIDIA Container Toolkit (for GPU support)

## Quick Start

### Option 1: Using Docker Compose (GPU)

```bash
docker-compose up --build
```

### Option 2: Using Docker (GPU)

```bash
# Build the image
docker build -t holo-api .

# Run the container
docker run --gpus all -p 8000:8000 holo-api
```

### Option 3: Using Docker (CPU only)

```bash
# Build the CPU image
docker build -f Dockerfile.cpu -t holo-api-cpu .

# Run the container
docker run -p 8000:8000 holo-api-cpu
```

### Option 4: Local Development (without Docker)

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

### Health Check

```bash
curl http://localhost:8000/health
```

### Make a Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "image=@/path/to/your/image.png" \
  -F "text=What is in this image?"
```

### Python Example

```python
import requests

url = "http://localhost:8000/predict"

with open("screenshot.png", "rb") as image_file:
    files = {"image": image_file}
    data = {"text": "Where is the search button located?"}
    response = requests.post(url, files=files, data=data)

print(response.json())
```

### JavaScript/Node.js Example

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('image', fs.createReadStream('screenshot.png'));
form.append('text', 'Where is the search button located?');

axios.post('http://localhost:8000/predict', form, {
  headers: form.getHeaders()
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

## API Endpoints

### `GET /`
Health check endpoint
- Returns basic service status

### `GET /health`
Detailed health check
- Returns model loading status and device information

### `POST /predict`
Main prediction endpoint
- **Parameters:**
  - `image` (file): Image file to analyze (PNG, JPG, etc.)
  - `text` (form field): Text query or instruction for the model
- **Returns:** JSON with model output

**Response format:**
```json
{
  "success": true,
  "text_input": "Your input text",
  "model_output": "Model's response"
}
```

## What Image Input to Provide

The Holo1.5-7B model is optimized for **UI/interface screenshots**:

### Recommended Image Types:
1. **Web page screenshots** - Browser interfaces, websites
2. **Desktop application screenshots** - Windows, Mac, or Linux UIs
3. **Mobile app screenshots** - iOS or Android interfaces
4. **UI mockups** - Design files showing interfaces

### Supported Formats:
- PNG
- JPG/JPEG
- WEBP
- Any format supported by PIL/Pillow

### Resolution:
- Up to 3840 × 2160 pixels natively supported
- Higher resolutions will be automatically resized

### Example Use Cases:

**1. Element Localization**
```
Image: Screenshot of a web page
Text: "Where is the login button?"
```

**2. UI Understanding**
```
Image: Mobile app screenshot
Text: "What options are available in the settings menu?"
```

**3. Screen Content QA**
```
Image: Desktop application
Text: "What is the text in the notification area?"
```

**4. Navigation Assistance**
```
Image: E-commerce website
Text: "How do I proceed to checkout?"
```

## Configuration

### Environment Variables

You can customize the service with environment variables:

```bash
# Cache directory for model files
TRANSFORMERS_CACHE=/path/to/cache

# Hugging Face token (if model requires authentication)
HF_TOKEN=your_token_here
```

### Model Configuration

Edit `app/main.py` to adjust:
- `max_new_tokens`: Maximum length of generated response (default: 512)
- `torch_dtype`: Precision (bfloat16 for GPU, float32 for CPU)
- Device placement and memory optimization

## Troubleshooting

### Out of Memory (GPU)
- Reduce batch size or max_new_tokens
- Use a smaller model variant
- Enable model quantization

### Slow Performance (CPU)
- Use GPU version if possible
- Reduce image resolution
- Consider using model quantization

### Model Download Issues
- Ensure stable internet connection
- First run will download ~14GB model
- Check disk space in cache directory

## Performance Notes

- **First request**: Will be slower as the model loads (~1-2 minutes)
- **Subsequent requests**: Much faster
- **GPU recommended**: For production use
- **Model size**: ~14GB download

## License

This project uses the Holo1.5-7B model which is licensed under Apache 2.0.

## Support

For issues specific to:
- The model: [Hcompany/Holo1.5-7B](https://huggingface.co/Hcompany/Holo1.5-7B)
- This API service: Create an issue in this repository
