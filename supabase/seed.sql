-- Seed data synced from live longxing database on 2026-03-28

insert into admin_roles (id, code, name, created_at) values
('202f8264-c411-405a-8843-a8e551c96839', 'super_admin', 'Super Admin', 1774634021),
('2303cd9b-6ca5-433b-8ec1-08149766950e', 'operator', 'Operator', 1774634021),
('a2689623-f1f8-4fec-93a3-b15d82d5bd29', 'editor', 'Editor', 1774634021)
on conflict (id) do update set
  code = excluded.code,
  name = excluded.name,
  created_at = excluded.created_at;

insert into admin_users (id, username, password_hash, display_name, status, created_at, updated_at) values
('96755e52-e012-47fc-b296-13635713ad53', 'admin', '7X2qQnwOIQoCJunQUJVr8tU0U02eHrf2bmz+cjGZGtk=', 'Super Admin', 'active', 1774634021, 1774634021)
on conflict (id) do update set
  username = excluded.username,
  password_hash = excluded.password_hash,
  display_name = excluded.display_name,
  status = excluded.status,
  created_at = excluded.created_at,
  updated_at = excluded.updated_at;

insert into admin_user_roles (id, admin_user_id, admin_role_id, created_at) values
('5213edb5-89bb-4230-98f2-f4cdb90c9bf4', '96755e52-e012-47fc-b296-13635713ad53', '202f8264-c411-405a-8843-a8e551c96839', 1774634021)
on conflict (id) do update set
  admin_user_id = excluded.admin_user_id,
  admin_role_id = excluded.admin_role_id,
  created_at = excluded.created_at;

insert into products (
  id, name, price, img, description, category, status, sort_order, cover_media_id, published_at, created_by_admin_id, updated_by_admin_id
) values
('11111111-1111-1111-1111-111111111111', '明前龙井 · 灵芽', '880', 'https://example.com/t1.jpg', '取谷雨前初发之芽。', 'tea', 'published', 0, null, null, null, null),
('22222222-2222-2222-2222-222222222222', '春剑 · 幽兰', '2600', 'https://example.com/o1.jpg', '叶姿挺拔，香气幽远。', 'orchid', 'published', 0, null, null, null, null),
('33333333-3333-3333-3333-333333333333', '茶礼仪培训', '1280', 'https://example.com/c1.jpg', '系统学习茶席规范。', 'course', 'published', 0, null, null, null, null)
on conflict (id) do update set
  name = excluded.name,
  price = excluded.price,
  img = excluded.img,
  description = excluded.description,
  category = excluded.category,
  status = excluded.status,
  sort_order = excluded.sort_order,
  cover_media_id = excluded.cover_media_id,
  published_at = excluded.published_at,
  created_by_admin_id = excluded.created_by_admin_id,
  updated_by_admin_id = excluded.updated_by_admin_id;

insert into articles (
  id, date, title, description, content_markdown, status, cover_media_id, published_at, created_by_admin_id, updated_by_admin_id
) values
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', '岁序·立春', '春茶开采记', '关于山野与新芽的故事。', E'立春后的第一场细雨落下。\n\n采茶讲究稳与轻。', 'published', null, null, null, null),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', '岁序·清明', '论点茶', '一盏茶汤里的心神归位。', E'点茶不是炫技，而是修心。', 'published', null, null, null, null)
on conflict (id) do update set
  date = excluded.date,
  title = excluded.title,
  description = excluded.description,
  content_markdown = excluded.content_markdown,
  status = excluded.status,
  cover_media_id = excluded.cover_media_id,
  published_at = excluded.published_at,
  created_by_admin_id = excluded.created_by_admin_id,
  updated_by_admin_id = excluded.updated_by_admin_id;

insert into article_contents (article_id, sort_order, content) values
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 0, '立春后的第一场细雨落下。'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 1, '采茶讲究稳与轻。'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 0, '点茶不是炫技，而是修心。')
on conflict (article_id, sort_order) do update set
  content = excluded.content;