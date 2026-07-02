# Changelog

## 2026-06-18

### Added
- Initialized project planning documents
- Defined MVP scope
- Drafted system architecture
- Drafted initial API contract


## 2026-06-19

### Added
- Initialized FastAPI backend structure
- Added `/health` endpoint
- Added backend environment variable template
- Added initial `.gitignore`

### Changed
- Updated project structure for backend development

## 2026-06-20

### Added
- Defined microservice-based backend architecture
- Designed initial `api-gateway` folder structure
- Planned API Gateway responsibilities
- Planned API Gateway health check endpoint

### Changed
- Updated main flow in ARCHITECTURE_DRAFT.md
- Updated backend architecture direction from single FastAPI app to microservices
- Decided to implement `api-gateway` before other backend services

## 2026-07-02

### Added

* Added `document-parser-service` foundation
* Added `document-parser-service` health check endpoint
* Added `POST /api/v1/parse-document` endpoint for extracting text from uploaded PDF documents
* Added initial PDF text extraction using PyMuPDF
* Added Document Parser API contract documentation
* Added Document Parser environment variable template
* Added Document Parser local development instructions
* Added API Gateway environment variables documentation
* Added internal service URL configuration for future service-to-service communication

### Changed

* Updated API Gateway environment configuration to align `.env`, `.env.example`, and `config.py`
* Updated API Gateway README with environment variables
* Standardized API route module naming with `routes.py`
* Updated Document Parser README to clarify current MVP usage and future JD PDF support
* Clarified that JD is currently expected as plain text in the MVP analysis flow

### Fixed

* Fixed API Gateway route import alignment from `router.py` to `routes.py`
* Removed unnecessary MVP reference to authentication service configuration
* Renamed parser service configuration from `DOCS_PARSER_SERVICE_URL` to `DOCUMENT_PARSER_SERVICE_URL`
* Clarified API Gateway and Document Parser service ports
