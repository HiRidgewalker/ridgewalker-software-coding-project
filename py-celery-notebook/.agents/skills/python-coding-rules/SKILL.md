---
name: python-coding-rules
description: 编写、修改、重构或审查 Python 源代码时遵守的强制规则，覆盖语言版本、语法克制、代码组织、命名、类型注解、外部依赖隔离、异常设计、文档与入口文件。
disable-model-invocation: false
---

# Python 编码规则

以下规则为强制约束，逐条执行。

## 语言版本

1. 目标运行环境固定为 Python 3.10 及以上；只写 3.10+ 语法，禁止为 3.9 及更低版本做任何兼容处理。

   > 禁止：`from __future__ import annotations`、`sys.version_info` 版本分支、`try/except ImportError` 条件导入、`typing.List` 等旧别名。

2. 3.10+ 提供的语法直接使用，不用旧写法替代。

   > 示例：
   > ```python
   > def parse(raw: str | None) -> list[int]: ...   # 用；禁止 Optional[str] / List[int]
   >
   > match status:                                  # 分支多时用 match
   >     case "pending": ...
   >     case "done": ...
   >
   > @dataclass(slots=True, kw_only=True)           # 3.10 起可用
   > class OCRResult: ...
   > ```

## 语法克制

3. 用 Python 内置语法和标准库的常见写法完成任务；同等效果下选阅读者无需查文档就能看懂的那一种。

4. 禁止元类、描述符协议、运行时动态建类、动态代码执行和动态属性注入；用显式的类定义、`property` 和普通方法替代。

   > 禁止：`class C(metaclass=M)`、`__get__` / `__set__`、`type("C", (), {})`、`exec` / `eval`、`setattr` 与 `__getattr__` 注入属性。

5. 推导式只允许单层且最多带一个 `if`；出现嵌套循环、嵌套条件或副作用时改用显式 `for`。

   > 示例：
   > ```python
   > [f(x) for row in rows for x in row if x and g(x)]   # 禁止
   > result = [f(x) for x in flatten(rows) if x]         # 用
   > ```

6. 单个表达式内的链式调用与运算不超过三段；超出时拆成带名字的中间变量。

   > 示例：
   > ```python
   > return sorted({x.strip().lower() for x in raw.split(",") if x}, key=len)[:5]  # 禁止
   > ```

7. 禁止为压缩行数牺牲可读性的写法：链式条件表达式、用 `:=` 承载分支逻辑、分号连写多条语句；改用独立语句或带名字的中间变量。

   > 示例：
   > ```python
   > level = "high" if s > 8 else "mid" if s > 4 else "low"   # 禁止
   > ```

8. 装饰器嵌套不超过两层，嵌套函数与闭包只用于装饰器内部；主流程逻辑放在模块级函数或类方法中。

## 代码组织

9. 默认用类组织代码；模块级散落函数只允许出现在入口文件和单一职责的小模块中。

10. 行为依赖可变状态、配置或协作者时，用实例方法。

11. 行为无状态但作用于类型本身，或用作替代构造函数时，用 `@classmethod`。

   > 示例：
   > ```python
   > class Config:
   >     @classmethod
   >     def from_env(cls) -> "Config":
   >         return cls(api_key=os.environ["API_KEY"])
   > ```

12. 一组无状态工具函数用类作命名空间聚合，以 `@staticmethod` 暴露。

   > 示例：
   > ```python
   > class TextUtils:
   >     @staticmethod
   >     def normalize(text: str) -> str: ...
   >
   > TextUtils.normalize(raw)   # 调用带明确前缀
   > ```

13. 类命名空间必须聚焦单一主题；禁止创建 `Utils`、`Helpers`、`Common` 这类无边界杂烩类。

   > 反例：`class Utils` 里同时放 `parse_date`、`send_email`、`resize_image`。
   > 正例：拆成 `DateUtils`、`EmailClient`、`ImageUtils` 三个各自聚焦的类。

14. 纯数据结构只用 `dataclass`；固定取值集合只用 `Enum`；项目已使用 Pydantic 且处于数据校验边界时用 `BaseModel`。禁止 `NamedTuple`、`TypedDict` 和手写只存数据的类。

   > 示例：
   > ```python
   > @dataclass(frozen=True)
   > class OCRResult:
   >     text: str
   >     confidence: float
   >
   > class TaskStatus(Enum):
   >     PENDING = "pending"
   >     DONE = "done"
   > ```

15. 优先用组合；继承只用于明确且稳定的"属于"关系。

16. 需要多态或可替换实现时，只用 `abc.ABC` + `@abstractmethod` 定义抽象基类。禁止使用 `Protocol`。

    > 示例：
    > ```python
    > class Storage(ABC):
    >     @abstractmethod
    >     def save(self, key: str, data: bytes) -> None: ...
    >
    > class LocalStorage(Storage):
    >     def save(self, key: str, data: bytes) -> None: ...
    > ```

17. 禁止 Java 风格的 `get_x()` / `set_x()`；需要校验或计算时用 `property`。

    > 示例：
    > ```python
    > # 禁止
    > def get_name(self) -> str: return self._name
    > def set_name(self, value: str) -> None: self._name = value
    >
    > # 用
    > @property
    > def name(self) -> str: return self._name
    > ```

18. 禁止为尚不存在的变体预建基类、工厂、注册表、策略、DTO 或扩展点。

    > 反例：项目当前只有一种解析器，却先写出 `ParserBase` + `ParserFactory` + `PARSER_REGISTRY`。
    > 正例：直接写 `InvoiceParser` 一个类，等第二种解析器真正出现时再抽象。

19. 每个类和每个函数只能有一个变更原因。

## 命名

20. 命名大小写遵守 PEP 8：包与模块用 `lower_snake_case`，类与异常用 `PascalCase`，函数、方法、变量、参数用 `lower_snake_case`，模块级常量用 `UPPER_SNAKE_CASE`。

21. 名称必须指向它承载的具体领域对象或职责；禁止用 `Current`、`Temp`、`New`、`Data`、`Info`、`Item`、`Object`、`Manager`、`Handler`、`Processor` 这类无信息量的词充当名称主干。

    > 示例：
    > ```python
    > CurrentSession = Session()      # 禁止：说不出这是什么会话
    > DBSession = Session()           # 用
    > DBTransactionSession = Session()  # 用：需要强调事务语义时
    > ```

22. 名称控制在 1-4 个词，表达清楚即停止；禁止把类型名、设计模式名、层级路径堆进名称。

    > 示例：`OCRResultDataClassObject` 禁止；`OCRResult` 用。

23. 只允许领域内公认的缩写（`OCR`、`URL`、`ID`、`DB`、`HTTP`、`API`），禁止自造缩写和无上下文的单字母名，循环下标 `i` / `j`、坐标 `x` / `y`、异常 `exc` 除外；缩写在类名中整体大写，在函数名与变量名中整体小写。

    > 示例：
    > ```python
    > class DbSession: ...        # 禁止
    > class DBSession: ...        # 用
    > def parse_URL(u): ...       # 禁止
    > def parse_url(url): ...     # 用
    > ```

24. 名称不重复其所在类、模块或命名空间已表达的信息。

    > 示例：
    > ```python
    > class OCRClient:
    >     def ocr_recognize_image(self, image: bytes): ...   # 禁止
    >     def recognize(self, image: bytes): ...             # 用
    > ```

25. 函数名与方法名以动词开头表达动作；返回布尔值的用 `is_` / `has_` / `can_` / `should_` 前缀。

    > 示例：
    > ```python
    > def valid(self) -> bool: ...      # 禁止
    > def is_valid(self) -> bool: ...   # 用
    > ```

26. 类名用名词或名词短语；抽象基类直接用领域概念命名，实现类在名称中体现自身差异点，禁止 `Base` / `Abstract` 前缀和 `Impl` 后缀。

    > 示例：`Storage` + `LocalStorage` / `S3Storage`；禁止 `BaseStorage` + `StorageImpl`。

27. 自定义异常类名以 `Error` 结尾。

    > 示例：`OCRServiceError` 用；`OCRException`、`OCRFailure` 禁止。

28. 同一概念在整个项目中只用一个名称，跨模块保持一致。

    > 反例：同一字段在三处分别叫 `user_id`、`uid`、`account_no`。

29. 仅供内部消费的方法、属性、变量以单下划线开头（`_name`），公开接口不加下划线；禁止用双下划线 name mangling 模拟私有。

    > 示例：
    > ```python
    > class OCRClient:
    >     def recognize(self, image: bytes) -> OCRResult: ...   # 对外契约
    >     def _build_headers(self) -> dict[str, str]: ...       # 实现细节
    >     def __build_headers(self): ...                        # 禁止
    > ```

## 类型注解

30. 所有公开函数和方法的参数与返回值必须有类型注解；私有代码跨越重要内部边界时同样注解。

31. 容器与联合类型用原生语法：`list[int]`、`dict[str, int]`、`tuple[int, ...]`、`set[str]`、`int | None`、`int | str`；禁止 `List`、`Dict`、`Tuple`、`Set`、`Optional`、`Union`。

32. `Callable`、`Iterable`、`Mapping`、`Sequence` 从 `collections.abc` 导入；`Any`、`Literal`、`TypeVar`、`Generic`、`Final`、`ClassVar` 从 `typing` 导入。

33. 用精确的联合类型、`Literal`、泛型或抽象基类替代 `Any`；`Any` 只允许出现在真正的动态边界。

    > 示例：
    > ```python
    > def set_mode(mode: Any) -> None: ...                        # 禁止
    > def set_mode(mode: Literal["fast", "accurate"]) -> None: ... # 用
    > ```

34. 结构已知的数据禁止以 `dict[str, Any]` 跨模块边界传递。

    > 示例：
    > ```python
    > def handle(payload: dict[str, Any]) -> None: ...   # 禁止
    > def handle(payload: OCRRequest) -> None: ...       # 用 dataclass 承载
    > ```

35. 同一函数的不同分支必须返回同一类结构。

    > 反例：命中缓存时返回 `OCRResult`，未命中时返回 `{"text": ..., "score": ...}`。

36. `None` 只用于表示契约允许的"缺失"；禁止用 `None` 表示失败。

    > 示例：
    > ```python
    > def load(path: str) -> Config | None: ...   # 禁止：用 None 掩盖读取失败
    > def load(path: str) -> Config: ...          # 用：失败时抛 ConfigError
    > ```

37. 公开接口用显式参数；`*args` / `**kwargs` 只允许用于装饰器、回调、插件钩子、兼容层和有意转发第三方参数，装饰器场景用 `ParamSpec` 保留类型。

    > 示例：
    > ```python
    > def create_user(**kwargs) -> User: ...                                  # 禁止
    > def create_user(name: str, email: str, age: int | None = None) -> User: ...  # 用
    > ```

38. 禁止为使用 Pydantic 而向项目引入该依赖；项目未使用 Pydantic 时，一律用 `dataclass`。

## 外部依赖隔离

39. 第三方 SDK、远程 API、模型提供方、存储客户端、消息队列等集成必须封装在专用类中，由该类集中管理客户端构造、认证、超时、传输细节和 SDK 专用选项。

40. 封装层只暴露原子操作；禁止把业务流程编排写进封装层。

    > 示例：
    > ```python
    > class OCRClient:
    >     def recognize(self, image: bytes) -> OCRResult: ...        # 原子操作
    >     def process_invoice_and_archive(self, path: Path): ...     # 禁止：业务流程
    > ```

41. 第三方响应在封装层内转换为项目自有的类型化结果；禁止供应商数据结构扩散到调用方。

    > 示例：
    > ```python
    > def recognize(self, image: bytes) -> OCRResult:
    >     raw = self._sdk.basicAccurate(image)                       # 供应商原始 dict
    >     return OCRResult(text=raw["words_result"][0]["words"],
    >                      confidence=raw["words_result"][0]["probability"]["average"])
    > ```

42. 该能力已有封装层时直接复用；禁止另建平行封装。

43. 局部、稳定且仅使用一次的库调用保持直接调用，不加封装层。

44. 数据转换按复杂度就近处理：一次性转换写在调用处或小函数中；可复用转换放独立函数或模块；只有转换本身具备内聚状态、配置或注入依赖时才用映射器类。

## 异常与失败

45. 只捕获最小且有意义的异常类型；禁止静默吞掉失败。

    > 示例：
    > ```python
    > try: ...
    > except Exception: pass                        # 禁止
    >
    > try: ...
    > except FileNotFoundError as exc:              # 用
    >     raise ConfigError(f"配置缺失: {path}") from exc
    > ```

46. `except Exception` 只允许用于真正的容错边界，且必须重新抛出、上报或有意转换。

47. 转换异常时用 `raise NewError(...) from exc` 保留原始异常链。

    > 示例：
    > ```python
    > except httpx.HTTPError as exc:
    >     raise OCRServiceError("识别请求失败") from exc
    > ```

48. 同一操作只用一种失败契约；禁止对同一条件混用异常、`None`、布尔值和错误字典。

    > 反例：同一个 `load()`，文件缺失返回 `None`，格式错误抛异常，字段缺失返回 `{"error": ...}`。

49. 只有调用方能据此采取不同行动时才创建自定义异常。

50. 资源清理用上下文管理器或 `try/finally` 保证确定性执行。

51. 在最早能识别不变量的边界处完成校验。

## 文档与注释

52. 类、公开函数、公开方法写一行文档字符串，说明其职责。

53. 私有函数仅在契约、副作用或算法不直观时才写文档字符串。

54. 文档字符串不复述参数和返回类型（由注解表达），只记录重要前置条件、副作用、抛出的领域异常和不直观的约束。

    > 示例：
    > ```python
    > class OCRClient:
    >     """封装百度 OCR 的基础识别能力."""
    >
    >     def recognize(self, image: bytes) -> OCRResult:
    >         """识别图片并返回标准化结果.
    >
    >         Raises:
    >             OCRServiceError: 远程服务不可用或返回错误码时抛出.
    >         """
    > ```

55. 行内注释只解释"为什么这么做"；禁止复述代码在做什么。

    > 示例：
    > ```python
    > counter += 1        # 计数器加一                    —— 禁止：复述代码
    > retries = 3         # 百度 OCR 偶发 502，三次可覆盖   —— 用：解释取值依据
    > ```

## 入口文件

56. 入口文件（可执行脚本的 `main`、CLI 入口、服务启动点）直接实例化并编排所需的类；禁止为编排逻辑本身再套一层类。

57. 可执行文件通过 `main()` 启动，并用 `if __name__ == "__main__":` 作为入口守卫。

58. 在 `main()` 中显式构造并传入依赖和配置。

    > 示例：
    > ```python
    > def main() -> None:
    >     config = Config.from_env()
    >     client = OCRClient(api_key=config.api_key, timeout=config.timeout)
    >     result = client.recognize(Path(sys.argv[1]).read_bytes())
    >     print(result.text)
    >
    > if __name__ == "__main__":
    >     main()
    > ```

59. I/O 与环境访问留在入口层，可复用的纯逻辑归入对应的类。

60. 确实简单的一次性脚本保持轻量，不强行拆分为多个类。

## 变更纪律

61. 编辑前先读相关代码、项目约定和邻近测试，优先复用或扩展现有实现，禁止创建平行抽象。

62. 只实现本次任务所需的行为；禁止顺带做无关重构。

63. 完成后运行项目现有的测试、类型检查和 linter；无法运行时明确说明原因。
