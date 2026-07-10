# Career Copilot Agent - Roadmap

Tài liệu này mô tả các phase tiếp theo để đưa Career Copilot Agent từ backend foundation hiện tại tới MVP end-to-end.

## Trạng thái hiện tại

Project hiện đã có nền backend microservices:

- `api-gateway`: nhận CV PDF và JD text, validate input, gọi Document Parser Service, trả response parser-based tạm thời.
- `document-parser-service`: validate PDF, extract raw text bằng PyMuPDF, trả metadata và warning cho PDF ít text/scanned.
- `agent-service`: đã có skeleton FastAPI và deterministic rule-based analyzer, nhưng chưa được API Gateway tích hợp và chưa dùng LangGraph/Gemini/embedding.

Frontend, session tracking, persistence, deployment production và AI workflow thật vẫn chưa hoàn thiện.

## Nguyên tắc triển khai các phase tiếp theo

- Mỗi phase nên tạo ra một lát cắt chạy được, test được.
- Không đưa Supabase/deployment/frontend nâng cao vào trước khi backend analysis contract ổn định.
- Agent output contract cần được chốt trước khi frontend render result.
- Deterministic rule-based logic nên được dùng làm baseline trước, sau đó mới thay dần bằng Gemini/LangGraph/embedding.

## Danh sách phase đề xuất

| Phase | Mục tiêu | File chi tiết |
|---|---|---|
| Phase 01 | Stabilize backend foundation và đồng bộ docs/env/tests | [Phase 01](phase-01-foundation-stabilization.md) |
| Phase 02 | Hoàn thiện Agent Service deterministic core | [Phase 02](phase-02-agent-service-core.md) |
| Phase 03 | Tích hợp API Gateway với Agent Service để có backend E2E flow | [Phase 03](phase-03-gateway-agent-integration.md) |
| Phase 04 | Thêm session tracking MVP | [Phase 04](phase-04-session-tracking.md) |
| Phase 05 | Xây frontend MVP | [Phase 05](phase-05-frontend-mvp.md) |
| Phase 06 | Nâng cấp Agent bằng LangGraph, Gemini và embedding matching | [Phase 06](phase-06-ai-agent-upgrade.md) |
| Phase 07 | Thêm Supabase persistence và storage | [Phase 07](phase-07-supabase-persistence.md) |
| Phase 08 | Chuẩn bị deployment, observability và production hardening | [Phase 08](phase-08-deployment-hardening.md) |

## Thứ tự ưu tiên khuyến nghị

Ưu tiên gần nhất:

1. Phase 01: sửa các điểm foundation còn lệch nhau.
2. Phase 02: chốt Agent Service contract và scoring baseline.
3. Phase 03: nối API Gateway với Agent Service để có backend E2E.

Sau khi backend E2E ổn định, mới nên làm frontend MVP và AI upgrade.

## Definition of MVP Done

MVP được xem là xong khi flow sau chạy được:

```text
User upload CV PDF + nhập JD text
→ Frontend gọi API Gateway
→ API Gateway gọi Document Parser Service
→ API Gateway gửi cv_text + jd_text sang Agent Service
→ Agent Service trả fit_score, fit_level, matched/missing skills, suggestions, conditional output
→ Frontend hiển thị kết quả rõ ràng
```

Persistence, auth, payment, dashboard history và production-grade infrastructure không bắt buộc cho MVP đầu tiên.
