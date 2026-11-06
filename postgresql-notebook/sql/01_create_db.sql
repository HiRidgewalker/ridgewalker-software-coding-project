-- ============================================================================
-- 01. 创建数据库
-- 目标：体验 CREATE DATABASE / DROP DATABASE 和常用 psql 元命令
-- 执行：交互式粘贴，或整文件执行（连接默认库 app）：
--   docker exec -i postgresql psql -U postgres -d app < sql/01_create_db.sql
-- ============================================================================

-- 1. 查看当前有哪些数据库（元命令 \l，等价 \list）
\l

-- 2. 查看当前连接信息
\conninfo

-- 3. 删除旧库（如果之前练习建过）。WITH (FORCE) 会强制断开占用连接（PG 13+）
DROP DATABASE IF EXISTS learning_shop WITH (FORCE);

-- 4. 创建数据库
--    注意：CREATE DATABASE 不能写在事务块里；psql 默认每条语句自动提交，所以没问题
CREATE DATABASE learning_shop;

-- 5. 切换到新库（psql 元命令，等价于重新连接）
\c learning_shop

-- 6. 确认当前库（应显示 learning_shop）
SELECT current_database(), current_user;

-- 7. 查看当前库里的表（现在应该为空，Nothing found）
\dt

-- 8. 常用 psql 元命令速查（学习全程会用到）：
--    \l            列出所有数据库
--    \dt           列出当前库所有表
--    \d 表名       查看表结构（列/索引/约束/默认值）
--    \di           列出索引
--    \dv / \dm     视图 / 物化视图
--    \dx           已安装扩展
--    \x            行转列显示（结果宽时切换）
--    \timing       显示每条 SQL 执行耗时
--    \i 文件名     执行 SQL 文件（如 \i sql/03_crud.sql）
--    \q            退出
