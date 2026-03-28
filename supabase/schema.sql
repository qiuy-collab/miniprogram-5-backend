-- PostgreSQL schema synced from live longxing database on 2026-03-28

create extension if not exists pgcrypto;

create table if not exists admin_roles (
  id uuid primary key,
  code text not null unique,
  name text not null,
  created_at bigint not null
);

create table if not exists admin_users (
  id uuid primary key,
  username text not null unique,
  password_hash text not null,
  display_name text not null,
  status text not null,
  created_at bigint not null,
  updated_at bigint not null
);

create table if not exists admin_user_roles (
  id uuid primary key,
  admin_user_id uuid not null references admin_users(id) on delete cascade,
  admin_role_id uuid not null references admin_roles(id) on delete cascade,
  created_at bigint not null
);

create table if not exists admin_audit_logs (
  id uuid primary key,
  admin_user_id uuid references admin_users(id) on delete set null,
  entity_type text not null,
  entity_id text not null,
  action text not null,
  before_snapshot text,
  after_snapshot text,
  created_at bigint not null
);

create table if not exists app_users (
  id uuid primary key default gen_random_uuid(),
  created_at bigint not null default (extract(epoch from now()) * 1000)::bigint
);

create table if not exists app_sessions (
  id uuid primary key default gen_random_uuid(),
  login_code text not null unique,
  session_ready boolean not null default true,
  session_expires_at bigint not null,
  created_at bigint not null,
  updated_at bigint not null
);

create table if not exists media_assets (
  id uuid primary key default gen_random_uuid(),
  storage_key text not null,
  url text not null,
  media_type varchar(32) not null default 'image',
  mime_type varchar(128) not null default '',
  size_bytes bigint not null default 0,
  width integer,
  height integer,
  alt_text text not null default '',
  status varchar(32) not null default 'active',
  created_by_admin_id uuid,
  created_at timestamptz not null default now()
);

create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  price text not null,
  img text not null,
  description text not null,
  category text not null check (category in ('tea', 'orchid', 'course')),
  status varchar(32) not null default 'published',
  sort_order integer not null default 0,
  cover_media_id uuid,
  published_at timestamptz,
  created_by_admin_id uuid,
  updated_by_admin_id uuid
);

create index if not exists idx_products_category on products (category);

create table if not exists articles (
  id uuid primary key default gen_random_uuid(),
  date text not null,
  title text not null,
  description text not null,
  content_markdown text not null default '',
  status varchar(32) not null default 'published',
  cover_media_id uuid,
  published_at timestamptz,
  created_by_admin_id uuid,
  updated_by_admin_id uuid
);

create table if not exists article_contents (
  article_id uuid not null references articles(id) on delete cascade,
  sort_order integer not null check (sort_order >= 0),
  content text not null,
  primary key (article_id, sort_order)
);

create index if not exists idx_article_contents_article_sort
  on article_contents (article_id, sort_order);

create table if not exists profiles (
  user_id uuid primary key references app_users(id) on delete cascade,
  name text not null check (char_length(name) >= 1 and char_length(name) <= 10),
  city text not null default '' check (char_length(city) <= 12),
  phone text not null check (phone ~ '^1[0-9]{10}$'),
  motto text not null default '' check (char_length(motto) <= 40),
  updated_at bigint not null
);

create table if not exists favorites (
  user_id uuid not null references app_users(id) on delete cascade,
  product_id uuid not null references products(id) on delete restrict,
  count integer not null check (count >= 1),
  added_at bigint not null,
  primary key (user_id, product_id)
);

create index if not exists idx_favorites_user on favorites (user_id);

create table if not exists bookings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references app_users(id) on delete cascade,
  type_key text not null,
  type_label text not null,
  type_desc text not null,
  datetime text not null,
  name text not null check (char_length(name) >= 1 and char_length(name) <= 12),
  phone text not null check (phone ~ '^1[0-9]{10}$'),
  notes text not null default '' check (char_length(notes) <= 60),
  location text not null,
  status text not null,
  created_at bigint not null,
  status_code varchar(32) not null default 'new',
  internal_note text not null default '',
  assigned_admin_id uuid,
  updated_at timestamptz
);

create index if not exists idx_bookings_user_created_at
  on bookings (user_id, created_at desc);

create table if not exists checkout_sessions (
  user_id uuid primary key references app_users(id) on delete cascade,
  source text not null check (source in ('favorites', 'product')),
  created_at bigint not null
);

create table if not exists checkout_session_items (
  user_id uuid not null references checkout_sessions(user_id) on delete cascade,
  product_id uuid not null references products(id) on delete restrict,
  count integer not null check (count >= 1),
  primary key (user_id, product_id)
);

create index if not exists idx_checkout_session_items_user
  on checkout_session_items (user_id);

create table if not exists payments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references app_users(id) on delete cascade,
  checkout_created_at bigint not null,
  pay_method text not null check (pay_method in ('wechat', 'alipay')),
  source text not null check (source in ('favorites', 'product')),
  paid boolean not null,
  paid_product_ids uuid[] not null,
  created_at bigint not null,
  unique (user_id, checkout_created_at)
);

create index if not exists idx_payments_user_checkout_created_at
  on payments (user_id, checkout_created_at);

create table if not exists wechat_identities (
  openid text primary key,
  user_id uuid not null unique references app_users(id) on delete cascade,
  created_at bigint not null
);

create table if not exists wechat_payment_prepares (
  out_trade_no text primary key,
  user_id uuid not null references app_users(id) on delete cascade,
  checkout_created_at bigint not null,
  created_at bigint not null
);

create index if not exists idx_wechat_payment_prepares_user_checkout
  on wechat_payment_prepares (user_id, checkout_created_at);