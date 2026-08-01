# Phase 03 - API Gateway to Agent Service Integration

> Tài liệu này ghi lại phạm vi lịch sử của Phase 03. Contract hiện tại đã mở rộng ở Phase 06: public API nhận CV PDF và chính xác một nguồn JD (`jd_text` hoặc `jd_file`); nếu dùng `jd_file`, Gateway gửi cả JD PDF qua Document Parser trước khi gọi Agent Service.

## Mục tiêu

Tạo backend end-to-end flow đầu tiên:

```text
API Gateway
→ Document Parser Service
→ Agent Service
→ API Gateway response
```

Đây là phase biến project từ parser demo thành analysis backend thật.

## Công việc chính

### 1. Thêm Agent Service client trong API Gateway

API Gateway cần gọi:

```text
POST {AGENT_SERVICE_URL}/api/v1/analyze
```

Payload:

```json
{
  "cv_text": "extracted text from parser",
  "jd_text": "normalized JD text"
}
```

### 2. Cập nhật response của public `/api/v1/analyze`

Có hai hướng:

#### Option A: Synchronous response cho MVP nhanh

Gateway trả thẳng Agent result:

```json
{
  "status": "completed",
  "result": {
    "fit_score": 78,
    "fit_level": "medium"
  },
  "cv_parse_result": {}
}
```

Ưu điểm: dễ làm frontend, dễ demo.

Nhược điểm: request có thể lâu khi dùng Gemini thật.

#### Option B: Session-based response

Gateway trả:

```json
{
  "session_id": "string",
  "status": "processing"
}
```

Frontend poll `/api/v1/session/{session_id}`.

Ưu điểm: hợp với AI workflow lâu.

Nhược điểm: cần session tracking ngay.

Khuyến nghị: làm Option A trước nếu mục tiêu là MVP demo nhanh, sau đó chuyển Phase 04 sang session.

### 3. Chuẩn hóa lỗi service-to-service

Cần error code riêng:

- `DOCUMENT_PARSER_UNAVAILABLE`
- `DOCUMENT_PARSER_ERROR`
- `AGENT_SERVICE_UNAVAILABLE`
- `AGENT_ANALYSIS_ERROR`
- `UPSTREAM_INVALID_RESPONSE`

### 4. Thêm integration tests

Test nên cover:

- Gateway analyze success với Parser + Agent mocked at HTTP/client boundary.
- Parser success nhưng Agent unavailable.
- Parser returns warning scanned PDF.
- Agent returns invalid schema.
- JD text normalization được gửi sang Agent.

## Tiêu chí hoàn thành

- Public `/api/v1/analyze` trả được result phân tích từ Agent Service.
- Không còn chỉ trả parser preview.
- Gateway validate được response từ cả Document Parser và Agent Service.
- Test cover lỗi của từng upstream service.

## Trạng thái triển khai

Phase này tập trung vào synchronous backend E2E flow:

- API Gateway gọi Document Parser Service để extract CV text.
- API Gateway gọi Agent Service với `cv_text` và normalized `jd_text`.
- Public `/api/v1/analyze` trả `status = completed` kèm `analysis_result`.
- Gateway xử lý CV text quá ngắn trước khi phân tích.
- Gateway chuẩn hóa lỗi Agent Service unavailable, Agent Service error, và invalid Agent response.
- Session tracking vẫn để Phase 04.
