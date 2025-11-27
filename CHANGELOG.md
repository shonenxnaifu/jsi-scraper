# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
