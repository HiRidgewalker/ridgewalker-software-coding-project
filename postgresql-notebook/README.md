# Learning PostgreSQL Notebook

基于 Docker 中的 PostgreSQL 16 容器（`postgresql`，端口 5432），通过**终端 psql** 学习 PostgreSQL 核心特性。

## 连接数据库

```bash
# 方式一：进入容器执行 psql
docker exec -it postgresql psql -U postgres

# 方式二：项目脚本（直接进 learning_shop 库）
./connect.sh
```

- 用户：`postgres` / 密码：`change-me`
- 数据卷：`D:\DockerWorkspace\volume\postgresql`

## 学习路径

| 文件 | 主题 | vs MySQL 核心差异 |
|---|---|---|
| `sql/01_create_db.sql` | 创建/删除数据库 + psql 元命令 | 语法基本相同 |
| `sql/02_schema.sql` | 建表：类型/约束/枚举/自增 | AUTO_INCREMENT → IDENTITY；DECIMAL → NUMERIC |
| `sql/03_crud.sql` | 增删改查 + 事务 + RETURNING | RETURNING / ON CONFLICT / FROM & USING 子句 |
| `sql/04_array.sql` | **数组类型**（list） | **MySQL 没有数组** |
| `sql/05_jsonb.sql` | **json / jsonb** | MySQL 只有 JSON，无 jsonb / @> 操作符 |
| `sql/06_advanced.sql` | CTE/窗口函数/全文检索/物化视图/分区表/扩展 | 物化视图、GIN 索引等为 PG 独有 |
| `notes/postgres-features.md` | 特性速查 + MySQL 对比笔记 | — |

## 执行方式

```bash
# 整文件执行（文件内部已按小节组织）
docker exec -i postgresql psql -U postgres -d learning_shop < sql/03_crud.sql

# 交互式逐段粘贴（推荐，学习效果更好）
docker exec -it postgresql psql -U postgres -d learning_shop
```

## 建议流程

1. 先执行 `sql/01_create_db.sql` 建库（learning_shop）
2. 再执行 `sql/02_schema.sql` 建表 + 种子数据
3. 之后每个文件按注释小节逐步执行：**先猜结果，再执行对照**
4. 文件故意包含少量"会报错的示例"，注释里已标明，用于理解语法边界

## 数据模型（电商）

```
users    用户    tags TEXT[]（标签数组）、profile JSONB（个人资料）
products 商品    attributes JSONB（属性）、description TEXT（全文检索）
orders   订单    items JSONB（商品明细数组）、status ENUM（状态枚举）
```
