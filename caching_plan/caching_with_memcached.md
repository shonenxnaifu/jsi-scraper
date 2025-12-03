# Implementing Caching with Memcached

## Overview
Memcached is a high-performance, distributed memory caching system. This guide shows how to implement caching for your JSI Scraper API using Memcached.

## Step 1: Install Required Dependencies

```bash
pip install pymemcache
```

## Step 2: Update requirements.txt

```txt
beautifulsoup4==4.12.2
fastapi==0.121.3
gunicorn==21.2.0
pydantic==2.12.4
pymemcache==4.0.0
requests==2.31.0
uvicorn[standard]==0.38.0
```

## Step 3: Create a Memcached Cache Manager

Create a new file `app/cache_manager.py`:

```python
import json
import os
from typing import Any, Optional
from pymemcache.client.base import Client
from pymemcache import serde

class MemcachedCacheManager:
    def __init__(self):
        # Get Memcached host and port from environment variables
        host = os.getenv("MEMCACHED_HOST", "localhost")
        port = int(os.getenv("MEMCACHED_PORT", "11211"))
        
        # Create Memcached client
        self.client = Client(
            (host, port),
            serde=serde.pickle_serde,  # Use pickle for serialization
            connect_timeout=60,
            timeout=60,
            no_delay=True
        )
    
    def _generate_key(self, max_pages: Optional[int], format_type: str) -> str:
        """Generate cache key based on parameters"""
        max_pages_str = str(max_pages) if max_pages is not None else "all"
        return f"scrape:{max_pages_str}:{format_type}"
    
    def get(self, max_pages: Optional[int], format_type: str) -> Optional[Any]:
        """Get cached data"""
        key = self._generate_key(max_pages, format_type)
        try:
            value = self.client.get(key)
            return value
        except Exception as e:
            print(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, max_pages: Optional[int], format_type: str, data: Any, ttl: int = 3600) -> None:
        """Set cached data with TTL"""
        key = self._generate_key(max_pages, format_type)
        try:
            self.client.set(key, data, expire=ttl)
        except Exception as e:
            print(f"Error setting cache key {key}: {e}")
    
    def delete(self, max_pages: Optional[int], format_type: str) -> bool:
        """Delete specific cache entry"""
        key = self._generate_key(max_pages, format_type)
        try:
            result = self.client.delete(key)
            return result
        except Exception as e:
            print(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear_all(self) -> int:
        """Clear all cache entries (flush all)"""
        try:
            self.client.flush_all()
            return 1  # Memcached flush_all doesn't return count
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return 0
    
    def cache_info(self) -> dict:
        """Get cache statistics"""
        try:
            stats = self.client.stats()
            return {
                "version": stats.get(b'version', b'unknown').decode('utf-8'),
                "curr_items": int(stats.get(b'curr_items', 0)),
                "total_items": int(stats.get(b'total_items', 0)),
                "bytes": int(stats.get(b'bytes', 0)),
                "curr_connections": int(stats.get(b'curr_connections', 0)),
                "get_hits": int(stats.get(b'get_hits', 0)),
                "get_misses": int(stats.get(b'get_misses', 0)),
            }
        except Exception as e:
            print(f"Error getting cache info: {e}")
            return {"error": str(e)}

# Create global cache manager instance
cache_manager = MemcachedCacheManager()
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
    return {"message": f"Cleared cache entries"}
```

## Step 7: Docker Configuration

Update your Dockerfile to include Memcached service:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8021

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8021"]
```

Update your docker-compose.yml:

```yaml
version: '3.8'

services:
  memcached:
    image: memcached:latest
    restart: unless-stopped
    ports:
      - "11211:11211"
    command: memcached -m 512m  # Allocate 512MB memory

  jsi-scraper:
    build: .
    ports:
      - "8021:8021"
    environment:
      - MEMCACHED_HOST=memcached
      - MEMCACHED_PORT=11211
    volumes:
      - /tmp/jsi_scraper_data:/tmp
    depends_on:
      - memcached
    restart: unless-stopped
```

## Step 8: Running with Docker

1. Build and run with Docker:

```bash
docker-compose up -d
```

## Step 9: Testing

1. Make sure Memcached service is running: `docker-compose ps`
2. Make a request to `/scrape/json` - this will take the full scraping time
3. Make another request to `/scrape/json` with the same parameters - this should return instantly from cache
4. Check cache status at `/cache/status`
5. Clear cache if needed at `/cache/clear`

## Important Note about Memcached

Since Memcached has no persistence, all cached data will be lost when:
- The Memcached service restarts
- The server reboots
- The Docker container is recreated

If you need persistence, consider using Redis instead, or implement a cache warming strategy after restarts.

This implementation provides high-performance caching with Memcached while maintaining the functionality of your existing scraper.