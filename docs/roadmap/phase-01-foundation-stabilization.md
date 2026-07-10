# Phase 01 - Foundation Stabilization

## Mục tiêu

Đảm bảo foundation hiện tại không có mâu thuẫn giữa code, docs, env và tests trước khi xây tiếp Agent flow.

Phase này không nhằm thêm feature lớn. Mục tiêu là làm nền sạch, chắc, dễ test.

## Công việc chính

### 1. Đồng bộ trạng thái Agent Service trong docs

`backend/agent-service` đã tồn tại với endpoint `/api/v1/health` và `/api/v1/analyze`.

Các docs cần mô tả thống nhất:

- Agent Service foundation đã có.
- Analyzer hiện là deterministic/rule-based baseline.
- Agent Service có thể test trực tiếp.
- Agent Service chưa tích hợp với API Gateway.
- Chưa có LangGraph, Gemini, embedding matching thật.

Trạng thái hiện tại:

- `README.md`, `IMPLEMENTATION_STATUS.md`, `ARCHITECTURE_DRAFT.md`, `API_DRAFT.md`, và service README nên cùng phản ánh trạng thái trên.

### 2. Sửa contract bug trong API Gateway parser response

`parse_cv_with_document_parser()` cần trả về `DocumentParserResponse`, không trả raw `dict`, vì route sử dụng object attribute như `parse_result.text`.

Trạng thái hiện tại:

- Response JSON đã được chuyển thành `DocumentParserResponse`.
- Việc xử lý graceful cho success response không hợp lệ hoặc non-JSON vẫn nên được bổ sung ở một bước hardening tiếp theo.

Kỳ vọng:

- Gateway không bị lỗi runtime khi gọi Document Parser Service thật.
- Test nên cover thêm invalid upstream success response hoặc schema validation failure.

### 3. Đồng bộ temporary analyze status

Chuẩn hiện tại:

```json
{
  "status": "parser_completed"
}
```

Lý do: tránh hiểu nhầm rằng full Agent analysis đã hoàn tất.

### 4. Đồng bộ env config

Key giữa `.env` và `.env.example` cần khớp ở từng service.

API Gateway cần document đủ config đang dùng trong code, bao gồm:

- `MAX_CV_FILE_SIZE_MB`

### 5. Khôi phục môi trường test local

Các `.venv` hiện trỏ tới Python WindowsApps path cũ nên test không chạy được trong môi trường hiện tại.

Cần tạo lại venv nếu gặp lỗi:

```powershell
Remove-Item -Recurse -Force .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Làm riêng cho từng service.

## Test cần chạy

Chạy riêng trong từng service:

```powershell
cd backend/api-gateway
.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q
```

```powershell
cd backend/document-parser-service
.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q
```

```powershell
cd backend/agent-service
.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q
```

## Tiêu chí hoàn thành

- Docs mô tả đúng trạng thái hiện tại.
- `.env.example` document đủ config đang dùng trong code.
- API Gateway gọi Document Parser Service thật không lỗi vì dict/object mismatch.
- Temporary analyze status nhất quán.
- Tests của 3 service chạy được trên môi trường local mới.
