# Building the Docker Image

This guide covers building the Holo1.5-7B Docker image for deployment on RunPod and other GPU platforms.

## Recommended: Use GitHub Actions (Automated)

**Don't build locally!** GitHub Actions automatically builds images for you:

✅ **Automatic builds** on every release and push to main
✅ **No disk space issues** - runs on GitHub's servers
✅ **Faster** - native x86_64 build (no emulation)
✅ **Free** - 2000 minutes/month on free tier

### How It Works

1. **Push code or create a release** → GitHub Actions triggers
2. **GitHub builds the image** on their x86_64 servers
3. **Image automatically pushed** to `ghcr.io/r0mainbatlle/holo1.5-endpoint`
4. **Ready to deploy** on RunPod or anywhere

### Setup (One-Time)

The workflow is already configured in `.github/workflows/docker-build.yml`.

**Enable workflow permissions:**
1. Go to: https://github.com/R0mainBatlle/holo1.5-endpoint/settings/actions
2. Under "Workflow permissions", select: **Read and write permissions**
3. Click "Save"

That's it! Now every release will automatically build and push.

### Trigger a Build

**Automatic (on release):**
```bash
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
# GitHub Actions automatically builds and pushes
```

**Manual (via GitHub UI):**
1. Go to: https://github.com/R0mainBatlle/holo1.5-endpoint/actions
2. Select "Build and Push Docker Image"
3. Click "Run workflow" → "Run workflow"

**On push to main:**
```bash
git push origin main
# Automatically triggers build
```

### Monitor Build Progress

View builds at: https://github.com/R0mainBatlle/holo1.5-endpoint/actions

Build typically takes **10-15 minutes**.

---

## Manual Building (Not Recommended)

If you must build locally (not recommended due to disk space and speed), see below.

### Important: Architecture Considerations

The image **must be built for AMD64/x86_64** architecture since:
- NVIDIA GPUs require x86_64
- RunPod uses x86_64 servers
- The CUDA base image is optimized for x86_64

### Building on Apple Silicon (M1/M2/M3)

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

## GitHub Actions (Already Configured!)

✅ **The workflow is already set up** at `.github/workflows/docker-build.yml`

No need to create anything - just:
1. Enable workflow permissions (see top of this document)
2. Create a release or push to main
3. GitHub automatically builds and pushes

See the "Recommended: Use GitHub Actions" section at the top for full details.

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
