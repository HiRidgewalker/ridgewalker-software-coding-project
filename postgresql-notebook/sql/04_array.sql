-- ============================================================================
-- 04. 数组类型（Array）——你提到的 "list" 对应 PostgreSQL 的数组
-- 核心差异点（vs MySQL）：MySQL 没有任何原生数组类型！
--   MySQL 模拟方式：逗号分隔字符串 / JSON / 多对多关联表（都不如数组方便）
-- 适用场景：标签、收藏 ID 列表、枚举集合
-- ============================================================================

-- ========== 1. 字面量与创建 ==========
-- 两种写法等价：ARRAY[...] 和 '{...}'::type[]
SELECT ARRAY['a','b','c'] AS arr1, '{a,b,c}'::text[] AS arr2;

-- 用临时表演示（正式数据在 users.tags）
CREATE TEMP TABLE demo_arr (id int, tags text[]);
INSERT INTO demo_arr VALUES
  (1, ARRAY['vip','student']),
  (2, '{new}'),
  (3, '{vip,teacher}');

-- ========== 2. 下标访问（⚠️ 从 1 开始！和 C/Python 的 0 不同） ==========
SELECT tags,
       tags[1] AS first_tag,
       tags[array_length(tags, 1)] AS last_tag
FROM demo_arr;

-- ========== 3. 长度 ==========
SELECT tags,
       cardinality(tags) AS len,        -- 总元素数（推荐）
       array_length(tags, 1) AS dim1    -- 指定维度的长度
FROM demo_arr;

-- ========== 4. 行 ↔ 数组互转（高频用法） ==========

-- 4.1 unnest：数组展开成多行
SELECT id, unnest(tags) AS tag FROM demo_arr;

-- 4.2 array_agg：多行聚合成数组（GROUP BY 场景）
SELECT tag, array_agg(id ORDER BY id) AS user_ids, count(*) AS cnt
FROM demo_arr, unnest(tags) AS tag
GROUP BY tag
ORDER BY cnt DESC;

-- 4.3 从查询结果构造数组
SELECT array_agg(name ORDER BY price DESC) AS top_names
FROM products WHERE category = 'electronics';

-- ========== 5. 操作符 ==========
-- @>   包含        <@   被包含
-- &&   有交集      ||   拼接
-- 可以先用简单值感受，再在真实数据上跑

-- 5.1 包含判断：找出 tags 包含 vip 的行（users 真实数据）
SELECT id, name, tags FROM users WHERE tags @> '{vip}';
SELECT id, name, tags FROM users WHERE tags <@ '{vip,student,teacher,new}';  -- 反向

-- 5.2 交集：和任一标签重叠
SELECT id, name, tags FROM users WHERE tags && ARRAY['vip','teacher'];

-- 5.3 拼接 / 追加 / 移除 / 去重
SELECT tags || '{gold}'::text[] AS append_gold FROM users WHERE id = 1;   -- 拼接
SELECT array_append(tags, 'gold')      FROM users WHERE id = 1;           -- 追加尾部
SELECT array_prepend('gold', tags)     FROM users WHERE id = 1;           -- 插入头部
SELECT array_remove(tags, 'vip')       FROM users WHERE id = 1;           -- 移除元素
SELECT array_cat(tags, tags)           FROM users WHERE id = 1;           -- 连接两个数组

-- 数组内去重（经典写法）
SELECT array_agg(DISTINCT t) FROM users, unnest(tags) AS t;

-- ========== 6. 查询条件：ANY / ALL（实用！） ==========

-- 6.1 ANY：= ANY(tags) 等价于 "等于其中任意一个"（最常用）
SELECT name FROM users WHERE 'vip' = ANY(tags);
-- 等价写法：SELECT name FROM users WHERE tags @> '{vip}';

-- 用 ANY 做多值过滤（不用写一串 OR）
SELECT name FROM users WHERE 'vip' = ANY(tags) OR 'student' = ANY(tags);

-- 6.2 ALL：数组里所有元素都满足条件
SELECT 3 = ALL (ARRAY[3,3,3]);  -- true
SELECT 3 = ALL (ARRAY[3,5]);    -- false
SELECT 3 = ANY (ARRAY[1,3,5]);  -- true

-- ========== 7. 数组排序与比较 ==========
-- PG 支持直接按数组排序（MySQL 只能按字符串凑合）
SELECT name, tags FROM users ORDER BY tags;   -- 按数组逐元素比较

-- 空数组处理
SELECT name, tags FROM users WHERE cardinality(tags) = 0;  -- 没有标签的用户
SELECT name, tags FROM users WHERE NOT (tags @> '{}');     -- 或 array_length(tags,1) IS NULL 表示 NULL

-- ========== 8. 实战：按标签统计用户数 ==========
SELECT tag, count(*) AS users
FROM users, unnest(tags) AS tag
GROUP BY tag
ORDER BY users DESC;

-- ========== 9. 多维数组（了解即可） ==========
SELECT ARRAY[[1,2],[3,4]] AS matrix;  -- 二维数组
SELECT (ARRAY[[1,2],[3,4]])[1][2];    -- 输出 2

-- ========== 10. 数组类型常用函数速查 ==========
-- unnest(x)          数组→多行
-- array_agg(x)       多行→数组
-- cardinality(x)     元素个数
-- array_length(x,n)  第 n 维长度
-- array_append / array_prepend / array_remove / array_cat
-- string_to_array / array_to_string  字符串↔数组（类似 MySQL 的 GROUP_CONCAT 反向操作）
SELECT array_to_string(ARRAY['a','b','c'], ',') AS str;      -- a,b,c
SELECT string_to_array('a,b,c', ',') AS arr;                 -- {a,b,c}
