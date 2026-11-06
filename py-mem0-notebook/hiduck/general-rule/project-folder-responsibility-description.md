# 项目目录职责规则

以下规则为强制约束，逐条执行。本文件规定目录职责与文件归属，FastAPI 编码细节遵循 [fastapi-project-rules](../../.agents/skills/fastapi-project-rules/SKILL.md)。

## 根目录与目录结构

FOLDER-1. 应用入口使用工作区根目录的 `main.py`，只负责实例化 `FastAPI`、注册中间件、注册总路由与注册异常处理器；业务代码全部放进 `src/`。

FOLDER-2. `src/` 默认只使用 `controller`、`service`、`dao`、`model`、`schema`、`core`、`client`、`util` 八个分层包。新增功能先确定所属层，不另建 `api`、`common`、`helper`、`repository` 等平行职责目录。

FOLDER-3. 根目录的 `alembic/` 存放数据库迁移环境与迁移脚本，`alembic/versions/` 存放版本迁移文件；ORM 映射仍放在 `src/model/`。`hiduck/general-rules/` 存放 agent 通用规则，`hiduck/doc/` 存放项目使用文档，`.agents/skills/` 存放技能及其配套资源。

## 各层职责

下表中的文件名来自当前项目，用于定位职责，不代表现有实现的所有细节都应照搬。

| 目录 | 应放内容 | 当前文件示例 |
| --- | --- | --- |
| `src/controller/` | HTTP 接口、参数与依赖注入、统一响应包装、路由汇总 | `health_controller.py`、`router.py` |
| `src/service/` | 业务规则、流程编排、状态判定、业务 Schema 转换 | `health_service.py` |
| `src/dao/` | SQL 构造与执行、持久化数据访问 | `health_dao.py` |
| `src/model/` | SQLAlchemy ORM 映射类及其基类 | `base_model.py` |
| `src/schema/` | Pydantic 请求与响应模型、字段校验、统一响应结构 | `health_schema.py`、`response_schema.py` |
| `src/core/` | 配置、常量、异常、全局异常处理、应用生命周期、访问日志中间件 | `config.py`、`exception_handler.py`、`lifespan.py`、`access_log_middleware.py` |
| `src/client/` | 外部依赖的连接与调用、资源初始化与关闭、数据库会话依赖 | `database_client.py` |
| `src/util/` | 可独立使用的日志、图片处理、数据转换等通用工具 | `log_util.py` |

FOLDER-4. `controller/` 按业务域定义接口，取得请求参数后交给对应 Service，并将业务 Schema 包装成 `ResponseSchema`。业务条件分支、循环与数据库操作不得放入 Controller。`controller/router.py` 只汇总各业务路由，并声明统一 URL 前缀与版本号。

FOLDER-5. `service/` 承担业务规则与流程编排，包括组合 DAO 查询、调用外部服务、使用通用工具、判断业务状态以及把 ORM 对象转换成业务 Schema。不得把这些逻辑放入 Controller、DAO、Schema 或 Util。

FOLDER-6. `dao/` 负责构造和执行 SQLAlchemy 语句，显式接收上层传入的数据库会话，返回 ORM 对象或标量；不得创建会话、提交或回滚事务，也不得返回 Pydantic 模型。数据库事务由会话依赖统一管理。

FOLDER-7. `model/` 只定义 SQLAlchemy ORM 映射及其基类，`schema/` 只定义 Pydantic 数据模型及字段校验。请求与响应模型按用途命名为 `XxxCreate`、`XxxUpdate`、`XxxRead`，统一响应定义在 `response_schema.py`。一个类不得同时承担 ORM 映射与接口字段校验，Schema 中不得包含业务流程或数据库访问。

FOLDER-8. `core/` 存放项目级基础设施，不承载业务流程。配置类与单例放在 `config.py`，公共常量放在 `constants.py`，项目异常统一放在 `exception.py`，全局异常处理放在 `exception_handler.py`。生命周期编排放在 `lifespan.py`，仅调用各 Client 自身的初始化与关闭函数；HTTP 访问日志中间件放在 `access_log_middleware.py`。`main.py` 负责将这些基础设施装配到应用。

FOLDER-9. `client/` 按外部依赖拆模块，封装数据库、缓存、向量库和第三方 HTTP 服务的连接、调用及资源释放。数据库引擎、会话工厂、会话依赖函数与 `DBSessionDependency` 统一放在 `database_client.py`；业务 SQL 放在 DAO。第三方服务调用结果与异常须在 Client 边界转换为项目自己的数据结构与异常。

## Util 的归属边界

FOLDER-10. `util/` 存放与具体业务、项目基本技术栈无强耦合且可独立使用的工具。工具可以依赖实现自身能力的通用库，但不依赖项目业务模型、数据库会话、Web 框架对象或配置单例；所需参数由调用方传入。

FOLDER-11. 工具以 class namespace 组织：类只作命名空间，工具方法使用 `@staticmethod`，调用时不实例化；数据转换函数也按所属工具类组织。工具不限定为纯函数，允许日志输出、图片读写等必要副作用。

FOLDER-12. 日志创建、格式化与输出封装归 `util/log_util.py`；图片坐标裁剪、EXIF 方向校正、格式转换等通用能力归 `util/image_util.py`。后者是新增图片工具时的目标路径，按实际需求创建。

FOLDER-13. 文件归属按实际职责判断，不因名称中包含“工具”就放入 `util/`。根据试题区域裁剪图片并提交批改的流程归 `service/`，其中可复用的坐标裁剪能力归 `util/`，调用外部识别服务的连接与请求归 `client/`。日志工具归 `util/`，依赖 HTTP 请求与响应的访问日志中间件归 `core/`。

FOLDER-14. 无法确定应放入 `util/` 还是其他职责目录时，可以向用户说明具体用途、依赖与候选归属后咨询。

## 文件命名与子目录

FOLDER-15. 各层默认按业务域平铺模块，业务模块使用“业务域 + 层名”的小写下划线名称，例如 `grading_controller.py`、`grading_service.py`、`grading_dao.py`、`grading_model.py`、`grading_schema.py`。Client 按外部依赖命名为 `xxx_client.py`，Util 按工具能力命名为 `xxx_util.py`。`router.py`、`config.py`、`constants.py`、`exception.py`、`exception_handler.py`、`lifespan.py`、`access_log_middleware.py` 等基础设施文件保留专用名称。

FOLDER-16. 只有实际功能需要拆分时才创建层内子包；子包必须继承父目录职责，文件仍遵守所属层的命名规则。例如 `service/grading/` 内只能组织该业务的 Service 实现，不得混放 Controller、DAO、ORM 或 Schema。不得预建空业务目录或空分层文件。

FOLDER-17. 只有用户明确要求按子应用拆分时，才允许创建 `src/subapp/<app_name>/`，在其内部复刻主应用的分层目录；禁止在子应用内再次嵌套 `subapp/`。

## 跨层调用与导入

FOLDER-18. Controller 将业务交给 Service，Service 调用 DAO、Client 与 Util。Controller 需要数据时，在对应 Service 上提供方法，不得直接调用 DAO 或 Client 执行业务；DAO 不得导入 Service 或 Schema，下层不得反向导入上层业务模块。

FOLDER-19. 业务调用限制不禁止必要的基础设施与类型导入。Controller 可以从数据库 Client 导入 `DBSessionDependency`、从 Schema 导入请求响应模型、从 Core 导入常量；全局异常处理器可以导入 `ResponseSchema`，生命周期模块可以导入 Client 初始化与关闭函数。此类导入不得成为跨层执行业务的入口。
