-- ============================================================================
-- 06. 团队常用高级特性
-- 覆盖：CTE / 递归 CTE / 窗口函数 / 分组集 / 全文检索 / 物化视图 / 分区表 / 扩展 / EXPLAIN
-- ============================================================================

-- ========== 1. CTE（WITH 子句） ==========
-- 把复杂查询拆成可读步骤；同一 CTE 可被多次引用（MySQL 8 也支持，写法一致）

WITH order_stats AS (
    SELECT user_id, count(*) AS cnt, sum(total) AS amount
    FROM orders
    WHERE status <> 'cancelled'
    GROUP BY user_id
)
SELECT u.name, os.cnt AS order_count, round(os.amount, 2) AS amount
FROM order_stats os JOIN users u ON u.id = os.user_id
ORDER BY amount DESC;

-- 1.1 数据修改 CTE：WITH 里可以直接 UPDATE/DELETE 再 RETURNING（PG 特色）
WITH deleted AS (
    DELETE FROM products WHERE stock = 0 RETURNING *
)
SELECT count(*) AS deleted_count FROM deleted;
-- 若返回 0，可先执行：UPDATE products SET stock = 0 WHERE id = 8; 再跑上面

-- ========== 2. 递归 CTE（树形结构 / 序列） ==========
-- MySQL 8 也有 RECURSIVE，但 PG 支持更早

WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 10
)
SELECT n FROM seq;

-- 典型场景：组织架构树、评论楼、BOM 展开。
-- 思路：初始行（顶层）+ 递归步（JOIN 自己的子节点），注意必须有终止条件防死循环

-- ========== 3. 窗口函数（团队高频，报表必用） ==========
-- 与 GROUP BY 不同：窗口不折叠行，每行都保留，同时能看到"分组内"的聚合

-- 3.1 ROW_NUMBER：每个用户的订单按时间倒序编号（取每组 Top N 的经典写法）
SELECT id, user_id, total,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
FROM orders
ORDER BY user_id, rn;

-- 3.2 LAG / LEAD：和"上一个订单"比较（环比）
SELECT id, user_id, total, created_at::date,
       LAG(total) OVER (PARTITION BY user_id ORDER BY created_at) AS prev_total,
       total - LAG(total) OVER (PARTITION BY user_id ORDER BY created_at) AS diff
FROM orders
ORDER BY user_id, created_at;

-- 3.3 SUM OVER：累计金额（running total）
SELECT id, user_id, total,
       SUM(total) OVER (PARTITION BY user_id ORDER BY created_at) AS cum_total
FROM orders
ORDER BY user_id, created_at;

-- 3.4 RANK / DENSE_RANK：并列排名（RANK 跳号，DENSE_RANK 不跳号）
SELECT id, user_id, total,
       RANK()       OVER (PARTITION BY user_id ORDER BY total DESC) AS rk,
       DENSE_RANK() OVER (PARTITION BY user_id ORDER BY total DESC) AS drk
FROM orders;

-- ========== 4. 分组集：GROUPING SETS / ROLLUP / CUBE ==========
-- 一次查出多个维度的汇总（MySQL 8 也支持）

SELECT user_id, status, count(*) AS cnt
FROM orders
GROUP BY GROUPING SETS ((user_id), (status), ())
ORDER BY user_id NULLS FIRST, status NULLS FIRST;

-- ROLLUP：逐层汇总（每个 user_id 的小计 + 总计）
SELECT user_id, count(*) AS cnt
FROM orders
GROUP BY ROLLUP (user_id)
ORDER BY user_id NULLS LAST;

-- ========== 5. 全文检索（vs MySQL FULLTEXT + MATCH...AGAINST） ==========
-- PG 用 tsvector（词向量）+ tsquery（查询词）+ @@ 匹配，配合 GIN 索引

-- 5.1 看看词向量长什么样
SELECT to_tsvector('english', description) FROM products WHERE id = 1;

-- 5.2 搜索（to_tsquery 支持 & | ! 组合，如 'keyboard & wireless'）
SELECT id, name FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'keyboard');

-- 5.3 建 GIN 索引加速（大表必须）
CREATE INDEX IF NOT EXISTS idx_products_fts ON products
    USING GIN (to_tsvector('english', description));

EXPLAIN ANALYZE
SELECT id, name FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'keyboard');

-- 5.4 相关性排序 ts_rank
SELECT id, name,
       ts_rank(to_tsvector('english', description), to_tsquery('english', 'keyboard')) AS rank
FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'keyboard')
ORDER BY rank DESC;

-- 注意：中文分词需要扩展（zhparser 等），生产环境常用；英文内置即用

-- ========== 6. 物化视图（MySQL 没有！PG 独有） ==========
-- 普通视图每次查都执行 SQL；物化视图把结果"存下来"，适合昂贵查询

CREATE MATERIALIZED VIEW mv_order_summary AS
SELECT user_id, status, count(*) AS cnt, sum(total) AS amount
FROM orders
GROUP BY user_id, status;

SELECT * FROM mv_order_summary;   -- 快照数据

-- 数据变化后需手动刷新（也可以建自动刷新的刷新调度）
REFRESH MATERIALIZED VIEW mv_order_summary;

-- 用完清理
DROP MATERIALIZED VIEW IF EXISTS mv_order_summary;

-- ========== 7. 分区表（PG 原生支持 RANGE / LIST / HASH） ==========
-- 大数据量按时间/地域拆分，查询自动路由到对应分区

CREATE TABLE IF NOT EXISTS events (
    id          BIGINT GENERATED ALWAYS AS IDENTITY,
    event_name  TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (occurred_at);   -- 按时间范围分区

CREATE TABLE IF NOT EXISTS events_2025 PARTITION OF events
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS events_2026 PARTITION OF events
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

INSERT INTO events (event_name, occurred_at) VALUES
('login',    '2025-06-01 10:00:00+08'),   -- 进 2025 分区
('checkout', '2026-02-01 12:00:00+08');   -- 进 2026 分区

SELECT tableoid::regclass AS partition, event_name, occurred_at FROM events;  -- 看落在哪个分区
SELECT count(*) FROM events_2025;   -- 1

-- 清理演示数据
DROP TABLE IF EXISTS events CASCADE;

-- ========== 8. 常用扩展 ==========

-- 8.1 UUID：gen_random_uuid()（PG 13+ 内置；MySQL 用 UUID()）
CREATE EXTENSION IF NOT EXISTS pgcrypto;
SELECT gen_random_uuid();
-- 用法：id UUID DEFAULT gen_random_uuid() 做主键，分布式系统常用

-- 8.2 citext：大小写不敏感的文本类型（对应 MySQL 的 utf8mb4_*_ci 排序规则）
CREATE EXTENSION IF NOT EXISTS citext;
SELECT 'Hello'::citext = 'hello'::citext;   -- true

-- 8.3 查看已安装扩展
\dx

-- ========== 9. EXPLAIN 分析执行计划 ==========
EXPLAIN SELECT * FROM products WHERE id = 1;                    -- 只出计划，不执行
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 1;         -- 真实执行，看耗时
EXPLAIN ANALYZE
SELECT o.*, u.name FROM orders o JOIN users u ON u.id = o.user_id;

-- 关键看点：
--   * Seq Scan = 全表扫描（慢）→ Bitmap/Index Scan = 走索引
--   * 观察 "actual time" 与实际行数估计的偏差
--   * 顺序：从最内层往外读

-- ========== 10. 生产团队常配的 psql 技巧 ==========

-- 10.1 \x 宽表转竖排
\x
SELECT * FROM users WHERE id = 1;
\x

-- 10.2 \timing 看每条 SQL 耗时
\timing
SELECT count(*) FROM orders;
\timing

-- 10.3 \d 系列速查
-- \d users         表结构
-- \di             索引列表
-- \dv / \dm       视图 / 物化视图
-- \d+ users       带更多细节（存储参数、注释）
