---
name: fastapi-project-rules
description: "新建 FastAPI 项目骨架、在既有 FastAPI 项目中新增或修改接口、编写 controller 与 service 与 dao 与 schema 与 client 分层代码、装配 app 与 CORS 与全局异常处理器、组织路由与依赖注入与数据库会话、审查 FastAPI 目录结构与分层实现时触发。"
disable-model-invocation: false
---

# FastAPI 项目编码规则

以下规则为强制约束，逐条执行。

## 目录与分层

1. 新建项目时，应用入口只用工作区根目录的 `main.py`，业务代码全部放进 `src/`。

2. `src/` 下只建 `controller`、`service`、`dao`、`model`、`schema`、`core`、`client`、`util` 八个包，包内按业务域拆模块文件。

3. 模块文件名用「业务域 + 层名」的小写下划线形式。

   > 示例：`user_controller.py`、`user_service.py`、`user_dao.py`、`user_model.py`。

4. 调用方向只允许 `controller → service → dao / client / util`；禁止下层模块反向导入上层模块。

5. `controller` 需要数据时，在对应 Service 上补一个方法转发；禁止 `controller` 导入并调用 DAO。

6. `model` 只放 SQLAlchemy ORM 映射类，`schema` 只放 Pydantic 模型；禁止一个类同时承担持久化映射与请求响应校验。

7. `core` 只放常量、异常类、配置类与全局异常处理器这类无业务语义的基础设施代码。

8. 只有用户明确要求按子应用拆分时才建 `src/subapp/`；未提出时禁止创建该目录。

9. 建 `src/subapp/<app_name>/` 时在其内部复刻主 app 的分层目录，且禁止在子应用内再嵌套 `subapp`。

## 配置

10. 配置值只从工作区根目录的 `.env` 读取；禁止在业务模块中调用 `os.getenv` 或另建配置文件。

11. 全局配置用一个继承 `BaseSettings` 的类表达，每个字段声明类型与默认值，并用 `model_config = SettingsConfigDict(env_file=".env")` 绑定文件。

12. 配置类所在文件末尾必须实例化一个模块级单例，用到配置的模块导入该单例并直接读属性。

    > 示例：
    >
    > ```python
    > settings = Settings()                        # 配置文件末尾
    > timeout = settings.redis_timeout_seconds     # 用
    > timeout = Settings().redis_timeout_seconds   # 禁止：每次重新解析 .env
    > ```

13. 配置只以导入单例的方式获取；禁止把配置对象做成 `Depends` 依赖或逐层当参数传递。

14. 凭据只写进 `.env`，同时在 `.env.example` 补同名空值键与一行用途注释，并确认 `.gitignore` 已忽略 `.env`。

15. 禁止在 FastAPI 实例的 `app.state` 上挂载任何属性；客户端、配置与共享对象改由各自模块的单例持有。

## 应用装配

16. `main.py` 只做四件事：实例化 `FastAPI`、注册中间件、注册路由、注册异常处理器；禁止在其中写端点与业务逻辑。

17. 路由只用 `app.include_router()` 挂载 `src/controller/router.py` 汇总出的总路由。

18. 必须显式注册 `CORSMiddleware`，`allow_origins`、`allow_methods`、`allow_headers` 逐项从配置单例读取；禁止硬编码 `["*"]`。

19. 进程启停时需要初始化或释放的资源用 `lifespan` 异步上下文管理器处理；禁止用已废弃的 `@app.on_event`。

20. `lifespan` 中只调用各 client 模块自身的初始化与关闭函数；禁止在其中构造对象再挂到 `app` 上。

## Controller 与路由

21. 每个 controller 模块必须在模块级定义 `router = APIRouter(prefix=..., tags=[...])`；禁止把 `APIRouter` 放进类属性或实例属性。

22. 同一业务域的端点必须收进一个以该业务域命名的 Controller 类，该类只作命名空间。

23. 端点方法一律用 `@staticmethod`，且 `@staticmethod` 写在 `@router.<method>` 上方。

    > 示例：
    >
    > ```python
    > @staticmethod                              # 用
    > @router.get("/{user_id}")
    > async def get_user(user_id: int, db_session: DBSessionDependency) -> ResponseSchema[UserRead]: ...
    >
    > @router.get("/{user_id}")                  # 禁止：装饰器顺序颠倒导致注册失败
    > @staticmethod
    > ```

24. `Controller` 方法只允许通过类名访问；禁止实例化 `Controller` 类或为它定义 `__init__`、实例属性与类属性依赖。

25. 每个 `Controller` 端点必须固定注入 `db_session: DBSessionDependency`，会话依赖类型别名只用 `DBSessionDependency`；禁止用 `SessionDep` 等缩写。

26. `Controller` 必须在模块顶部导入并直接调用 `Service`；禁止把 `Service` 声明为 `Depends` 依赖。

27. `Controller` 必须按接口实际需要声明路径参数、查询参数、表单、请求体、请求头和用户校验依赖，并在调用 `Service` 时显式传递 `db_session` 与接口参数。

    > 示例：
    >
    > ```python
    > from src.service.user_service import UserService
    >
    > async def get_user(user_id: int, db_session: DBSessionDependency) -> ResponseSchema[UserRead]:
    >     user = await UserService.get_user(db_session=db_session, user_id=user_id)
    >     return ResponseSchema[UserRead](code=200, msg="成功", data=user)
    > ```

28. 端点函数体禁止出现业务条件分支、循环与 `ORM` 调用；这类逻辑必须下沉到 `Service`。

29. 端点一律用 `async def` 定义。

30. `src/controller/router.py` 只做汇总：建一个总 `APIRouter`，逐个 `include_router` 各业务 controller 的 `router`。

31. 统一 URL 前缀与版本号在 `router.py` 的总路由上用 `prefix` 声明；禁止在每个 controller 的 `prefix` 里重复拼接。

## Schema 与响应

32. 请求体与业务响应数据只用 `schema/` 下的 `Pydantic` 模型表达，按用途拆成 `XxxCreate`、`XxxUpdate`、`XxxRead`。

33. 所有端点必须用函数返回类型注解声明 `ResponseSchema[业务 Schema]`；禁止改用装饰器的 `response_model` 参数。

34. 统一响应模型只用 `schema/` 下的泛型 `Pydantic` 模型 `ResponseSchema`，字段固定为 `code: int`、`msg: str` 与泛型 `data`。

35. 普通端点必须由 `Controller` 将业务结果包装为 `ResponseSchema` 并直接返回，交由 `FastAPI` 序列化；禁止自定义 `JSONResponse` 子类，异常响应只用框架提供的 `JSONResponse`。

36. `Service` 只允许返回业务 `Schema`，取得 `ORM` 对象时必须用 `XxxRead.model_validate(obj)` 转换；禁止返回 `ResponseSchema`，响应包装必须交给 `Controller`。

37. `ResponseSchema.code` 必须与实际 `HTTP` 状态码一致，非 `200` 的成功状态码必须用路由装饰器的 `status_code` 参数声明；禁止在端点函数体内手工构造 `Response` 改状态码。

38. `Schema` 类只允许字段定义与字段校验器；禁止在其中写业务方法与数据库访问，这类逻辑必须分别放入 `Service` 与 `DAO`。

## Service 与 DAO

39. 业务规则、流程编排与状态判定只允许写在 `Service` 中，`Service` 方法必须用 `async def` 定义。

40. `Service` 类只用作无状态命名空间，方法必须用 `@staticmethod` 并显式接收 `db_session: AsyncSession` 与业务参数；禁止通过构造函数装配 `Service` 或创建 `Service` 依赖提供函数。

41. `Service` 必须在模块顶部导入并直接调用所需的 `DAO`、`client` 或 `util`；禁止在方法内部导入或构造这些协作者。

42. 数据库引擎、`async_sessionmaker` 与会话依赖函数只允许定义在 `src/client/` 的数据库模块中。

43. 会话依赖只允许提供带事务的一种，用 `async_sessionmaker.begin()` 产出会话并导出 `DBSessionDependency` 这个 `Annotated` 别名；禁止再提供不带事务的会话依赖。

    > 示例：
    >
    > ```python
    > async def get_transaction_session() -> AsyncGenerator[AsyncSession, None]:
    >     async with async_session.begin() as db_session:
    >         yield db_session
    >
    > DBSessionDependency = Annotated[AsyncSession, Depends(get_transaction_session)]
    > ```

44. `Service` 与 `DAO` 需要会话时必须复用 `Controller` 传入的同一个 `db_session`；禁止在 `Service` 与 `DAO` 内部自行创建会话。

45. `SQLAlchemy` 语句只允许在 `DAO` 中构造与执行，访问数据库的 `DAO` 方法必须显式接收 `db_session: AsyncSession` 与基本参数；不访问数据库的 `DAO` 方法必须按实际需要声明参数，不强制接收 `db_session`。

46. 事务提交与回滚必须由会话依赖的 `begin()` 上下文统一处理；禁止在 `DAO` 与 `Service` 中调用 `db_session.commit()` 与 `db_session.rollback()`。

47. `DAO` 只允许返回 `ORM` 对象或标量，禁止导入 `schema`、`service` 或返回 `Pydantic` 模型；业务数据转换必须由 `Service` 完成。

## Client 与 Util

48. 数据库、缓存、向量库与第三方 HTTP 服务的连接和调用一律封装在 `src/client/` 下，一个外部依赖一个模块。

49. client 对外暴露的方法只返回项目自己的数据结构；禁止让调用方感知第三方 SDK 的模型类型与异常类型。

50. `util/` 只放与业务无关的纯函数和数据结构转换；禁止在其中访问数据库、发起网络请求与读取配置单例。

## 异常与日志

51. 项目自定义异常类必须以 `Exception` 结尾并统一定义在 `src/core/` 的异常模块中，业务异常必须继承同一个项目基础异常类。

52. 项目基础异常必须包含 `code: int`、`message: str` 和 `data`，未传入 `data` 时必须为每个异常实例创建独立的空字典。

53. 项目异常的 `code` 必须直接用作 `HTTP` 状态码，常用错误类别只用 `src/core/constants.py` 中复用的整数常量；禁止为细微业务场景新增错误码，差异只用 `message` 与 `data` 表达。

54. `DAO` 捕获 `SQLAlchemyError`、`client` 捕获第三方 `SDK` 异常后，必须转换成项目异常并用 `raise ... from exc` 向上抛出。

55. `Service` 只允许抛出业务异常与为底层异常补充业务上下文；禁止吞掉异常后返回 `None` 或默认值。

56. `Controller` 禁止用 `try/except` 捕获业务异常或手工转换成 `HTTPException`；异常必须交给全局异常处理器。

57. 全局异常处理器必须在 `src/core/` 中定义并在 `main.py` 注册，覆盖项目基础异常、`starlette.exceptions.HTTPException`、`RequestValidationError` 和未知 `Exception`，所有异常响应必须统一为 `ResponseSchema`。

58. 构造异常响应时，项目异常必须将 `message` 与 `data` 分别填入响应的 `msg` 与 `data`；`HTTPException` 必须沿用其 `status_code` 并保留 `headers`；请求字段校验异常必须用对应 `422` 的常量；未知异常必须用对应 `500` 的常量及通用错误消息。

59. 请求字段校验异常的响应数据只允许包含每项错误的字段位置 `loc`、错误原因 `msg` 和错误类型 `type`；禁止返回原始输入值或直接返回完整的 `exc.errors()`、`exc.body`，必须逐项提取这三个字段。

60. 异常处理器必须先构造 `ResponseSchema`，再用 `model_dump(mode="json")` 的结果作为 `JSONResponse.content`，并将响应的 `code` 用作 `JSONResponse.status_code`，包含嵌套 `datetime` 的数据也必须经此转换。

    > 示例：
    >
    > ```python
    > response = ResponseSchema(code=exc.code, msg=exc.message, data=exc.data)
    > return JSONResponse(status_code=response.code, content=response.model_dump(mode="json"))
    > ```

61. 未知异常用 `logger.exception` 记 `ERROR`；已定义的业务异常按业务语义记 `INFO` 或 `WARNING`，禁止一律记成 `ERROR`。

62. 同一异常调用链只允许在全局异常处理器中记录一次异常日志；`DAO`、`client`、`Service`、`Controller` 中禁止出现 `logger.error` 与 `logger.exception`。

    > 示例：
    >
    > ```python
    > except SQLAlchemyError as exc:
    >     logger.exception("query user failed")              # 禁止：边界会再记一次
    >     raise DatabaseException(code=INTERNAL_SERVER_ERROR, message="query user failed") from exc  # 用
    > ```

63. 正常日志只在 Service 中按有业务价值的事件记 `INFO`；禁止记录方法进出、每次查询成功与局部变量状态。

64. 日志上下文一律用 `extra` 传结构化字段，禁止用 f-string 拼接；禁止写入密钥、令牌与完整敏感请求体。

    > 示例：
    >
    > ```python
    > logger.info(f"user {user_id} created")                    # 禁止
    > logger.info("user created", extra={"user_id": user_id})   # 用
    > ```

65. 访问日志用一个中间件统一记录 `method`、`path`、`status_code`、`duration_ms`；禁止在端点内逐个记录请求信息。
