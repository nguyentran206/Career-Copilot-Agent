# Phase 05 - Frontend MVP

## Mục tiêu

Xây frontend Next.js tối giản để user upload CV PDF, nhập JD text và xem kết quả analysis.

Frontend ở phase này nên tập trung vào usability cơ bản, chưa cần dashboard/history/auth.

## Màn hình cần có

### 1. Analyze form

Input:

- CV PDF upload.
- JD text textarea.
- Submit button.

Validation client-side:

- CV required.
- Chỉ nhận `.pdf`.
- JD text không rỗng.
- JD text đủ độ dài tối thiểu.

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
- PDF scanned/ít text.
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
- Error hiển thị rõ, không chỉ raw JSON.
- Frontend không gọi trực tiếp Document Parser hoặc Agent Service.
- Chỉ gọi API Gateway.
