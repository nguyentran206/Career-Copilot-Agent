# Phase 02 - Agent Service Deterministic Core

## Mục tiêu

Hoàn thiện Agent Service baseline trước khi dùng LangGraph/Gemini/embedding.

Baseline này nên chạy deterministic để dễ test, dễ debug và làm chuẩn so sánh cho AI workflow sau này.

## Công việc chính

### 1. Chốt API contract nội bộ

Endpoint:

```text
POST /api/v1/analyze
```

Input:

```json
{
  "cv_text": "string",
  "jd_text": "string"
}
```

Output cần ổn định:

```json
{
  "fit_score": 0,
  "fit_level": "low",
  "score_breakdown": {},
  "parsed_cv": {},
  "parsed_jd": {},
  "skill_matches": [],
  "matched_skills": [],
  "missing_skills": [],
  "cv_improvement_suggestions": [],
  "cover_letter": null,
  "learning_roadmap": []
}
```

### 2. Chốt scoring baseline

Scoring hiện có trọng số:

- Required skills: 45%
- Preferred skills: 20%
- Experience relevance: 15%
- Project/domain relevance: 10%
- Education/cert/tool: 10%

Cần quyết định:

- Các score chưa implement nên để `0`, `null`, hay tách trạng thái `not_evaluated`.
- Nếu để `0`, fit score sẽ bị kéo thấp dù required skills match tốt.
- Nếu phase này chỉ đánh required skills, có thể tạm normalize score theo phần đã implement.

Khuyến nghị cho MVP baseline:

- Giữ `score_breakdown` đầy đủ field.
- Thêm chú thích trong docs rằng một số component là placeholder.
- Hoặc đổi `calculate_fit_score` để chỉ tính trên các component đã enabled.

### 3. Mở rộng parser rule-based vừa đủ

Parser hiện dựa trên danh sách `COMMON_SKILLS`. Cần mở rộng vừa phải:

- Backend: Python, FastAPI, Django, Flask, REST API, PostgreSQL, Docker, AWS.
- Data: SQL, Excel, Power BI, Tableau, Pandas, NumPy, Statistics.
- AI/ML: Machine Learning, LLM, RAG, LangChain, LangGraph, Embedding.

Không nên cố parse CV hoàn hảo ở phase này.

### 4. Hoàn thiện conditional output

Theo MVP:

- `high`: cover letter, không cần roadmap.
- `medium`: suggestions + cover letter.
- `low`: suggestions + learning roadmap, không cần cover letter.

Đảm bảo các field không áp dụng trả `null` hoặc `[]` nhất quán theo API draft.

### 5. Test Agent Service

Cần thêm test cho:

- High fit.
- Medium fit.
- Low fit.
- Missing required skills.
- Empty/no known skills.
- Short text validation.
- Conditional output field consistency.

## Tiêu chí hoàn thành

- Agent Service chạy độc lập.
- Output schema ổn định.
- Scoring baseline có giải thích rõ.
- Tests cover đủ high/medium/low.
- Chưa cần LangGraph/Gemini.

## Trạng thái triển khai

Phase này tập trung vào deterministic baseline:

- Mở rộng rule-based skill extraction.
- Thêm related-skill matching ở mức deterministic.
- Dùng required-skill score làm `fit_score` baseline.
- Giữ các score breakdown chưa implement dưới dạng placeholder.
- Cover test cho high, medium, low, partial match, no known JD skills, và validation.
