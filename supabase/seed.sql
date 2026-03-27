-- Optional seed data
insert into products (id, name, price, img, description, category) values
('11111111-1111-1111-1111-111111111111', '明前龙井 · 灵芽', '880', 'https://example.com/t1.jpg', '取谷雨前初发之芽。', 'tea'),
('22222222-2222-2222-2222-222222222222', '春剑 · 幽兰', '2600', 'https://example.com/o1.jpg', '叶姿挺拔，香气幽远。', 'orchid'),
('33333333-3333-3333-3333-333333333333', '茶礼仪培训', '1280', 'https://example.com/c1.jpg', '系统学习茶席规范。', 'course')
on conflict (id) do nothing;

insert into articles (id, date, title, description, content_markdown) values
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', '岁序·立春', '春茶开采记', '关于山野与新芽的故事。', E'# 春茶开采记\n\n立春后的第一场细雨落下。\n\n![春茶山场](/uploads/articles/spring-tea.jpg "春茶山场")\n\n采茶讲究稳与轻。'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', '岁序·清明', '论点茶', '一盏茶汤里的心神归位。', E'# 论点茶\n\n点茶不是炫技，而是修心。\n\n![点茶](/uploads/articles/tea-whisk.jpg)\n\n1. 温盏\n2. 注汤\n3. 击拂')
on conflict (id) do update set
  date = excluded.date,
  title = excluded.title,
  description = excluded.description,
  content_markdown = excluded.content_markdown;

insert into article_contents (article_id, sort_order, content) values
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 0, '# 春茶开采记'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 1, '立春后的第一场细雨落下。'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 2, '![春茶山场](/uploads/articles/spring-tea.jpg "春茶山场")'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 3, '采茶讲究稳与轻。'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 0, '# 论点茶'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 1, '点茶不是炫技，而是修心。'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 2, '![点茶](/uploads/articles/tea-whisk.jpg)'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 3, '1. 温盏\n2. 注汤\n3. 击拂')
on conflict (article_id, sort_order) do update set
  content = excluded.content;
