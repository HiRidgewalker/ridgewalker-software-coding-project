# python-dotenv Quickstart

python-dotenv 用来把 `.env` 文件里的配置加载到 `os.environ`，让纯 Python 项目在本地开发时用统一方式管理环境变量。

## 与同类技术的核心差异

| 技术 | 定位 | 最适合做什么 | 不适合做什么 | 直接结论 |
| --- | --- | --- | --- | --- |
| python-dotenv | Python 本地配置加载库 | 在开发环境把 `.env` 内容注入 `os.environ` | 替代真正的密钥管理系统 | 纯 Python 项目本地开发首选它 |
| `os.environ` 直读 | Python 标准库环境变量读取 | 生产环境直接读取系统环境变量 | 本地开发时手工维护大量环境变量 | 生产必须会用，但本地开发不够方便 |
| Pydantic Settings | 配置建模与校验 | 有大量配置项、需要类型校验的项目 | 只想快速加载几个配置项 | 配置复杂时叠加它，不替代 dotenv |
| Dynaconf / environs | 更重的配置框架 | 多环境、多来源配置管理 | 一个小项目的快速上手 | 需求简单时没必要上更重抽象 |

## 适用场景 vs 不适用场景

### 适用场景

- 纯 Python 脚本、本地 CLI、FastAPI 启动脚本需要加载配置
- 你希望把数据库连接、API Key、调试开关放到 `.env`
- 团队需要统一本地开发配置入口

### 不适用场景

- 想把 `.env` 当生产密钥管理方案
- 想用它替代配置校验、类型转换和复杂配置分层
- 部署环境已经由容器平台或 CI 注入环境变量，不需要从文件加载

## 子文档索引

- [01_install_and_load.md](./01_install_and_load.md)
  安装、创建 `.env`、`load_dotenv()` 的最小可用方式。
- [02_layered_config_and_best_practices.md](./02_layered_config_and_best_practices.md)
  多文件配置、`dotenv_values()`、覆盖规则和工程实践。

## 学习路径建议

1. 先看 `01_install_and_load.md`
2. 再看 `02_layered_config_and_best_practices.md`

如果你的目标只是“本地脚本先跑起来”，看完 `01` 就够用。
如果你要把它放进真实项目，请把 `02` 一起看完。
