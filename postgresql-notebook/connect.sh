#!/usr/bin/env bash
# 连接 learning_shop 库（先执行 sql/01_create_db.sql 建库）
# 用法: ./connect.sh  [psql 参数]
docker exec -it postgresql psql -U postgres -d learning_shop "$@"
