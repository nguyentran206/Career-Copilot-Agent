# Phase 08 - Deployment and Production Hardening

## Mục tiêu

Chuẩn bị project để deploy demo/public một cách an toàn hơn.

Phase này nên làm sau khi flow chính đã ổn.

## Công việc chính

### 1. Deployment target

Theo architecture draft:

- Frontend: Vercel.
- Backend services: AWS.
- Database/storage: Supabase.

Cần quyết định cụ thể backend sẽ chạy bằng:

- ECS/Fargate.
- EC2.
- App Runner.
- Lambda container.

### 2. Environment management

Tách env:

- local
- staging
- production

Không commit `.env` thật.

Mỗi service cần `.env.example` đầy đủ.

### 3. CORS và service exposure

Public:

- API Gateway.

Internal-only:

- Document Parser Service.
- Agent Service.

Không expose internal service trực tiếp ra frontend.

### 4. Observability

Cần có:

- Structured logs.
- Request ID/correlation ID.
- Error code thống nhất.
- Latency logs cho Parser và Agent.
- Basic health checks.

### 5. Security hardening

Cần kiểm tra:

- File size limit.
- Content type validation.
- Timeout service-to-service.
- Không log raw CV/JD.
- Rate limiting public endpoint.
- Secrets không nằm trong repo.

### 6. CI/CD

Tối thiểu:

- Run tests cho từng service.
- Lint/format nếu có.
- Build frontend.
- Check env examples.

## Tiêu chí hoàn thành

- Có staging hoặc production demo URL.
- Public chỉ truy cập API Gateway/frontend.
- Internal services không bị expose bừa.
- Logs đủ debug nhưng không lộ dữ liệu nhạy cảm.
- CI chạy test trước khi merge/deploy.
