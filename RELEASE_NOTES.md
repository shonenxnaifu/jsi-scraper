# JSI Scraper v1.1.3 - Docker Compose Deployment & Enhanced Deployment Process

## 🚀 Feature Enhancements
- **Docker Compose Support**: Added docker-compose.yml for easier deployment and container orchestration
  - Standardized deployment with memory limits (256m/512m)
  - Health checks for service monitoring
  - Restart policies for improved reliability
- **GitHub Actions Enhancement**: New workflow using Docker Compose for deployment
  - SCP action for secure copy of docker-compose.yml to server
  - Docker Compose v2 commands for better compatibility
  - Container recreation with --force-recreate flag
  - Automatic cleanup of unused Docker images
- **Deployment Directory Structure**: Organized deployment with /opt/apps-container/jsi-scraper directory
  - Dedicated directory for application deployment files
  - Proper file permissions and organization

# JSI Scraper v1.1.2 - Concurrency Control & Enhanced Locking

## 🚀 Feature Enhancements
- **Concurrent Scraping Prevention**: Added blocking mechanism to prevent multiple simultaneous scraping requests
  - All scraping endpoints (`/scrape/json`, `/scrape/csv`) now block when another scraping process is in progress
  - Returns HTTP 423 Locked status with descriptive message when scraping is in progress
- **Scraping Status API**: New endpoint `/scrape/status` to check current scraping status
  - Returns status ("IDLE", "IN PROGRESS", "FINISHED"), message, progress percentage, and total projects
  - Available even when scraping is in progress (not blocked)
- **Progress Tracking**: Real-time progress updates during scraping operations
- **Optimized File Locking**: Improved file-based locking mechanism for better cross-worker coordination
  - Separate lock file for atomic operations and state file for status information
  - Significantly reduced lock duration to improve responsiveness
  - Cross-platform compatibility with graceful fallback for systems without `fcntl`

## 🐞 Bug Fixes
- Fixed race condition issues in multi-worker environments
- Resolved "FCNTL_AVAILABLE is not defined" error on systems without fcntl support
- Improved file handling with proper JSON error handling for corrupted files
- Enhanced atomic operations to prevent deadlocks during long-running scraping

## 🔧 Technical Improvements
- **Concurrency Control**: Robust mechanism to handle multiple workers in gunicorn deployments
- **Optimized Locking**: Reduced lock contention by separating critical operations from status updates
- **Cross-Platform Support**: Works on Linux, macOS, and other Unix-like systems with graceful degradation
- **Gunicorn Compatibility**: Proper handling of multiple worker processes with file-based coordination

# JSI Scraper v1.0.2 - Enhanced CSV Export

## 🐞 Bug Fixes
- Fixed and Enhanced CSV export with improved discography formatting
  - Multiline display of discography items within single cells
  - New format: `tahun :: judul :: jenis :: format :: pranala_terkait`
  - Clear column header: `diskografi (tahun :: judul :: jenis :: format :: pranala_terkait)`

# JSI Scraper v1.0.1 - Bug Fix

## 🐞 Bug Fixes
- Fixed data extraction from "Pranala" and "Pranala Terkait" sections
- Deleted unused files

# JSI Scraper v1.0.0 - Initial Release

## 🚀 What's New

### Core Features
- **Web Scraping Engine**: Advanced scraping capabilities specifically designed for jogjasonicindex.com
- **FastAPI Integration**: RESTful API with two endpoints for data export
  - `/scrape/json` - Retrieve data in JSON format
  - `/scrape/csv` - Download data as CSV file
- **Production-Ready Architecture**: Built with Gunicorn and optimized for production deployments

### Technical Improvements
- **Enhanced Performance**:
  - Async processing to prevent blocking operations
  - Thread pool executor for long-running tasks
  - Optimized timeout handling to prevent 504 Gateway Timeout errors
- **Robust Error Handling**:
  - Request timeout protection with retry mechanism
  - Exponential backoff algorithm
  - Graceful error responses
- **API Documentation**: Interactive Swagger UI available at `/docs`

### Deployment Options
- **Docker Support**: Production-ready Docker configuration with multi-stage setup
- **Traditional Deployment**: Direct Python/uvicorn deployment capability

## 🔧 How to Install & Run

### Option 1: Direct Python Installation
```bash
# Clone the repository
git clone git@github.com:shonenxnaifu/jsi-scraper.git
cd jsi-scraper

# Install dependencies
pip install -r requirements.txt

# Start the API server
cd app && uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 2: Docker Deployment
```bash
# Build the Docker image
docker build -t jsi-scraper .

# Run the container
docker run -p 8000:8000 jsi-scraper
```

## 📋 Requirements

- Python 3.10+
- Docker (if using containerized deployment)
- Internet access to jogjasonicindex.com

## 🛡️ Important Notes

- Always respect [jogjasonicindex.com](https://jogjasonicindex.com/)'s `robots.txt` file
- Be mindful of rate limiting to avoid being blocked
- Check jogjasonicindex.com's terms of service before scraping
- This scraper is specifically designed for jogjasonicindex.com

## 📈 Usage Recommendations

1. **Limit Scraping Scope**: Always specify `max_pages` parameter to prevent long-running operations
2. **Monitor Progress**: Check server logs during operation to track scraping progress
3. **Implement Caching**: For repeated requests, consider implementing caching to reduce server load
4. **Consider Background Jobs**: For extensive scraping, implement background job queue for better user experience

## 🔄 Upgrade Path

To upgrade from previous versions (if applicable):
1. Pull the latest code from the repository
2. Update dependencies: `pip install -r requirements.txt`
3. Restart the application service

## 📄 License

This project is licensed under the terms specified in the repository.

## 🤝 Contributing

We welcome contributions! Please see the repository for contribution guidelines.

---
*For API documentation and testing, visit `http://localhost:8000/docs` after starting the server.*
