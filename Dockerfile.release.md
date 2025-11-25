# Docker Release Process

## Building Docker Images for Releases

To build a Docker image for a specific release:

```bash
# Build with a specific version tag
docker build -t jsi-scraper:v1.0.0 .

# Or build with latest tag as well
docker build -t jsi-scraper:v1.0.0 -t jsi-scraper:latest .
```

## Pushing to Container Registry

To push the image to a container registry (e.g., Docker Hub, GitHub Container Registry):

```bash
# Tag for your registry (replace with your registry details)
docker tag jsi-scraper:v1.0.0 your-registry/jsi-scraper:v1.0.0

# Push to registry
docker push your-registry/jsi-scraper:v1.0.0
```

## Running Released Versions

To run a specific version:

```bash
# Run a specific version
docker run -p 8000:8000 jsi-scraper:v1.0.0

# Or with environment variables
docker run -p 8000:8000 -e ENV=production jsi-scraper:v1.0.0
```

## Multi-platform Builds (Optional)

For supporting multiple architectures:

```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t jsi-scraper:v1.0.0 --push .
```