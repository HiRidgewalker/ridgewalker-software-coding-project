-- ============================================================================
-- 05. JSON / JSONB
-- 核心差异点（vs MySQL）：
--   * PG 有两种 JSON 类型；MySQL 只有一种 JSON
--       json   ：原样保存文本（保留空白/键序/重复键），不能索引，无等值比较
--       jsonb  ：解析成二进制存储（键重排/去重/去空白），可建 GIN 索引，有操作符
--     → 业务场景几乎都用 jsonb
--   * PG 操作符：->  ->>  #>  #>>  @>  ?  ?|  ?&  ||  -
--     MySQL 操作符/函数：->  ->>  JSON_EXTRACT  JSON_CONTAINS  JSON_SET ...
-- ============================================================================

-- ========== 1. json vs jsonb 的存储差异 ==========

-- 1.1 重复键：json 保留，jsonb 去重（后者覆盖前者）
SELECT '{"b":1, "a":2, "b":3}'::json;    -- 原样：{"b":1, "a":2, "b":3}
SELECT '{"b":1, "a":2, "b":3}'::jsonb;   -- 去重+重排：{"a": 2, "b": 3}

-- 1.2 空白：json 保留，jsonb 压缩
SELECT '{"x": 1, "y": 2}'::json;         -- 原样
SELECT '{"x": 1, "y": 2}'::jsonb;        -- {"x": 1, "y": 2}

-- 1.3 等值比较：jsonb 支持 =，json 不支持
SELECT '{"a":1}'::jsonb = '{"a":1}'::jsonb;   -- true
-- SELECT '{"a":1}'::json = '{"a":1}'::json;  -- 报错：json 没有 = 操作符

-- ========== 2. 访问操作符：-> 与 ->> ==========
-- users.profile 示例：{"city":"Shanghai","age":25,"preferences":{"theme":"dark","language":"zh"}}

-- 2.1 -> 返回 jsonb，->> 返回 text（注意显示格式差异：带不带引号）
SELECT profile -> 'city' AS city_jsonb,
       profile ->> 'city' AS city_text
FROM users WHERE id = 1;

-- 2.2 数字取值注意类型
SELECT profile ->> 'age' AS age_text,                    -- text: '25'
       (profile ->> 'age')::int + 1 AS age_plus_1        -- int: 26
FROM users WHERE id = 1;

-- 2.3 嵌套访问：链式 -> 或路径操作符 #> / #>>
SELECT profile #> '{preferences,theme}' AS theme,        -- jsonb: "dark"
       profile #>> '{preferences,language}' AS lang      -- text:  zh
FROM users WHERE id = 1;

-- 2.4 数组下标：jsonb 数组从 0 开始（区别于 PG 数组从 1 开始）
SELECT items -> 0 ->> 'name' AS first_item,
       items -> 1 ->> 'qty'  AS second_qty
FROM orders WHERE id = 2;   -- 订单2 有两件商品

-- ========== 3. 存在性判断（jsonb 核心操作符） ==========
-- @>   左边 jsonb 包含右边
-- ?    键是否存在
-- ?|   任一键存在
-- ?&   所有键存在

SELECT name FROM users WHERE profile @> '{"city":"Shanghai"}';      -- 按值过滤
SELECT name FROM users WHERE profile ? 'preferences';               -- 按键过滤
SELECT name FROM users WHERE profile ?| ARRAY['age','height'];      -- 有任一键
SELECT name FROM users WHERE profile ?& ARRAY['city','age'];        -- 同时有这两个键

-- 商品属性查询（jsonb 最典型的业务场景）
SELECT id, name FROM products WHERE attributes @> '{"brand":"Apple"}';
SELECT id, name FROM products WHERE attributes @> '{"color":"black"}';

-- jsonb 数组包含判断：谁买过 MacBook Air M3（product_id=1）
SELECT id, user_id FROM orders WHERE items @> '[{"product_id":1}]';

-- ========== 4. 修改 jsonb ==========

-- 4.1 jsonb_set：修改或新增键（MySQL 对应 JSON_SET）
SELECT profile,
       jsonb_set(profile, '{city}', '"Hangzhou"') AS changed
FROM users WHERE id = 1;

-- 4.2 删除键：- 操作符
SELECT profile - 'preferences' AS without_prefs FROM users WHERE id = 1;

-- ========== 5. 展开与聚合 ==========

-- 5.1 jsonb_array_elements：jsonb 数组展开为多行（类似 unnest）
--     语法：FROM orders o, jsonb_array_elements(o.items) AS item（隐式 LATERAL）
SELECT o.id AS order_id, item ->> 'name' AS product,
       (item ->> 'qty')::int AS qty, (item ->> 'price')::numeric AS price
FROM orders o, jsonb_array_elements(o.items) AS item
WHERE o.id IN (1, 2);

-- 5.2 每个订单包含几种商品
SELECT id, jsonb_array_length(items) AS item_kinds FROM orders;

-- 5.3 jsonb_each：键值对展开成行（jsonb_each_text 返回 text 值）
SELECT key, value FROM users, jsonb_each(profile) WHERE id = 1;

-- 5.4 按 jsonb 字段聚合统计
SELECT profile ->> 'city' AS city, count(*) AS cnt
FROM users GROUP BY 1 ORDER BY cnt DESC;

-- 5.5 行 → jsonb：to_jsonb / jsonb_build_object
SELECT to_jsonb(u) FROM users u WHERE id = 1;   -- 整行转 jsonb

SELECT jsonb_build_object(
    'user', u.name,
    'order_count', count(o.id),
    'total_spent', coalesce(sum(o.total), 0)
)
FROM users u LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name
ORDER BY 1;

-- ========== 6. GIN 索引（jsonb 查询加速的关键） ==========
CREATE INDEX IF NOT EXISTS idx_products_attributes ON products USING GIN (attributes);
CREATE INDEX IF NOT EXISTS idx_orders_items ON orders USING GIN (items);

-- 对比执行计划：@> 查询应走 Bitmap Index Scan（没建索引时是 Seq Scan）
EXPLAIN ANALYZE SELECT id, name FROM products WHERE attributes @> '{"brand":"Apple"}';

-- 注意：@> / ? 等操作符必须用 GIN；= 精确匹配才用 btree。
-- 可以再看一下索引列表：
\di

-- ========== 7. 类型互转 ==========
SELECT '{"a":1}'::jsonb::json;   -- jsonb → json
SELECT '{"a":1}'::json::jsonb;   -- json → jsonb（键重排、去重）
