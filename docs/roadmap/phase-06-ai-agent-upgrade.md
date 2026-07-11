# Phase 06 - Scoring Intelligence and AI Agent Upgrade

## Mục tiêu

Nâng cấp Agent Service từ deterministic baseline sang scoring intelligence tốt hơn và AI workflow có LangGraph, Gemini, embedding-based skill matching, và O*NET occupational prior.

Phase này chỉ nên bắt đầu sau khi deterministic backend E2E đã ổn.

O*NET trong phase này chỉ đóng vai trò nguồn bổ sung ngữ cảnh nghề nghiệp. O*NET không được thay thế JD.

## Nguyên tắc JD-first

Thứ tự ưu tiên khi tính trọng số skill:

1. Yêu cầu được viết trực tiếp trong JD.
2. Phân loại `required`, `preferred`, hoặc `unknown` trong JD.
3. Mức độ liên quan của skill với occupation theo O*NET.
4. Bằng chứng skill, experience, và project trong CV.

JD luôn là nguồn thông tin chính. O*NET chỉ là occupational prior để điều chỉnh trọng số khi JD không đủ rõ.

## Công việc chính

### 1. Thiết kế LangGraph state

State nên chứa:

- `cv_text`
- `jd_text`
- `parsed_cv`
- `parsed_jd`
- `occupation_context`
- `skill_matches`
- `skill_weight_sources`
- `score_breakdown`
- `fit_score`
- `fit_level`
- `cv_improvement_suggestions`
- `cover_letter`
- `learning_roadmap`
- `errors`

### 2. Thiết kế O*NET occupational prior

Mục tiêu của O*NET:

- Bổ sung occupational context khi JD không phân loại rõ skill nào là required/preferred.
- Điều chỉnh trọng số skill theo occupation, ví dụ SQL quan trọng hơn Power BI với một số role.
- Giúp giải thích vì sao skill có trọng số cao/thấp.

Không dùng O*NET để:

- Override yêu cầu explicit trong JD.
- Tự biến một skill không xuất hiện trong JD thành `missing_skill` chính.
- Thay thế phân tích JD.

Output khuyến nghị:

```json
{
  "occupation_context": {
    "occupation_title": "Data Scientist",
    "onet_soc_code": "15-2051.00",
    "confidence": 0.82,
    "source": "jd_text"
  },
  "skill_weight_sources": [
    {
      "skill": "SQL",
      "jd_classification": "required",
      "onet_prior": "high",
      "cv_evidence": "strong",
      "final_weight": 0.95
    }
  ]
}
```

### 3. JD-first weighting rule

JD classification nên tạo base weight:

| JD Classification | Base Weight |
|---|---:|
| `required` | 1.0 |
| `preferred` | 0.65 |
| `unknown` | 0.45 |

O*NET chỉ điều chỉnh trong biên độ có kiểm soát, đặc biệt với `unknown`.

Ví dụ:

```text
final_skill_weight = jd_base_weight + onet_adjustment
```

Guardrails:

- Skill `required` trong JD không bị O*NET hạ trọng số.
- Skill `preferred` trong JD không bị O*NET đẩy cao hơn skill `required`.
- Skill không xuất hiện trong JD không nên được tính là missing skill chính chỉ vì O*NET nói nó phổ biến.
- Nếu cần gợi ý skill nghề nghiệp từ O*NET nhưng JD không nhắc tới, trả ở field riêng như `occupation_relevant_suggestions`.

### 4. Tạo nodes

MVP nodes:

- `detect_occupation_node`
- `load_onet_context_node`
- `parse_cv_node`
- `parse_jd_node`
- `classify_jd_skill_priority_node`
- `match_skills_node`
- `calculate_skill_weights_node`
- `calculate_fit_score_node`
- `evaluate_fit_level_node`
- `suggest_improvements_node`
- `generate_cover_letter_node`
- `generate_roadmap_node`

### 5. Gemini structured output

Gemini nên dùng để:

- Parse CV thành structured data.
- Parse JD thành structured requirements.
- Detect likely occupation from JD when deterministic matching is not enough.
- Generate suggestions.
- Generate cover letter.
- Generate learning roadmap.

Output cần validate bằng Pydantic schema. Không tin raw model output.

### 6. Embedding-based matching

Skill matching nên hỗ trợ:

- Exact match.
- Synonym/semantic match.
- Similarity score.
- Match level: `strong`, `partial`, `missing`.

Ví dụ:

- `PostgreSQL` gần với `SQL`.
- `REST API` gần với `API development`.
- `LangGraph` gần với `agent workflow`.

### 7. Fallback strategy

Nếu Gemini lỗi:

- Trả error có code rõ.
- Hoặc fallback về deterministic baseline nếu phù hợp.

Nếu O*NET occupation lookup lỗi hoặc không đủ confidence:

- Vẫn dùng JD-only scoring.
- Ghi rõ `occupation_context = null` hoặc `source = unavailable`.
- Không fail toàn bộ analysis chỉ vì thiếu O*NET.

### 8. Cost và latency guardrails

Cần có:

- Max input length.
- Timeout.
- Retry giới hạn.
- Logging request stage.
- Không log full CV/JD nếu chứa dữ liệu cá nhân.

### 9. Tests cần có

- JD required skill không bị O*NET hạ trọng số.
- JD preferred skill không vượt required skill chỉ vì O*NET prior cao.
- Unknown JD skill được O*NET điều chỉnh hợp lý.
- Không thêm O*NET-only skill vào `missing_skills` chính.
- Fallback về JD-only scoring khi không detect được occupation.
- O*NET context xuất hiện trong explainability fields khi available.
- Gemini output được mock để tests không phụ thuộc API thật.

## Tiêu chí hoàn thành

- Agent workflow có LangGraph state/nodes rõ.
- O*NET chỉ hoạt động như occupational prior, không thay thế JD.
- Skill weight có explainability theo JD classification, O*NET prior, và CV evidence.
- Gemini output được validate.
- Embedding matching tốt hơn exact match.
- Deterministic tests vẫn tồn tại cho baseline/scoring.
- Có tests mock Gemini để không phụ thuộc API thật.
