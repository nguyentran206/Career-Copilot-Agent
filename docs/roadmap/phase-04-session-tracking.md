# Phase 04 - Session Tracking MVP

## Mục tiêu

Thêm basic in-memory session tracking để frontend có thể theo dõi trạng thái analysis.

Phase này chuẩn bị nền cho workflow AI lâu hơn khi thêm Gemini/LangGraph.

## API đề xuất

### Start analysis

```text
POST /api/v1/analyze
```

Response:

```json
{
  "session_id": "string",
  "status": "processing"
}
```

### Get session result

```text
GET /api/v1/session/{session_id}
```

Processing:

```json
{
  "session_id": "string",
  "status": "processing",
  "result": null,
  "error": null
}
```

Completed:

```json
{
  "session_id": "string",
  "status": "completed",
  "result": {},
  "error": null
}
```

Failed:

```json
{
  "session_id": "string",
  "status": "failed",
  "result": null,
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "Unable to complete analysis."
  }
}
```

## Công việc chính

### 1. Thiết kế session store tạm

Dùng in-memory dictionary cho MVP:

```text
session_id → status/result/error/created_at/updated_at
```

Chưa cần Supabase ở phase này.

### 2. Chạy analysis background

Với FastAPI MVP có thể dùng `BackgroundTasks`.

Lưu ý:

- BackgroundTasks đủ cho demo local.
- Không phải job queue production.
- Khi service restart, session mất.

### 3. Thêm trạng thái rõ ràng

Status nên giới hạn:

- `processing`
- `completed`
- `failed`

Nếu muốn debug tốt hơn, có thể thêm internal stage:

- `parsing_cv`
- `analyzing`
- `generating_result`

### 4. Test session flow

Cần test:

- Create session.
- Get processing/completed session.
- Unknown session returns 404.
- Failed session stores error.

## Tiêu chí hoàn thành

- Frontend có thể start analysis và poll result.
- Session contract khớp `API_DRAFT.md`.
- In-memory limitation được document rõ.
