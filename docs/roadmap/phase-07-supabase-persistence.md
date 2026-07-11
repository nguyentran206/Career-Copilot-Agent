# Phase 07 - Supabase Persistence

## Mục tiêu

Thêm persistence cho analysis sessions, uploaded file metadata và results.

Phase này không bắt buộc cho MVP demo đầu tiên, nhưng cần cho history, reliability và production.

## Công việc chính

### 1. Thiết kế database schema

Bảng đề xuất:

```text
analysis_sessions
```

Fields:

- `id`
- `status`
- `cv_filename`
- `cv_file_size_bytes`
- `cv_text_length`
- `jd_text_length`
- `result_json`
- `error_json`
- `created_at`
- `updated_at`

Nếu có auth sau này:

- `user_id`

### 2. Storage cho uploaded CV

Supabase Storage có thể lưu CV PDF nếu cần.

Với MVP có thể chỉ lưu metadata và result, chưa lưu file để giảm rủi ro dữ liệu cá nhân.

### 3. Repository layer

Không gọi Supabase trực tiếp trong route.

Nên có layer:

- `create_session`
- `update_session_status`
- `save_result`
- `get_session`

### 4. Privacy guardrails

CV/JD là dữ liệu cá nhân. Cần quyết định:

- Có lưu raw `cv_text` không?
- Có lưu raw `jd_text` không?
- Retention bao lâu?
- Có cần masking logs không?

Khuyến nghị ban đầu:

- Không log raw CV/JD.
- Không lưu raw text nếu chưa cần history.
- Lưu result JSON và metadata trước.

## Tiêu chí hoàn thành

- Session/result không mất khi service restart.
- API session endpoint đọc được từ DB.
- Có migration/schema document.
- Không log hoặc expose dữ liệu nhạy cảm không cần thiết.
