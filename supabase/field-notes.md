# Supabase 字段说明

本文件对应数据库 schema.sql，用于说明主键、外键、索引与字段语义。

## 1. `products`
- 主键: `id` (UUID)
- 字段:
  - `name`: 商品名称
  - `price`: 展示价格字符串
  - `img`: 图片地址
  - `description`: 商品描述（接口映射为 `desc`）
  - `category`: 商品分类（`tea`/`orchid`/`course`）
- 索引: `idx_products_category(category)`

## 2. `articles`
- 主键: `id` (UUID)
- 字段:
  - `date`: 文章日期文案
  - `title`: 标题
  - `description`: 摘要（接口映射为 `desc`）

## 3. `article_contents`
- 主键: `(article_id, sort_order)`
- 外键: `article_id -> articles.id`
- 字段:
  - `sort_order`: 段落顺序
  - `content`: 段落内容
- 索引: `idx_article_contents_article_sort(article_id, sort_order)`

## 4. `profiles`
- 主键/外键: `user_id -> app_users.id`
- 字段:
  - `name` (1~10)
  - `city` (<=12)
  - `phone` (11位，正则校验)
  - `motto` (<=40)
  - `updated_at`: 更新时间戳（毫秒）

## 5. `favorites`
- 主键: `(user_id, product_id)`
- 外键:
  - `user_id -> app_users.id`
  - `product_id -> products.id`
- 字段:
  - `count`: 收藏数量（>=1）
  - `added_at`: 最近加入时间戳（毫秒）
- 索引: `idx_favorites_user(user_id)`

## 6. `bookings`
- 主键: `id` (UUID)
- 外键: `user_id -> app_users.id`
- 字段:
  - `type_key`, `type_label`, `type_desc`
  - `datetime`: 预约时间字符串
  - `name`, `phone`, `notes`
  - `location`, `status`
  - `created_at`: 创建时间戳（毫秒）
- 索引: `idx_bookings_user_created_at(user_id, created_at desc)`

## 7. `checkout_sessions`
- 主键/外键: `user_id -> app_users.id`
- 字段:
  - `source`: `favorites`/`product`
  - `created_at`: 会话创建时间戳（毫秒）

## 8. `checkout_session_items`
- 主键: `(user_id, product_id)`
- 外键:
  - `user_id -> checkout_sessions.user_id`
  - `product_id -> products.id`
- 字段:
  - `count`: 结算数量（>=1）
- 索引: `idx_checkout_session_items_user(user_id)`

## 9. `payments`
- 主键: `id` (UUID)
- 外键: `user_id -> app_users.id`
- 唯一约束: `(user_id, checkout_created_at)`（支付幂等键）
- 字段:
  - `pay_method`: `wechat`/`alipay`
  - `source`: `favorites`/`product`
  - `paid`: 是否支付成功
  - `paid_product_ids`: 本次支付商品ID数组
  - `created_at`: 支付记录创建时间戳（毫秒）
- 索引: `idx_payments_user_checkout_created_at(user_id, checkout_created_at)`

## 10. `app_sessions`
- 主键: `id` (UUID)
- 唯一约束: `login_code`
- 字段:
  - `session_ready`: 会话是否可用
  - `session_expires_at`: 会话过期时间戳（毫秒）
  - `created_at`, `updated_at`: 记录时间戳（毫秒）

## 11. `wechat_identities`
- 主键: `openid`
- 外键: `user_id -> app_users.id`
- 唯一约束: `user_id`
- 字段:
  - `openid`: 微信用户在当前小程序下的唯一标识
  - `user_id`: 平台用户ID（用于关联业务数据）
  - `created_at`: 映射创建时间戳（毫秒）

## 12. `wechat_payment_prepares`
- 主键: `out_trade_no`
- 外键: `user_id -> app_users.id`
- 字段:
  - `out_trade_no`: 微信支付商户订单号（用于回调定位）
  - `user_id`: 订单所属用户
  - `checkout_created_at`: 对应结算会话时间戳（毫秒）
  - `created_at`: 预下单创建时间戳（毫秒）
- 索引: `idx_wechat_payment_prepares_user_checkout(user_id, checkout_created_at)`


