# Backend (FastAPI + PostgreSQL + SQLAlchemy)

本目录实现了基于契约文档的后端系统，遵循：
- `service-contract.md`
- `error-convention.md`
- `frontend-service-mapping.md`

## 1. 目录结构与职责

```text
backend/
  app/
    main.py                    # FastAPI 启动入口、异常处理器注册
    api/
      router.py                # v1 路由汇总
      routes/                  # 各业务 REST Endpoint
    auth/
      deps.py                  # JWT Bearer Token 校验
    core/
      config.py                # 环境变量配置
      database.py              # SQLAlchemy Engine / SessionLocal / Base
    models/                    # ORM 模型
    repositories/              # 数据访问层
    services/                  # 业务实现（只编排业务，不直接访问底层SDK）
    schemas/                   # Pydantic 请求/响应模型
    errors/
      codes.py                 # 统一错误码枚举
      exceptions.py            # 业务异常模型
      handlers.py              # FastAPI 异常映射
  db/
    schema.sql                 # PostgreSQL 表结构
    field-notes.md             # 字段语义说明
    seed.sql                   # 可选种子数据
  requirements.txt
  .env.example
  README.md
```

## 2. 环境变量

复制 `backend/.env.example` 到 `backend/.env` 并填写：

- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- `WECHAT_MCH_ID`
- `WECHAT_MCH_KEY`
- `WECHAT_PAY_NOTIFY_URL`
- `CORS_ALLOW_ORIGINS`
- `CORS_ALLOW_ORIGIN_REGEX`

说明：
- 登录接口 `/api/v1/sessions/acquire` 会签发本地 JWT。
- 前端 Bearer Token 由后端 JWT 解析，不依赖外部鉴权服务。

## 3. 初始化数据库

在 PostgreSQL 中执行：
1. `backend/db/schema.sql`
2. （可选）`backend/db/seed.sql`

## 4. 安装与启动

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/healthz
```

## 5. 鉴权策略

### 5.1 匿名可访问
- `POST /api/v1/sessions/acquire`
- `GET /api/v1/catalog/products`
- `GET /api/v1/catalog/products/{product_id}`
- `GET /api/v1/articles`
- `GET /api/v1/articles/{article_id}`

### 5.2 需要登录（Bearer Token）
- `GET/PUT /api/v1/profile`
- `GET/POST/DELETE /api/v1/favorites*`
- `GET/POST /api/v1/bookings`
- `POST/GET/DELETE /api/v1/checkout/session`
- `POST /api/v1/payments/submit`
- `POST /api/v1/payments/wechat/prepare`

未提供或无效 Token 会返回 `E_SESSION_UNAVAILABLE`。

## 6. 统一错误响应

```json
{
  "code": "ERROR_CODE",
  "message": "Human readable description"
}
```

错误码范围来自 `error-convention.md`。

