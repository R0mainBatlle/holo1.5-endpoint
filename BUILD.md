# Building the Docker Image

This guide covers building the Holo1.5-7B Docker image for deployment on RunPod and other GPU platforms.

## Important: Architecture Considerations

The image **must be built for AMD64/x86_64** architecture since:
- NVIDIA GPUs require x86_64
- RunPod uses x86_64 servers
- The CUDA base image is optimized for x86_64

## Building on Apple Silicon (M1/M2/M3)

If you're on an Apple Silicon Mac, you **must** specify the platform:

```bash
docker buildx build --platform linux/amd64 -t ghcr.io/r0mainbatlle/holo1.5-endpoint:latest .
```

**Why?** Your Mac is ARM64, but the image needs to run on AMD64 GPUs.

### Setup Docker Buildx (First Time Only)

If you get an error about buildx, set it up once:

```bash
# Create a new builder instance
docker buildx create --name multiarch --use

# Verify it's ready
docker buildx inspect --bootstrap
```

## Building on x86_64 Linux

If you're already on x86_64 Linux (not Apple Silicon):

```bash
docker build -t ghcr.io/r0mainbatlle/holo1.5-endpoint:latest .
```

## Build Options

### Full Build (Recommended for Production)

Downloads and includes the model (~14GB):

```bash
docker buildx build --platform linux/amd64 \
  -t ghcr.io/r0mainbatlle/holo1.5-endpoint:latest \
  --push .
```

The `--push` flag automatically pushes to the registry after building.

### Build Without Push

Build locally first, push later:

```bash
# Build
docker buildx build --platform linux/amd64 \
  -t ghcr.io/r0mainbatlle/holo1.5-endpoint:latest \
  --load .

# Push later
docker push ghcr.io/r0mainbatlle/holo1.5-endpoint:latest
```

**Note:** `--load` loads the image into your local Docker, but only works with single platform builds.

### Build Time Expectations

- **First build**: 10-15 minutes (downloads ~14GB model)
- **Subsequent builds**: 1-2 minutes (uses cache)
- **Final image size**: ~16-18GB

## Pushing to GitHub Container Registry

### 1. Create a GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `write:packages`
   - `read:packages`
   - `delete:packages`
4. Copy the token

### 2. Login to GitHub Container Registry

```bash
echo YOUR_TOKEN | docker login ghcr.io -u R0mainBatlle --password-stdin
```

### 3. Build and Push

```bash
docker buildx build --platform linux/amd64 \
  -t ghcr.io/r0mainbatlle/holo1.5-endpoint:latest \
  --push .
```

## Multi-Version Tagging

Tag the same image with multiple tags:

```bash
docker buildx build --platform linux/amd64 \
  -t ghcr.io/r0mainbatlle/holo1.5-endpoint:latest \
  -t ghcr.io/r0mainbatlle/holo1.5-endpoint:v1.0.0 \
  --push .
```

## Testing the Built Image Locally

### On Apple Silicon (with Rosetta emulation):

```bash
docker run --platform linux/amd64 -p 8000:8000 \
  ghcr.io/r0mainbatlle/holo1.5-endpoint:latest
```

**Note:** This will be slow (CPU emulation), but good for testing the build.

### On x86_64 Linux with GPU:

```bash
docker run --gpus all -p 8000:8000 \
  ghcr.io/r0mainbatlle/holo1.5-endpoint:latest
```

### Check if it's working:

```bash
# Health check
curl http://localhost:8000/health

# Test with an image
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Hcompany/Holo1.5-7B",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What is this?"},
        {"type": "image_url", "image_url": {"url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"}}
      ]
    }]
  }'
```

## Troubleshooting

### Error: "multiple platforms feature is currently not supported"

Use buildx instead of regular build:

```bash
docker buildx build --platform linux/amd64 ...
```

### Error: "failed to solve: nvidia/cuda:12.1.0-runtime-ubuntu22.04: no match for platform"

Make sure you're using buildx with the correct platform flag.

### Error: "denied: permission_denied"

Login to the registry:

```bash
echo YOUR_TOKEN | docker login ghcr.io -u R0mainBatlle --password-stdin
```

### Error: GPG signature errors during build

This usually happens when:
1. Building on wrong architecture without specifying platform
2. Docker cache is corrupted

**Solution:**
```bash
# Build with platform specified
docker buildx build --platform linux/amd64 --no-cache ...
```

### Build is very slow on Apple Silicon

This is expected when building AMD64 images on ARM. The build must:
1. Emulate x86_64 architecture
2. Download 14GB model
3. Process everything through emulation

**Expected time:** 15-30 minutes on Apple Silicon

### Out of disk space

The final image is ~16-18GB. Ensure you have at least 25GB free:

```bash
# Check disk space
df -h

# Clean up old Docker images
docker system prune -a
```

## GitHub Actions (Automated Builds)

To avoid manual building, set up GitHub Actions to build automatically on release.

Create `.github/workflows/docker-build.yml`:

```yaml
name: Build and Push Docker Image

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/amd64
          push: true
          tags: |
            ghcr.io/r0mainbatlle/holo1.5-endpoint:latest
            ghcr.io/r0mainbatlle/holo1.5-endpoint:${{ github.ref_name }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

This will automatically build and push whenever you create a GitHub release.

## Summary

**On Apple Silicon:**
```bash
docker buildx build --platform linux/amd64 \
  -t ghcr.io/r0mainbatlle/holo1.5-endpoint:latest \
  --push .
```

**On x86_64 Linux:**
```bash
docker build -t ghcr.io/r0mainbatlle/holo1.5-endpoint:latest .
docker push ghcr.io/r0mainbatlle/holo1.5-endpoint:latest
```

**Build time:** 10-15 minutes
**Image size:** ~16-18GB
**Target platform:** linux/amd64 (for NVIDIA GPUs)
