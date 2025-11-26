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
