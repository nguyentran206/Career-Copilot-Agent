# Phase 06 - AI Agent Upgrade

## Mục tiêu

Nâng cấp Agent Service từ deterministic baseline sang AI workflow có LangGraph, Gemini và embedding-based skill matching.

Phase này chỉ nên bắt đầu sau khi deterministic backend E2E đã ổn.

## Công việc chính

### 1. Thiết kế LangGraph state

State nên chứa:

- `cv_text`
- `jd_text`
- `parsed_cv`
- `parsed_jd`
- `skill_matches`
- `score_breakdown`
- `fit_score`
- `fit_level`
- `cv_improvement_suggestions`
- `cover_letter`
- `learning_roadmap`
- `errors`

### 2. Tạo nodes

MVP nodes:

- `parse_cv_node`
- `parse_jd_node`
- `match_skills_node`
- `calculate_fit_score_node`
- `evaluate_fit_level_node`
- `suggest_improvements_node`
- `generate_cover_letter_node`
- `generate_roadmap_node`

### 3. Gemini structured output

Gemini nên dùng để:

- Parse CV thành structured data.
- Parse JD thành structured requirements.
- Generate suggestions.
- Generate cover letter.
- Generate learning roadmap.

Output cần validate bằng Pydantic schema. Không tin raw model output.

### 4. Embedding-based matching

Skill matching nên hỗ trợ:

- Exact match.
- Synonym/semantic match.
- Similarity score.
- Match level: `strong`, `partial`, `missing`.

Ví dụ:

- `PostgreSQL` gần với `SQL`.
- `REST API` gần với `API development`.
- `LangGraph` gần với `agent workflow`.

### 5. Fallback strategy

Nếu Gemini lỗi:

- Trả error có code rõ.
- Hoặc fallback về deterministic baseline nếu phù hợp.

### 6. Cost và latency guardrails

Cần có:

- Max input length.
- Timeout.
- Retry giới hạn.
- Logging request stage.
- Không log full CV/JD nếu chứa dữ liệu cá nhân.

## Tiêu chí hoàn thành

- Agent workflow có LangGraph state/nodes rõ.
- Gemini output được validate.
- Embedding matching tốt hơn exact match.
- Deterministic tests vẫn tồn tại cho baseline/scoring.
- Có tests mock Gemini để không phụ thuộc API thật.
