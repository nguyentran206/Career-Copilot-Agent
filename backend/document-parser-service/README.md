# Document Parser Service

Microservice responsible for extracting raw text from uploaded CV/JD PDF files.

## Responsibilities

* Receive uploaded PDF documents
* Validate uploaded file type and size
* Extract raw text from PDF files
* Return extracted text and document metadata to API Gateway or Agent Service

## Current Endpoints

| Method | Endpoint                 | Description                             |
| ------ | ------------------------ | --------------------------------------- |
| GET    | `/api/v1/health`         | Check service health                    |
| POST   | `/api/v1/parse-document` | Extract text from uploaded PDF document |

## API Contract

### Parse Document

Extract text content from an uploaded PDF document.

```http
POST /api/v1/parse-document
```

### Request

Content type: `multipart/form-data`

| Field         | Type     | Required | Description                                      |
| ------------- | -------- | -------- | ------------------------------------------------ |
| file          | PDF file | Yes      | The document file to parse                       |
| document_type | string   | No       | Optional document type, for example `cv` or `jd` |

Current MVP usage:

* Parse CV PDF into raw text.
* JD is currently expected as plain text in the main analysis flow.
* JD PDF parsing may be supported in a future phase.

### Successful Response

```json
{
  "filename": "cv.pdf",
  "document_type": "cv",
  "content_type": "application/pdf",
  "file_size_bytes": 245321,
  "page_count": 2,
  "text": "Extracted CV text here...",
  "text_length": 5421,
  "warnings": []
}
```

### Response With Warning

If the PDF appears to be scanned or contains too little extractable text, the service returns a successful response with a warning.

```json
{
  "filename": "cv_scan.pdf",
  "document_type": "cv",
  "content_type": "application/pdf",
  "file_size_bytes": 512331,
  "page_count": 2,
  "text": "",
  "text_length": 0,
  "warnings": [
    "NO_TEXT_EXTRACTED_OR_SCANNED_PDF"
  ]
}
```

OCR is not included in the MVP. The service only detects low-text or scanned PDFs and returns a warning.

## Environment Variables

| Variable                  | Description                                  | Default                 |
| ------------------------- | -------------------------------------------- | ----------------------- |
| APP_NAME                  | Service name                                 | document-parser-service |
| APP_ENV                   | Environment                                  | development             |
| APP_VERSION               | App version                                  | 0.1.0                   |
| API_PREFIX                | API prefix                                   | /api/v1                 |
| HOST                      | Server host                                  | 127.0.0.1               |
| PORT                      | Server port                                  | 8001                    |
| ALLOWED_EXTENSIONS        | Supported file extensions                    | pdf                     |
| MAX_FILE_SIZE_MB          | Maximum upload file size in MB               | 5                       |
| MIN_EXTRACTED_TEXT_LENGTH | Minimum extracted text length before warning | 50                      |
| ENABLE_OCR                | Enable OCR parsing                           | false                   |
| LOG_LEVEL                 | Logging level                                | INFO                    |

## Local Development

### 1. Navigate to Document Parser Service

```bash
cd backend/document-parser-service
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 6. Run server

```bash
uvicorn app.main:app --reload --port 8001
```

### 7. Open Document Parser Service

Health check:

```txt
http://127.0.0.1:8001/api/v1/health
```

API documentation:

```txt
http://127.0.0.1:8001/docs
```

## Current MVP Limitations

* Only PDF files are supported.
* OCR is not implemented yet.
* Scanned PDFs may return empty or very short text with a warning.
* The service only extracts raw text and metadata.
* Structured CV/JD parsing, AI analysis, fit scoring, cover letter generation, and roadmap generation are handled by other services in future phases.
