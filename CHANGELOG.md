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

## 2026-07-03

### Added

* Added `IMPLEMENTATION_STATUS.md` to track current MVP implementation progress separately from MVP scope and changelog.
* Added upload validation for `document-parser-service`, including file type, content type, empty file, and file size checks.
* Added PDF parsing error handling for invalid or unsupported PDF inputs.
* Added basic tests for `document-parser-service`.
* Added test coverage for health check and document parsing validation cases.
* Added `pytest.ini` for stable test discovery and import path configuration.
* Added Document Parser error response documentation.

### Changed

* Refined project documentation structure to improve Single Source of Truth.
* Updated `README.md` to focus on project overview, documentation links, tech stack, backend services summary, and local development.
* Updated `MVP_SCOPE.md` to focus on MVP goal, input/output, scope, out-of-scope items, decision rules, and success criteria.
* Updated `ARCHITECTURE_DRAFT.md` to focus on backend services, technical flow, and LangGraph workflow nodes.
* Updated `API_DRAFT.md` to clarify API response rules for conditional result fields.
* Clarified that Supabase result persistence is planned for a future phase, not the initial MVP.
* Clarified that API Gateway is responsible for coordinating calls between frontend and internal services.
* Updated `document-parser-service` response schema to use `Field(default_factory=list)` for warnings.
* Standardized parser output to include filename, document type, content type, file size, page count, extracted text, text length, and warnings.

### Fixed

* Moved implementation progress tracking out of `MVP_SCOPE.md` to avoid mixing scope definition with current development status.
* Separated initial LangGraph workflow nodes from future workflow nodes.
* Fixed test import issues by configuring pytest path discovery.
* Fixed mutable default list usage in parser response warnings.

