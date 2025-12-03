# Implementing Caching with Upstash Redis

## Overview
Upstash is a serverless Redis provider that offers pay-per-request pricing with sub-millisecond latency. This guide shows how to implement caching for your JSI Scraper API using Upstash.

## Step 1: Create Upstash Account and Database

1. Go to https://upstash.com/
2. Sign up for a free account
3. Click "Create Database"
4. Choose a region closest to your server
5. Select "Redis" as the database type
6. Click "Create"
7. Copy the "REST API URL" and "REST API Token" from your database dashboard

## Step 2: Install Required Dependencies

```bash
pip install redis upstash-redis
```

## Step 3: Update requirements.txt

```txt
beautifulsoup4==4.12.2
fastapi==0.121.3
gunicorn==21.2.0
pydantic==2.12.4
redis==5.0.1
requests==2.31.0
upstash-redis==1.0.4
uvicorn[standard]==0.38.0
```

## Step 4: Create a Redis Cache Manager

Create a new file `app/cache_manager.py`:

```python
import redis
from typing import Any, Optional, Union
import json
import os
from urllib.parse import urlparse

class UpstashRedisCacheManager:
    def __init__(self):
        # Use the Upstash Redis REST API URL from environment variable
        redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
        if not redis_url:
            raise ValueError("UPSTASH_REDIS_REST_URL environment variable is required")
        
        # Parse the URL to extract host and token
        parsed = urlparse(redis_url)
        token = parsed.password
        
        # Create Redis client with Upstash REST API
        self.client = redis.from_url(
            redis_url,
            username="default",
            password=token,
            decode_responses=True
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
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, max_pages: Optional[int], format_type: str, data: Any, ttl: int = 3600) -> None:
        """Set cached data with TTL"""
        key = self._generate_key(max_pages, format_type)
        try:
            self.client.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            print(f"Error setting cache key {key}: {e}")
    
    def delete(self, max_pages: Optional[int], format_type: str) -> bool:
        """Delete specific cache entry"""
        key = self._generate_key(max_pages, format_type)
        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            print(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear_all(self) -> int:
        """Clear all cache entries"""
        try:
            keys = self.client.keys("scrape:*")
            if keys:
                result = self.client.delete(*keys)
                return result
            return 0
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return 0
    
    def cache_info(self) -> dict:
        """Get cache statistics"""
        try:
            info = self.client.info()
            db_size = self.client.dbsize()
            return {
                "connected": True,
                "db_size": db_size,
                "used_memory": info.get("used_memory_human", "N/A"),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            print(f"Error getting cache info: {e}")
            return {"connected": False, "error": str(e)}

# Create global cache manager instance
cache_manager = UpstashRedisCacheManager()
```

## Step 5: Update your scraper.py file

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

## Step 6: Update main.py to use caching

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

## Step 7: Add Cache Management Endpoints

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

## Step 8: Docker Configuration

Update your Dockerfile to include environment variables:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables for Upstash Redis
ENV UPSTASH_REDIS_REST_URL=https://your-redis-url-comes-here.upstash.io

EXPOSE 8021

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8021"]
```

Update your docker-compose.yml:

```yaml
version: '3.8'

services:
  jsi-scraper:
    build: .
    ports:
      - "8021:8021"
    environment:
      - UPSTASH_REDIS_REST_URL=${UPSTASH_REDIS_REST_URL}
      - UPSTASH_REDIS_REST_TOKEN=${UPSTASH_REDIS_REST_TOKEN}
    volumes:
      - /tmp/jsi_scraper_data:/tmp
    restart: unless-stopped
```

Create a `.env` file:

```env
UPSTASH_REDIS_REST_URL=https://your-upstash-url-goes-here.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-upstash-token-goes-here
```

## Step 9: Running with Docker

1. Create the `.env` file with your Upstash credentials
2. Build and run with Docker:

```bash
docker-compose up -d
```

## Step 10: Testing

1. Make a request to `/scrape/json` - this will take the full scraping time
2. Make another request to `/scrape/json` with the same parameters - this should return instantly from cache
3. Check cache status at `/cache/status`
4. Clear cache if needed at `/cache/clear`

This implementation provides fast caching with Upstash Redis while maintaining the functionality of your existing scraper.