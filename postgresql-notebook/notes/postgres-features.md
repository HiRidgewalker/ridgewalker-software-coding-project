# PostgreSQL 特性速查（vs MySQL 对比笔记）

> 配套 SQL 练习：`sql/01_create_db.sql` ~ `sql/06_advanced.sql`（数据库：learning_shop）

## 1. 类型对比

| 需求 | PostgreSQL | MySQL | 说明 |
|---|---|---|---|
| 自增主键 | `BIGINT GENERATED ALWAYS AS IDENTITY` | `BIGINT AUTO_INCREMENT` | PG 还有旧写法 SERIAL，新项目用 IDENTITY |
| 整数 | `SMALLINT/INT/BIGINT` | 相同 | |
| 精确小数 | `NUMERIC(10,2)` | `DECIMAL(10,2)` | 等价 |
| 字符串 | `TEXT`（不限长） | `VARCHAR(n)` 有长度限制 | PG 的 TEXT 随便存 |
| 大小写不敏感 | `CITEXT`（扩展） | `utf8mb4_*_ci` 排序规则 | 见 sql/06 §8.2 |
| 时间戳 | `TIMESTAMPTZ`（UTC 存储） | `TIMESTAMP/DATETIME` | PG 推荐一律 TIMESTAMPTZ |
| **数组** | `TEXT[] / INT[] / ...` ✅ | **无** | 见 sql/04 |
| **JSON** | `json` / `jsonb`（两种） | `JSON`（一种） | 见 sql/05 |
| 枚举 | `CREATE TYPE ... AS ENUM`（独立类型） | `ENUM(...)`（列内嵌） | PG 可复用 |
| 金额 | `NUMERIC` | `DECIMAL` | |
| 区间 | `TSRANGE / DATERANGE` ✅ | 无 | 排期/价格区间 |
| UUID | `gen_random_uuid()` 内置 | `UUID()` | |
| 网络地址 | `INET / CIDR` ✅ | 无 | IP 存储+查询 |
| 几何 | `POINT / POLYGON` 等 ✅ | 无 | |

## 2. 数组（MySQL 无对应物）

- 字面量：`ARRAY['a','b']` 或 `'{a,b}'::text[]`
- **下标从 1 开始**：`tags[1]`
- 展开/聚合：`unnest(arr)` ↔ `array_agg(x)`
- 操作符：`@>` 包含、`<@` 被包含、`&&` 交集、`||` 拼接、`-` 移除
- 条件：`'vip' = ANY(tags)`、`3 = ALL(arr)`
- 常用函数：`cardinality`、`array_length`、`array_append`、`array_remove`、`string_to_array`、`array_to_string`
- MySQL 替代方案：逗号字符串（无类型安全）/ JSON / 关联表（重），都不如数组顺手

## 3. json vs jsonb（MySQL 只有 JSON）

| 维度 | `json` | `jsonb`（业务首选） |
|---|---|---|
| 存储 | 原文保存（含空白/重复键/键序） | 解析后二进制（键重排、去重、去空白） |
| 等值比较 | ❌ | ✅ |
| 索引 | ❌ | ✅ GIN 索引 |
| 写入速度 | 快（不解析） | 稍慢（要解析） |
| 查询/更新 | 慢 | 快 |

**操作符速查**（jsonb）：

| 操作符 | 含义 | MySQL 对应 |
|---|---|---|
| `->` | 取键，返回 jsonb | `->` |
| `->>` | 取键，返回 text | `->>` |
| `#>` / `#>>` | 路径访问 | `JSON_EXTRACT` |
| `@>` | 包含（值过滤） | `JSON_CONTAINS` |
| `?` / `?\|` / `?&` | 键存在判断 | 无直接对应 |
| `\|\|` | 拼接 | `JSON_MERGE_PRESERVE` |
| `-` | 删除键 | `JSON_REMOVE` |
| `jsonb_set` | 修改键 | `JSON_SET` |
| `jsonb_array_elements` | 数组展开为行 | `JSON_TABLE` |
| `jsonb_each` | 键值对展开 | 无 |

关键场景：`WHERE attrs @> '{"brand":"Apple"}'` + GIN 索引 = 灵活的属性查询（MySQL 8 需对生成列建索引）。

## 4. SQL 语法差异

| 能力 | PostgreSQL | MySQL |
|---|---|---|
| `RETURNING` | ✅ INSERT/UPDATE/DELETE 都有 | ❌ |
| 冲突处理 | `ON CONFLICT (key) DO UPDATE/NOTHING` | `ON DUPLICATE KEY UPDATE` |
| 多表更新 | `UPDATE t SET ... FROM t2 WHERE ...` | `UPDATE t JOIN t2 ...` |
| 多表删除 | `DELETE FROM t USING t2 WHERE ...` | `DELETE t FROM t JOIN t2 ...` |
| NULL 排序 | `ORDER BY x NULLS FIRST/LAST` | 不支持，NULL 固定最前 |
| 取每组第一条 | `DISTINCT ON (col)` | 无，子查询模拟 |
| 大小写不敏感匹配 | `ILIKE`、`~*` 正则 | `LIKE` + collation 或 `LOWER()` |
| 行值比较 | `(a,b) = (1,2)` | ❌ |
| 单引号转义 | `''` 或 `E'...'` | `''` 或 `\'` |

## 5. 索引

| 类型 | 用途 | MySQL 对应 |
|---|---|---|
| B-tree | 默认，等值/范围 | 同 |
| **GIN** | jsonb `@>`、数组包含、全文检索 | 无（8.0 有倒排索引，弱） |
| GiST | 几何/全文/范围 | 无 |
| BRIN | 超大表按物理顺序的列 | 无 |
| 部分索引 | `WHERE status='active'` 的局部索引 | 无 |
| 表达式索引 | `ON lower(email)` | 8.0+ 支持生成列 |

## 6. 高级特性

| 特性 | PostgreSQL | MySQL |
|---|---|---|
| 窗口函数 | ✅ 强（FILTER、帧定义丰富） | ✅ 8.0+（较弱） |
| CTE / 递归 CTE | ✅ | ✅ 8.0+（不能用于 UPDATE/DELETE） |
| 数据修改 CTE | ✅ `WITH d AS (DELETE ... RETURNING *)` | ❌ |
| GROUPING SETS / ROLLUP / CUBE | ✅ | ✅ 8.0+ |
| **物化视图** | ✅ `MATERIALIZED VIEW` | ❌（8.0 有索引视图，限制多） |
| 分区表 | ✅ RANGE/LIST/HASH，原生成熟 | ✅ 8.0+（早期版本较弱） |
| 全文检索 | ✅ `tsvector/tsquery` + GIN（中文需 zhparser 扩展） | ✅ FULLTEXT（中文需 ngram 插件） |
| 扩展生态 | ✅ `CREATE EXTENSION`（pgcrypto/citext/postgis/uuid-ossp...） | ❌ 无此机制（有 plugin 但弱） |
| 序列 | `SEQUENCE` 独立对象，可多表共享 | 无独立序列 |
| 触发器 | ✅ 函数化（PL/pgSQL） | ✅（过程式） |
| 复制 | 逻辑复制/流复制，成熟 | 主从/组复制 |

## 7. 事务与并发

- 隔离级别：Read Committed（默认）/ Repeatable Read / Serializable / Read Uncommitted（可用但等同 RC）
- MVCC 实现不同：PG 用元组多版本（旧版本留在页面，VACUUM 回收）；MySQL 用 undo log
- 无"幻读"问题的方式不同：PG 靠快照/SSI，MySQL 靠间隙锁
- `SELECT ... FOR UPDATE / FOR SHARE` 两边都有
- PG 无 `INSERT ... IGNORE`、无 `REPLACE INTO`（用 ON CONFLICT 代替）

## 8. 运维 / 工具差异

| 项目 | PostgreSQL | MySQL |
|---|---|---|
| 客户端 | `psql`（元命令 \d \dt \l \x \timing 强） | `mysql`（\G 等） |
| 数据库 = schema | 一个实例多 database，database 内多 schema | database 即 schema |
| 大小写敏感 | 标识符大小写敏感（建议全小写） | 表名与系统相关 |
| 备份 | `pg_dump / pg_restore` | `mysqldump` |
| 配置热加载 | `SELECT pg_reload_conf()` | 无（需重启或 SET PERSIST） |
| 查询分析 | `EXPLAIN (ANALYZE, BUFFERS)` 信息极丰富 | `EXPLAIN ANALYZE` |

## 9. 给团队的建议（PG 常见实践）

1. 主键用 `BIGINT IDENTITY` 或 `UUID`（分布式）；时间列用 `TIMESTAMPTZ`
2. 非结构化/多态属性用 `JSONB` + GIN 索引，别建一堆可空列
3. 标签/ID 集合用 `TEXT[]` + GIN，别用逗号字符串
4. 报表/昂贵查询用**物化视图**（注意刷新策略）
5. 大表按时间**分区** + BRIN 索引，天然利于归档
6. 全文检索数据量大用 **zhparser/zhongwen 扩展**（中文），否则 `LIKE '%x%'` 兜底
7. 常用扩展：`pgcrypto`（UUID/加密）、`citext`、`postgis`（地理）、`pg_stat_statements`（慢查询）
8. 注意 `VACUUM`/`autovacuum` 是日常，别关；大事务会拖慢它
9. 多用 `EXPLAIN (ANALYZE, BUFFERS)` 看执行计划，索引不是越多越好
10. 应用层连接池：PG 每个连接开销大，必须用 PgBouncer 之类的池
