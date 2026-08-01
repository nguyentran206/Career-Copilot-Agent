# Phase 05 - Frontend MVP

## Trạng thái

Implemented as a frontend MVP in `frontend/web`.

The app uses Next.js TypeScript App Router, calls only API Gateway, starts analysis through `POST /api/v1/analyze`, polls `GET /api/v1/session/{session_id}`, and renders completed results or friendly errors.

## Mục tiêu

Xây frontend Next.js tối giản để user upload CV PDF, chọn nhập JD text hoặc upload JD PDF, và xem kết quả analysis.

Frontend ở phase này nên tập trung vào usability cơ bản, chưa cần dashboard/history/auth.

## Màn hình cần có

### 1. Analyze form

Input:

- CV PDF upload.
- Chọn chính xác một nguồn JD:
  - JD text textarea.
  - JD PDF upload.
- Submit button.

Validation client-side:

- CV required.
- Chỉ nhận `.pdf`.
- Phải cung cấp JD text hoặc JD PDF, không gửi đồng thời cả hai.
- Với JD text: không rỗng và đủ độ dài tối thiểu.
- Với JD PDF: bắt buộc chọn file `.pdf` khi đang ở chế độ upload.
- PDF nên có text layer vì OCR chưa nằm trong MVP.

API Gateway tiếp tục kiểm tra metadata, file rỗng và giới hạn dung lượng cho cả CV/JD trước khi tạo session.

### 2. Loading state

Nếu API còn synchronous:

- Hiển thị spinner/loading message.

Nếu đã có session:

- Poll `/api/v1/session/{session_id}`.
- Hiển thị trạng thái `processing`.

### 3. Result page/section

Hiển thị:

- Fit score.
- Fit level.
- Matched skills.
- Missing skills.
- CV improvement suggestions.
- Cover letter nếu có.
- Learning roadmap nếu có.
- Parser warning nếu CV có vấn đề extract text.

### 4. Error state

Hiển thị lỗi dễ hiểu cho:

- File quá lớn.
- Không phải PDF.
- CV hoặc JD PDF scanned/ít text.
- Thiếu nguồn JD hoặc gửi đồng thời JD text và JD PDF.
- Parser service unavailable.
- Agent service unavailable.
- Analysis failed.

## Công việc chính

### 1. Tạo Next.js app

Đặt ở:

```text
frontend/web
```

### 2. Cấu hình env frontend

Ví dụ:

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Tạo API client

Client gửi `multipart/form-data` tới API Gateway.

### 4. Tạo component kết quả

Nên tách:

- `AnalyzeForm`
- `AnalysisResult`
- `SkillList`
- `ConditionalRecommendation`
- `ErrorMessage`

## Tiêu chí hoàn thành

- User có thể chạy toàn bộ flow từ UI.
- User có thể chuyển giữa JD text và JD PDF; frontend chỉ gửi nguồn JD đang được chọn.
- Error hiển thị rõ, không chỉ raw JSON.
- Frontend không gọi trực tiếp Document Parser hoặc Agent Service.
- Chỉ gọi API Gateway.
