-- ============================================================================
-- 02. 建表 + 种子数据（电商：users / products / orders）
-- PostgreSQL 特色类型一览（vs MySQL）：
--   BIGINT GENERATED ALWAYS AS IDENTITY  自增主键（MySQL: AUTO_INCREMENT）
--   TEXT                                 不限长度字符串（MySQL: TEXT/VARCHAR 混合）
--   NUMERIC(10,2)                        精确小数（MySQL: DECIMAL，等价）
--   TIMESTAMPTZ                          带时区时间戳，内部按 UTC 存储
--   TEXT[]                               数组（MySQL 没有！）
--   JSONB                                二进制 JSON（MySQL 只有 JSON）
--   ENUM                                 枚举类型（PG 的枚举是独立类型，可复用）
-- ============================================================================

-- 0. 清理旧对象（重复执行本文件不会报错）
DROP TABLE IF EXISTS orders, products, users CASCADE;
DROP TYPE IF EXISTS order_status CASCADE;

-- ========== 1. 创建枚举类型 ==========
-- MySQL 的 ENUM 是列内嵌的；PG 的枚举是独立类型，多张表可复用
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'completed', 'cancelled');

-- ========== 2. users 表 ==========
CREATE TABLE users (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- 自增主键
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,          -- 唯一约束（03 的 ON CONFLICT 要用）
    tags       TEXT[] NOT NULL DEFAULT '{}',  -- 数组列（04 章重点）
    profile    JSONB NOT NULL DEFAULT '{}',   -- jsonb 列（05 章重点）
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========== 3. products 表 ==========
CREATE TABLE products (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL,
    price       NUMERIC(10,2) NOT NULL CHECK (price >= 0),   -- CHECK 约束
    category    TEXT NOT NULL,
    attributes  JSONB NOT NULL DEFAULT '{}',   -- 商品属性（jsonb）
    stock       INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    description TEXT NOT NULL DEFAULT '',      -- 全文检索用（06 章）
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========== 4. orders 表 ==========
CREATE TABLE orders (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(id),   -- 外键
    status     order_status NOT NULL DEFAULT 'pending',
    total      NUMERIC(10,2) NOT NULL DEFAULT 0,
    items      JSONB NOT NULL DEFAULT '[]',            -- 商品明细快照：[{product_id,name,qty,price}]
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 建一个"用户-订单"的常规索引（外键列最好建索引，PG 不会自动建）
CREATE INDEX idx_orders_user_id ON orders (user_id);
CREATE INDEX idx_products_category ON products (category);

-- ========== 5. 种子数据 ==========

INSERT INTO users (name, email, tags, profile) VALUES
('Alice Chen',  'alice@example.com',  '{vip,student}', '{"city":"Shanghai","age":25,"preferences":{"theme":"dark","language":"zh"}}'),
('Bob Li',      'bob@example.com',    '{new}',         '{"city":"Beijing","age":30,"preferences":{"theme":"light","language":"en"}}'),
('Carol Wang',  'carol@example.com',  '{vip,teacher}', '{"city":"Guangzhou","age":35,"preferences":{"theme":"dark","language":"zh"}}'),
('David Zhang', 'david@example.com',  '{}',            '{"city":"Hangzhou","age":28}'),
('Eve Liu',     'eve@example.com',    '{student}',     '{"city":"Shanghai","age":21,"preferences":{"language":"zh"}}');

INSERT INTO products (name, price, category, attributes, stock, description) VALUES
('MacBook Air M3',     999.00, 'electronics', '{"brand":"Apple","color":"silver","warranty_years":1}',     10,  'Apple MacBook Air with M3 chip, 13 inch'),
('Mechanical Keyboard', 89.90, 'electronics', '{"brand":"Keychron","layout":"75%","switch":"red"}',         45,  'Wireless mechanical keyboard with red switches'),
('AirPods Pro 2',      159.98, 'electronics', '{"brand":"Apple","color":"white"}',                         30,  'Apple AirPods Pro with active noise cancellation'),
('PostgreSQL实战',      79.00, 'books',       '{"author":"张三","publisher":"人民邮电出版社","pages":560}', 100, 'PostgreSQL in practice, Chinese edition'),
('三体全集',            128.00, 'books',      '{"author":"刘慈欣","publisher":"重庆出版社"}',              80,  'The Three-Body Problem trilogy'),
('Cotton T-Shirt',      39.90, 'clothing',    '{"brand":"Uniqlo","color":"black","size":"M"}',             200, 'Basic cotton t-shirt'),
('Levi''s Jeans',       199.00, 'clothing',   '{"brand":"Levi''s","color":"blue","size":30}',              60,  'Classic blue jeans size 30'),
('Espresso Machine',   299.00, 'home',        '{"brand":"Delonghi","color":"silver"}',                     15,  'Semi-automatic espresso machine');

INSERT INTO orders (user_id, status, total, items, created_at) VALUES
(1, 'completed', 999.00, '[{"product_id":1,"name":"MacBook Air M3","qty":1,"price":999.00}]',                                '2025-11-01 10:00:00+08'),
(1, 'paid',      249.88, '[{"product_id":2,"name":"Mechanical Keyboard","qty":1,"price":89.90},{"product_id":3,"name":"AirPods Pro 2","qty":1,"price":159.98}]', '2025-12-15 20:30:00+08'),
(2, 'completed', 207.00, '[{"product_id":4,"name":"PostgreSQL实战","qty":1,"price":79.00},{"product_id":5,"name":"三体全集","qty":1,"price":128.00}]',          '2026-01-05 09:15:00+08'),
(3, 'shipped',   39.90,  '[{"product_id":6,"name":"Cotton T-Shirt","qty":1,"price":39.90}]',                                 '2026-01-20 14:00:00+08'),
(3, 'pending',   299.00, '[{"product_id":8,"name":"Espresso Machine","qty":1,"price":299.00}]',                              '2026-02-10 18:45:00+08'),
(4, 'cancelled', 199.00, '[{"product_id":7,"name":"Levi''s Jeans","qty":1,"price":199.00}]',                                 '2025-12-01 11:00:00+08'),
(5, 'pending',   79.00,  '[{"product_id":4,"name":"PostgreSQL实战","qty":1,"price":79.00}]',                                 '2026-02-25 22:10:00+08');

-- ========== 6. 验证 ==========
-- 查看表结构（重点看类型）
\d users
\d orders

-- 各表行数
SELECT 'users' AS tbl, count(*) FROM users
UNION ALL SELECT 'products', count(*) FROM products
UNION ALL SELECT 'orders', count(*) FROM orders;
