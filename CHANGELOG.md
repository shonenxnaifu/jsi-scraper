# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.3] - 2025-12-05

### Added
- New endpoints `/scrape/json/range` and `/scrape/csv/range` to support page range scraping
- Added `page_from` and `page_to` parameters for precise page range control
- Input validation for page range parameters
- Error handling for range validation failures
- Updated API documentation with new endpoints

### Changed
- Enhanced scraper module with `scrape_page_range` function
- Maintained backward compatibility for existing `max_pages` parameter
- Improved error response messages for validation failures

## [1.1.3] - 2025-12-02

### Added
- Docker Compose Support: Added docker-compose.yml for easier deployment and container orchestration
  - Standardized deployment with memory limits (256m/512m)
  - Health checks for service monitoring
  - Restart policies for improved reliability
- GitHub Actions Enhancement: New workflow using Docker Compose for deployment
  - SCP action for secure copy of docker-compose.yml to server
  - Docker Compose v2 commands for better compatibility
  - Container recreation with --force-recreate flag
  - Automatic cleanup of unused Docker images
- Deployment Directory Structure: Organized deployment with /opt/apps-container/jsi-scraper directory
  - Dedicated directory for application deployment files
  - Proper file permissions and organization

## [1.1.2] - 2025-12-01

### Added
- Concurrent Scraping Prevention: Added blocking mechanism to prevent multiple simultaneous scraping requests
  - All scraping endpoints (`/scrape/json`, `/scrape/csv`) now block when another scraping process is in progress
  - Returns HTTP 423 Locked status with descriptive message when scraping is in progress
- Scraping Status API: New endpoint `/scrape/status` to check current scraping status
  - Returns status ("IDLE", "IN PROGRESS", "FINISHED"), message, progress percentage, and total projects
  - Available even when scraping is in progress (not blocked)
- Progress Tracking: Real-time progress updates during scraping operations
- Optimized File Locking: Improved file-based locking mechanism for better cross-worker coordination
  - Separate lock file for atomic operations and state file for status information
  - Significantly reduced lock duration to improve responsiveness
  - Cross-platform compatibility with graceful fallback for systems without `fcntl`

### Fixed
- Fixed race condition issues in multi-worker environments
- Resolved "FCNTL_AVAILABLE is not defined" error on systems without fcntl support
- Improved file handling with proper JSON error handling for corrupted files
- Enhanced atomic operations to prevent deadlocks during long-running scraping

### Changed
- Concurrency Control: Robust mechanism to handle multiple workers in gunicorn deployments
- Optimized Locking: Reduced lock contention by separating critical operations from status updates
- Cross-Platform Support: Works on Linux, macOS, and other Unix-like systems with graceful degradation
- Gunicorn Compatibility: Proper handling of multiple worker processes with file-based coordination

## [1.0.2] - 2025-11-27

### Fixed
- Fixed and Enhanced CSV export functionality with multiline discography format
  - New format: `diskografi (tahun :: judul :: jenis :: format :: pranala_terkait)`
  - Each discography item displayed on separate lines within the same cell
  - Improved readability of discography data in CSV exports

## [1.0.1] - 2025-11-26

### Fixed
- Fixed data extraction from "Pranala" and "Pranala Terkait" sections
  - Corrected scraping logic to properly extract links when "Pranala" is found in strong elements
  - Renamed `pranala` field to `pranala_terkait` in discography items for clarity
  - Added proper initialization of `pranala` field in project data

## [1.0.0] - 2025-11-25

### Added
- Initial release of JSI Scraper - a web scraping tool for jogjasonicindex.com
- Web scraping functionality with data extraction for project details
  - Project name (`nama_projek`)
  - Date posted (`date_posted`)
  - Author information (`author`)
  - Descriptions (`deskripsi`)
  - Format types (`format`)
  - Member information (`anggota`)
  - Genre classifications (`genre`)
  - Years (`tahun`)
  - Status information (`status`)
  - Links (`pranala`)
  - Tags (`tags`)
  - Media information (`media`)
  - Discography data (`diskografi`)
- FastAPI endpoints for data export:
  - `/scrape/json` endpoint returning structured JSON data
  - `/scrape/csv` endpoint for CSV file downloads
  - `/health` endpoint for service status checking
  - Interactive API documentation at `/docs`
- Docker support with production-ready Gunicorn configuration
- Async processing implementation using thread pools
- Timeout handling mechanisms to prevent 504 Gateway Timeout errors
- Comprehensive error handling with retry mechanisms
- Rate limiting to respect target server resources
- Structured logging for monitoring and debugging

### Changed
- Increased timeout values from default to prevent 504 Gateway Timeout errors
- Improved scraping efficiency with better error handling and recovery
- Enhanced request headers for better server compatibility
- Optimized inter-request delays while maintaining respectful scraping practices
- Added CI/CD workflows for automated testing and quality assurance
