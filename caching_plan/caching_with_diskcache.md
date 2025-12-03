# Implementing Caching with DiskCache

## Overview
DiskCache is a Python caching library that provides disk-based caching using SQLite. This guide shows how to implement caching for your JSI Scraper API using DiskCache, which was recommended in your original cache plan.

## Step 1: Install Required Dependencies

```bash
pip install diskcache
```

## Step 2: Update requirements.txt

```txt
beautifulsoup4==4.12.2
diskcache==5.6.1
fastapi==0.121.3
gunicorn==21.2.0
pydantic==2.12.4
requests==2.31.0
uvicorn[standard]==0.38.0
```

## Step 3: Create a DiskCache Manager

Create a new file `app/cache_manager.py`:

```python
import diskcache as dc
from pathlib import Path
from typing import Any, Optional
import json
import os

class DiskCacheManager:
    def __init__(self, cache_dir: str = "/tmp/jsi_cache"):
        # Allow cache directory to be configured via environment variable
        cache_dir = os.getenv("DISKCACHE_DIR", cache_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = dc.Cache(self.cache_dir)
    
    def _generate_key(self, max_pages: Optional[int], format_type: str) -> str:
        """Generate cache key based on parameters"""
        max_pages_str = str(max_pages) if max_pages is not None else "all"
        return f"scrape:{max_pages_str}:{format_type}"
    
    def get(self, max_pages: Optional[int], format_type: str) -> Optional[Any]:
        """Get cached data"""
        key = self._generate_key(max_pages, format_type)
        try:
            return self.cache.get(key)
        except Exception as e:
            print(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, max_pages: Optional[int], format_type: str, data: Any, ttl: int = 3600) -> None:
        """Set cached data with TTL"""
        key = self._generate_key(max_pages, format_type)
        try:
            self.cache.set(key, data, expire=ttl)
        except Exception as e:
            print(f"Error setting cache key {key}: {e}")
    
    def delete(self, max_pages: Optional[int], format_type: str) -> bool:
        """Delete specific cache entry"""
        key = self._generate_key(max_pages, format_type)
        try:
            return self.cache.delete(key)
        except Exception as e:
            print(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear_all(self) -> int:
        """Clear all cache entries"""
        try:
            return self.cache.clear()
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return 0
    
    def cache_info(self) -> dict:
        """Get cache statistics"""
        try:
            return {
                "key_count": len(self.cache),
                "cache_size": self.cache.volume(),
                "cache_path": str(self.cache_dir),
                "stats": self.cache.stats(),
                "caches": list(self.cache.itercacheinfo())
            }
        except Exception as e:
            print(f"Error getting cache info: {e}")
            return {"error": str(e)}

# Create global cache manager instance
cache_manager = DiskCacheManager()
```

## Step 4: Update your scraper.py file

Update the `scrape_all_projects` function in `app/scraper.py` to use caching:

```python
# Add import at the top
from .cache_manager import cache_manager

def scrape_all_projects_with_cache(max_pages: Optional[int] = None, format_type: str = "json", progress_callback=None) -> List[Dict]:
    """
    Scrape all projects with caching
    """
    # Try to get from cache first
    cached_result = cache_manager.get(max_pages, format_type)
    if cached_result is not None:
        print(f"Cache HIT for max_pages={max_pages}, format={format_type}")
        return cached_result
    
    print(f"Cache MISS for max_pages={max_pages}, format={format_type}")
    
    # Perform actual scraping
    result = scrape_all_projects(max_pages, progress_callback)
    
    # Cache the result
    cache_manager.set(max_pages, format_type, result)
    
    return result
```

## Step 5: Update main.py to use caching

Update your endpoints in `app/main.py`:

```python
# Add import
from .cache_manager import cache_manager

@app.get("/scrape/json", response_model=ScrapeResponse)
async def scrape_json(
    max_pages: Optional[int] = Query(None, description="Limit the number of project pages to scrape"),
    bypass_cache: bool = Query(False, description="Bypass cache and force fresh scrape")
):
    """
    Scrape project data from jogjasonicindex.com and return as JSON
    """
    # Check cache first (unless bypass_cache is True)
    if not bypass_cache:
        cached_result = cache_manager.get(max_pages, "json")
        if cached_result is not None:
            print(f"Cache HIT for JSON scrape with max_pages={max_pages}")
            return ScrapeResponse(projects=cached_result)
    
    print(f"Cache MISS for JSON scrape with max_pages={max_pages}")
    
    # Check if scraping is already in progress
    if state_manager.is_scraping():
        raise HTTPException(status_code=423, detail="Scraping process is currently in progress. Please wait until it completes or check status at /scrape/status")

    try:
        logger.info("Starting JSON scraping process...")
        state_manager.start_scraping()

        def progress_callback(progress, total_projects):
            state_manager.update_progress(progress, total_projects)

        # Use caching version
        projects = scrape_all_projects_with_cache(max_pages=max_pages, format_type="json", progress_callback=progress_callback)
        logger.info(f"Scraping completed. Total projects: {len(projects)}")
        state_manager.finish_scraping(f"Scraping completed. Total projects: {len(projects)}")

        # Cache the result if it wasn't already cached during scraping
        cache_manager.set(max_pages, "json", projects)
        
        response = ScrapeResponse(projects=projects)
        return response
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        state_manager.finish_scraping(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@app.get("/scrape/csv")
async def scrape_csv(
    max_pages: Optional[int] = Query(None, description="Limit the number of project pages to scrape"),
    bypass_cache: bool = Query(False, description="Bypass cache and force fresh scrape")
):
    """
    Scrape project data from jogjasonicindex.com and return as CSV file
    """
    # Check cache first for raw projects (unless bypass_cache is True)
    if not bypass_cache:
        cached_projects = cache_manager.get(max_pages, "json")  # Store as JSON, convert to CSV when needed
        if cached_projects is not None:
            print(f"Cache HIT for CSV scrape with max_pages={max_pages}")
            csv_content = generate_csv_content(cached_projects)
            response = StreamingResponse(io.StringIO(csv_content), media_type="text/csv")
            response.headers["Content-Disposition"] = "attachment; filename=jogjasonicindex_projects.csv"
            return response
    
    print(f"Cache MISS for CSV scrape with max_pages={max_pages}")
    
    # Check if scraping is already in progress
    if state_manager.is_scraping():
        raise HTTPException(status_code=423, detail="Scraping process is currently in progress. Please wait until it completes or check status at /scrape/status")

    try:
        logger.info("Starting CSV scraping process...")
        state_manager.start_scraping()

        def progress_callback(progress, total_projects):
            state_manager.update_progress(progress, total_projects)

        # Use caching version
        projects = scrape_all_projects_with_cache(max_pages=max_pages, format_type="csv", progress_callback=progress_callback)
        
        # Cache the projects as JSON for future CSV and JSON requests
        cache_manager.set(max_pages, "json", projects)
        
        logger.info(f"Scraping completed. Total projects: {len(projects)}")
        state_manager.finish_scraping(f"Scraping completed. Total projects: {len(projects)}")

        # Generate CSV content
        csv_content = generate_csv_content(projects)

        # Create a streaming response for the CSV content
        response = StreamingResponse(io.StringIO(csv_content), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=jogjasonicindex_projects.csv"
        return response
    except Exception as e:
        logger.error(f"Error during CSV scraping: {e}")
        state_manager.finish_scraping(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV scraping failed: {str(e)}")
```

## Step 6: Add Cache Management Endpoints

Add these endpoints to `app/main.py`:

```python
@app.get("/cache/status")
async def cache_status():
    """Get cache statistics and information"""
    return cache_manager.cache_info()

@app.post("/cache/clear")
async def clear_cache():
    """Clear all cached data"""
    deleted_count = cache_manager.clear_all()
    return {"message": f"Cleared {deleted_count} cache entries"}

@app.post("/cache/clear/{format_type}")
async def clear_cache_format(
    format_type: str = Query(..., description="Format type (json/csv)"),
    max_pages: Optional[int] = Query(None, description="Max pages parameter")
):
    """Clear specific cache entry"""
    success = cache_manager.delete(max_pages, format_type)
    if success:
        return {"message": f"Cache entry cleared for max_pages={max_pages}, format={format_type}"}
    else:
        return {"message": f"No cache entry found for max_pages={max_pages}, format={format_type}"}
```

## Step 7: Docker Configuration

Update your Dockerfile to include volume for persistent cache:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create cache directory
RUN mkdir -p /tmp/jsi_cache

EXPOSE 8021

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8021"]
```

### Dockerfile Explanation:

```dockerfile
FROM python:3.10-slim
```
- **Purpose**: Specifies the base image for the container
- **Explanation**: Uses the official Python 3.10 slim image, which is a minimal Linux distribution with Python pre-installed
- **Why `slim`**: Reduces image size and attack surface by including only essential packages

```dockerfile
WORKDIR /app
```
- **Purpose**: Sets the working directory inside the container
- **Explanation**: All subsequent commands will be executed relative to `/app`
- **Benefit**: Organizes the application code in a consistent location

```dockerfile
COPY requirements.txt .
```
- **Purpose**: Copies the requirements file into the container
- **Explanation**: The `.` represents the current working directory (`/app`)
- **Benefit**: Allows Docker to cache the dependency installation layer

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```
- **Purpose**: Installs Python dependencies
- **`--no-cache-dir`**: Prevents pip from caching downloaded packages, reducing final image size
- **Benefit**: Ensures dependencies are available when the application runs

```dockerfile
COPY . .
```
- **Purpose**: Copies all application files from the host's current directory to the container's `/app` directory
- **Explanation**: The first `.` is the source (current directory on host), the second `.` is the destination in container (`/app`)

```dockerfile
# Create cache directory
RUN mkdir -p /tmp/jsi_cache
```
- **Purpose**: Creates a directory for temporary cache files
- **`-p`**: Creates parent directories if they don't exist and doesn't error if the directory already exists
- **Note**: This directory is created for compatibility but the actual cache will be stored in the mounted volume

```dockerfile
EXPOSE 8021
```
- **Purpose**: Documents which port the container will listen on
- **Explanation**: This is purely informational for humans reading the Dockerfile; it doesn't actually publish the port
- **Port 8021**: Matches the port specified in your application's uvicorn command

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8021"]
```
- **Purpose**: Specifies the command to run when the container starts
- **`["command", "arg1", "arg2"]` format**: JSON array format (exec form) is preferred over shell form
- **`--host 0.0.0.0`**: Allows the application to accept connections from outside the container
- **`--port 8021`**: Uses the same port exposed in the EXPOSE instruction

Update your docker-compose.yml:

```yaml
version: '3.8'

services:
  jsi-scraper:
    build: .
    ports:
      - "8021:8021"
    environment:
      - DISKCACHE_DIR=/cache
    volumes:
      - /tmp/jsi_scraper_data:/tmp
      - jsi_cache_volume:/cache  # Named volume for persistent cache
    restart: unless-stopped

volumes:
  jsi_cache_volume:
```

### docker-compose.yml Explanation:

```yaml
version: '3.8'
```
- **Purpose**: Specifies the Docker Compose file format version
- **Version 3.8**: Is compatible with modern Docker versions and supports all the features we'll use

```yaml
services:
  jsi-scraper:
```
- **Purpose**: Defines a service called `jsi-scraper`
- **Explanation**: A service represents a containerized application component

```yaml
    build: .
```
- **Purpose**: Tells Docker Compose to build an image from the current directory (where the docker-compose.yml file is located)
- **Explanation**: Uses the Dockerfile in the current directory to build the image

```yaml
    ports:
      - "8021:8021"
```
- **Purpose**: Maps a port on the host to a port in the container
- **Format**: `"HOST_PORT:CONTAINER_PORT"`
- **Explanation**: Traffic to port 8021 on the host machine will be forwarded to port 8021 in the container

```yaml
    environment:
      - DISKCACHE_DIR=/cache
```
- **Purpose**: Sets environment variables in the container
- **`DISKCACHE_DIR=/cache`**: Tells the application to store cache files in the `/cache` directory
- **How it works**:
  - In the cache manager code (`app/cache_manager.py`), the `DiskCacheManager` class checks for this environment variable:
    ```python
    cache_dir = os.getenv("DISKCACHE_DIR", "/tmp/jsi_cache")
    ```
  - `os.getenv("variable_name", "default_value")` is a Python function that:
    - Looks for an environment variable named "DISKCACHE_DIR"
    - If found, returns its value (in this case "/cache")
    - If not found, returns the default value ("/tmp/jsi_cache")
  - So when Docker Compose sets `DISKCACHE_DIR=/cache`, the application uses "/cache" instead of the default
- **Benefit**: Allows the application to use a specific directory that we can mount as a persistent volume

```yaml
    volumes:
      - /tmp/jsi_scraper_data:/tmp
      - jsi_cache_volume:/cache  # Named volume for persistent cache
```
- **Purpose**: Mounts directories from the host to the container or creates persistent volumes
- **Volume Syntax**: `SOURCE:TARGET` where SOURCE is the host path or volume name, TARGET is the container path
- **First volume** (`/tmp/jsi_scraper_data:/tmp`):
  - **Type**: Bind mount (mounts a host directory into the container)
  - **SOURCE**: `/tmp/jsi_scraper_data` on the host machine
  - **TARGET**: `/tmp` inside the container
  - **Purpose**: Allows sharing data between host and container for temporary files
- **Second volume** (`jsi_cache_volume:/cache`):
  - **Type**: Named volume (managed by Docker, stored in Docker's storage area)
  - **SOURCE**: `jsi_cache_volume` (defined at the bottom of docker-compose.yml)
  - **TARGET**: `/cache` inside the container
  - **Purpose**: Creates persistent storage for cache files that survives container restarts
- **`jsi_cache_volume:/cache` explained**:
  - When the application writes files to `/cache` inside the container, Docker actually stores them in the named volume
  - This volume is completely independent of the container's filesystem
  - The volume persists even if the container is stopped, removed, or recreated
  - This is essential for maintaining cache data across container lifecycle events
- **Benefits of named volumes for caching**:
  - **Persistence**: Cache files survive container restarts, maintaining performance benefits
  - **Isolation**: Cache files are separate from application files and host filesystem
  - **Management**: Can be backed up, copied, or shared independently of containers
  - **Security**: Provides a clear boundary between application code and cached data

```yaml
    restart: unless-stopped
```
- **Purpose**: Sets the restart policy for the container
- **`unless-stopped`**: The container will always restart unless manually stopped with `docker stop`
- **Benefit**: Ensures the service recovers from crashes or system reboots

```yaml
volumes:
  jsi_cache_volume:
```
- **Purpose**: Defines a named volume that can be used by services
- **Syntax**: `volume_name:` where volume_name is the identifier for the volume
- **`jsi_cache_volume`**: Creates a volume with this name that persists data independently of container lifecycle
- **Docker-managed storage**: Docker stores this volume in its own storage area (typically `/var/lib/docker/volumes/` on Linux)
- **Default driver**: Uses Docker's default local storage driver unless specified otherwise
- **Automatic management**: Docker handles the creation, mounting, and cleanup of this volume
- **Benefit**: Cache data will survive container restarts, updates, and removals
- **How it connects**: This volume is referenced by the `jsi_cache_volume:/cache` mapping in the service configuration

### How These Scripts Work Together for DiskCache

1. **Application Configuration**: The `DISKCACHE_DIR=/cache` environment variable tells the application to store cache files in `/cache`

2. **Volume Mounting**: The `jsi_cache_volume:/cache` mapping ensures that data written to `/cache` in the container is stored in the persistent named volume

3. **Relationship between the volumes and the Dockerfile instruction**:
   - **`RUN mkdir -p /tmp/jsi_cache` in Dockerfile**: This creates a directory at `/tmp/jsi_cache` inside the container's filesystem during image build time. This is actually not needed for our cache implementation since we override the default cache location with the environment variable, but it remains harmless. For a cleaner setup, this line could be removed.
   - **`/tmp/jsi_scraper_data:/tmp` bind mount**: This maps the host's `/tmp/jsi_scraper_data` directory to the container's `/tmp` directory. This volume IS needed for the state management functionality in your application (the state manager stores files in `/tmp/jsi_scraper_state.json`). While not directly related to caching, it's necessary to preserve the existing state management functionality.
   - **`jsi_cache_volume:/cache` named volume**: This is THE critical component for our caching implementation - it maps the application's cache directory to a persistent Docker volume.
   - **Complete configuration for both features**:
     1. The environment variable `DISKCACHE_DIR=/cache` tells the application to store cache files in `/cache` inside the container
     2. The named volume `jsi_cache_volume:/cache` ensures that cache data written to `/cache` is stored in the persistent named volume
     3. The bind mount `/tmp/jsi_scraper_data:/tmp` ensures that state files (like `/tmp/jsi_scraper_state.json`) persist across container restarts
   - **Important distinction**: The application stores cache data in `/cache`, which is mapped to the named volume, while state management data is stored in `/tmp`, which is mapped to the bind mount. These are completely separate data storage systems.

4. **Persistence**: Thanks to the named volume, cache data survives container restarts, which is essential for a scraping API where the first request after restart would otherwise lose all the performance benefits of caching

5. **Separation of Concerns**: The cache doesn't interfere with the application code, which remains in the container's filesystem (`/app`)

6. **Scalability**: The volume definition allows for easy management of the persistent data separate from the application container

This configuration ensures that your disk cache persists across container lifecycle events while keeping the application lightweight and portable.

## Step 8: Running with Docker

1. Build and run with Docker:

```bash
docker-compose up -d
```

## Step 9: Testing

1. Make a request to `/scrape/json` - this will take the full scraping time
2. Make another request to `/scrape/json` with the same parameters - this should return instantly from cache
3. Check cache status at `/cache/status`
4. Clear cache if needed at `/cache/clear`
5. The cache will persist across container restarts due to the named volume

## Advantages of DiskCache for Your Use Case

1. **Persistence**: Cache survives container restarts and system reboots
2. **Simplicity**: No external services needed, just a library
3. **Thread-safe**: Works well with your multi-threading approach
4. **Efficient**: Uses SQLite for fast access to cached data
5. **Low overhead**: Minimal resource usage compared to separate cache services

This implementation provides persistent caching with DiskCache while maintaining the functionality of your existing scraper and providing the performance benefits you're looking for.