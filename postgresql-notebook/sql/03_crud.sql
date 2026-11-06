-- ============================================================================
-- 03. CRUD：增 / 删 / 改 / 查 + 事务
-- 核心差异点（vs MySQL）：
--   * INSERT/UPDATE/DELETE 都支持 RETURNING 返回受影响的行（MySQL 不支持）
--   * INSERT ... ON CONFLICT（MySQL: INSERT ... ON DUPLICATE KEY UPDATE）
--   * 多表 UPDATE 用 FROM 子句、多表 DELETE 用 USING 子句（MySQL 用 JOIN）
--   * ORDER BY 支持 NULLS FIRST / NULLS LAST（MySQL 没有）
--   * DISTINCT ON 取每组第一条（MySQL 没有，需子查询模拟）
-- ============================================================================

-- ========== 1. INSERT ==========

-- 1.1 单行插入 + RETURNING（MySQL 只能 LAST_INSERT_ID() 拿 id）
INSERT INTO users (name, email, tags, profile)
VALUES ('Frank Wu', 'frank@example.com', '{new,student}', '{"city":"Shenzhen","age":22}')
RETURNING id, name, created_at;

-- 1.2 多行插入 + RETURNING
INSERT INTO products (name, price, category, attributes, stock, description) VALUES
('USB-C Hub', 49.90, 'electronics', '{"brand":"Anker","ports":7}', 50, '7-in-1 USB-C hub with HDMI'),
('Yoga Mat',  25.00, 'sports',     '{"color":"purple","thickness":"6mm"}', 120, 'Non-slip yoga mat')
RETURNING id, name;

-- 1.3 冲突处理：ON CONFLICT (唯一键) DO NOTHING / DO UPDATE
--     对应 MySQL 的 INSERT ... ON DUPLICATE KEY UPDATE
-- alice@example.com 已存在 → 什么也不做，RETURNING 返回 0 行
INSERT INTO users (name, email, tags, profile)
VALUES ('Alice Chen', 'alice@example.com', '{vip}', '{}')
ON CONFLICT (email) DO NOTHING
RETURNING *;

-- 换成 DO UPDATE：冲突时更新 tags（EXCLUDED 指"本次想插入的值"）
-- 观察：Alice 的 tags 从 {vip,student} 变成 {vip,student,gold}
INSERT INTO users (name, email, tags, profile)
VALUES ('Alice Chen', 'alice@example.com', '{gold}', '{}')
ON CONFLICT (email) DO UPDATE SET tags = users.tags || EXCLUDED.tags
RETURNING id, name, tags;

-- ========== 2. SELECT ==========

-- 2.1 基础过滤 + 排序分页
SELECT id, name, email FROM users WHERE id > 2 ORDER BY id DESC LIMIT 3;

-- NULLS LAST：MySQL 里 NULL 永远排最前；PG 可以控制
SELECT name, tags FROM users ORDER BY tags DESC NULLS LAST;

-- 2.2 聚合 + GROUP BY + HAVING
SELECT category, count(*) AS cnt, round(avg(price),2) AS avg_price, sum(stock) AS total_stock
FROM products
GROUP BY category
HAVING count(*) >= 2
ORDER BY cnt DESC;

-- 2.3 多表 JOIN
SELECT o.id AS order_id, u.name, o.status, o.total, o.created_at::date AS day
FROM orders o JOIN users u ON u.id = o.user_id
WHERE o.status <> 'cancelled'
ORDER BY o.created_at DESC;

-- 2.4 标量子查询（一行一列）
SELECT u.name, u.email,
       (SELECT count(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u
ORDER BY order_count DESC;

-- 2.5 DISTINCT ON：按 category 分组取价格最高的商品（每组第一条）
--     MySQL 没有这个语法，只能写子查询
SELECT DISTINCT ON (category) category, name, price
FROM products
ORDER BY category, price DESC;

-- ========== 3. UPDATE ==========

-- 3.1 普通更新 + RETURNING（把电子产品价格打 9 折、库存减 5）
UPDATE products
SET price = price * 0.9, stock = stock - 5
WHERE category = 'electronics'
RETURNING id, name, price, stock;

-- 3.2 多表更新：PG 用 FROM 子句（先造临时数据，避免污染正式数据）
INSERT INTO users (name, email, tags, profile) VALUES ('Temp User', 'temp@example.com', '{}', '{}');
INSERT INTO orders (user_id, status, total, items) VALUES
  ((SELECT id FROM users WHERE email = 'temp@example.com'), 'paid', 50.00,
   '[{"product_id":6,"name":"Cotton T-Shirt","qty":1,"price":50.00}]');

UPDATE orders o
SET total = o.total + 5
FROM users u
WHERE o.user_id = u.id AND u.email = 'temp@example.com'
RETURNING o.id, o.total;

-- ========== 4. DELETE ==========

-- 4.1 删除 + RETURNING（删掉刚才的临时数据）
DELETE FROM orders WHERE user_id = (SELECT id FROM users WHERE email = 'temp@example.com')
RETURNING id, total;

-- 4.2 多表删除：PG 用 USING 子句（先造临时订单再删）
INSERT INTO orders (user_id, status, total, items) VALUES
  ((SELECT id FROM users WHERE email = 'temp@example.com'), 'pending', 10.00,
   '[{"product_id":6,"name":"Cotton T-Shirt","qty":1,"price":10.00}]');

DELETE FROM orders o USING users u
WHERE o.user_id = u.id AND u.email = 'temp@example.com'
RETURNING o.id;

DELETE FROM users WHERE email = 'temp@example.com' RETURNING id, name;  -- 清理临时用户

-- ========== 5. 事务 ==========

-- 5.1 提交/回滚
BEGIN;
UPDATE products SET stock = stock - 1 WHERE id = 1;
SELECT id, name, stock FROM products WHERE id = 1;   -- 当前会话可见（未提交）
ROLLBACK;                                            -- 撤销；若改 COMMIT 则生效

-- 验证回滚生效
SELECT id, stock FROM products WHERE id = 1;

-- 5.2 事务内出错 → 整体回滚（原子性）
BEGIN;
UPDATE products SET stock = stock - 1 WHERE id = 1;
INSERT INTO orders (user_id, status, total, items) VALUES (999, 'pending', 0, '[]');  -- 外键失败!
COMMIT;            -- 报错：当前事务已中止（aborted）
ROLLBACK;          -- 收尾：退出中止状态

-- 验证：库存没有被扣
SELECT id, stock FROM products WHERE id = 1;

-- ========== 6. 查询利器：ILIKE / 正则 / 行值比较 ==========

-- 6.1 ILIKE：大小写不敏感模糊匹配（MySQL 用 LIKE + collation 或 LOWER()）
SELECT name FROM products WHERE name ILIKE '%keyboard%';

-- 6.2 正则：~ 匹配 / ~* 不区分大小写（MySQL 用 REGEXP，写法不同）
SELECT name FROM products WHERE name ~* 'mac|air';

-- 6.3 行值比较（PG 独有语法，MySQL 不支持）
SELECT * FROM orders WHERE (user_id, status) = (1, 'paid');
