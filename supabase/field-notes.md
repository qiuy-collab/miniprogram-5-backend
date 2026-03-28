# Supabase 字段说明（已按 longxing 实库同步）

本文件对应 `schema.sql`，用于说明当前 `public` schema 的主键、外键、索引与字段语义。

## 1. `admin_roles`

- 主键: `id` (UUID)

- 唯一约束: `code`

- 字段:

  - `code`: 角色编码

  - `name`: 角色名称

  - `created_at`: 创建时间戳

## 2. `admin_users`

- 主键: `id` (UUID)

- 唯一约束: `username`

- 字段:

  - `username`: 管理员登录名

  - `password_hash`: 密码摘要

  - `display_name`: 显示名称

  - `status`: 状态

  - `created_at`, `updated_at`: 时间戳

## 3. `admin_user_roles`

- 主键: `id` (UUID)

- 外键:

  - `admin_user_id -> admin_users.idon delete cascade`）

  - `admin_role_id -> admin_roles.idon delete cascade`）

- 字段:

  - `created_at`: 创建时间戳

## 4. `admin_audit_logs`

- 主键: `id` (UUID)

- 外键:

  - `admin_user_id -> admin_users.idon delete set null`）

- 字段:

  - `entity_type`: 实体类型

  - `entity_id`: 实体标识

  - `action`: 审计动作

  - `before_snapshot`: 变更前快照

  - `after_snapshot`: 变更后快照

  - `created_at`: 创建时间戳

## 5. `app_users`

- 主键: `id` (UUID)

- 字段:

  - `created_at`: 创建时间戳（毫秒）

## 6. `app_sessions`

- 主键: `id` (UUID)

- 唯一约束: `login_code`

- 字段:

  - `session_ready`: 会话是否可用

  - `session_expires_at`: 会话过期时间戳（毫秒）

  - `created_at`, `updated_at`: 记录时间戳（毫秒）

## 7. `media_assets`

- 主键: `id` (UUID)

- 字段:

  - `storage_key`: 存储键

  - `url`: 访问地址

  - `media_type`: 媒体类型，默认 `image`

  - `mime_type`: MIME 类型

  - `size_bytes`: 文件字节数

  - `width`, `height`: 尺寸，可空

  - `alt_text`: 替代文本

  - `status`: 资源状态，默认 `active`

  - `created_by_admin_id`: 创建管理员 ID，可空

  - `created_at`: 创建时间（timestamptz）

## 8. `products`

- 主键: `id` (UUID)

- 字段:

  - `name`: 商品名称

  - `price`: 展示价格字符串

  - `img`: 图片地址

  - `description`: 商品描述（接口映射为 `desc`）

  - `category`: 商品分类`tea` / `orchid` / `course`）

  - `status`: 发布状态，默认 `published`

  - `sort_order`: 排序值，默认 `0`

  - `cover_media_id`: 封面媒体 ID，可空

  - `published_at`: 发布时间，可空

  - `created_by_admin_id`, `updated_by_admin_id`: 管理员 ID，可空

- 索引: `idx_products_category(category)`

## 9. `articles`

- 主键: `id` (UUID)

- 字段:

  - `date`: 文章日期文案

  - `title`: 标题

  - `description`: 摘要（接口映射为 `desc`）

  - `content_markdown`: Markdown 正文

  - `status`: 发布状态，默认 `published`

  - `cover_media_id`: 封面媒体 ID，可空

  - `published_at`: 发布时间，可空

  - `created_by_admin_id`, `updated_by_admin_id`: 管理员 ID，可空

## 10. `article_contents`

- 主键: `(article_id, sort_order)`

- 外键: `article_id -> articles.idon delete cascade`）

- 字段:

  - `sort_order`: 段落顺序`>= 0`）

  - `content`: 段落内容

- 索引: `idx_article_contents_article_sort(article_id, sort_order)`

## 11. `profiles`

- 主键/外键: `user_id -> app_users.id`

- 字段:

  - `name`：长度 `1~10`

  - `city`：长度 `<= 12`，默认空串

  - `phone`：11 位手机号，正则校验

  - `motto`：长度 `<= 40`，默认空串

  - `updated_at`: 更新时间戳（毫秒）

## 12. `favorites`

- 主键: `(user_id, product_id)`

- 外键:

  - `user_id -> app_users.id`

  - `product_id -> products.id`

- 字段:

  - `count`: 收藏数量`>= 1`）

  - `added_at`: 最近加入时间戳（毫秒）

- 索引: `idx_favorites_user(user_id)`

## 13. `bookings`

- 主键: `id` (UUID)

- 外键: `user_id -> app_users.id`

- 字段:

  - `type_key`, `type_label`, `type_desc`

  - `datetime`: 预约时间字符串

  - `name`: 长度 `1~12`

  - `phone`: 11 位手机号，正则校验

  - `notes`: 备注，长度 `<= 60`

  - `location`: 预约地点

  - `status`: 原始状态文本

  - `created_at`: 创建时间戳（毫秒）

  - `status_code`: 后台状态码，默认 `new`

  - `internal_note`: 内部备注，默认空串

  - `assigned_admin_id`: 指派管理员 ID，可空

  - `updated_at`: 更新时间（timestamptz），可空

- 索引: `idx_bookings_user_created_at(user_id, created_at desc)`

## 14. `checkout_sessions`

- 主键/外键: `user_id -> app_users.id`

- 字段:

  - `source`: `favorites` / `product`

  - `created_at`: 会话创建时间戳（毫秒）

## 15. `checkout_session_items`

- 主键: `(user_id, product_id)`

- 外键:

  - `user_id -> checkout_sessions.user_id`

  - `product_id -> products.id`

- 字段:

  - `count`: 结算数量`>= 1`）

- 索引: `idx_checkout_session_items_user(user_id)`

## 16. `payments`

- 主键: `id` (UUID)

- 外键: `user_id -> app_users.id`

- 唯一约束: `(user_id, checkout_created_at)`（支付幂等键）

- 字段:

  - `checkout_created_at`: 结算会话时间戳

  - `pay_method`: `wechat` / `alipay`

  - `source`: `favorites` / `product`

  - `paid`: 是否支付成功

  - `paid_product_ids`: 本次支付商品 ID 数组

  - `created_at`: 支付记录创建时间戳（毫秒）

- 索引: `idx_payments_user_checkout_created_at(user_id, checkout_created_at)`

## 17. `wechat_identities`

- 主键: `openid`

- 外键: `user_id -> app_users.id`

- 唯一约束: `user_id`

- 字段:

  - `openid`: 微信用户在当前小程序下的唯一标识

  - `user_id`: 平台用户 ID

  - `created_at`: 映射创建时间戳（毫秒）

## 18. `wechat_payment_prepares`

- 主键: `out_trade_no`

- 外键: `user_id -> app_users.id`

- 字段:

  - `out_trade_no`: 微信支付商户订单号

  - `user_id`: 订单所属用户

  - `checkout_created_at`: 对应结算会话时间戳（毫秒）

  - `created_at`: 预下单创建时间戳（毫秒）

- 索引: `idx_wechat_payment_prepares_user_checkout(user_id, checkout_created_at)`