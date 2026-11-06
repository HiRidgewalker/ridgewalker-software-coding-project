# 01. 安装与最小加载

## 1. 是什么

这一部分解决最核心的问题：把项目根目录下的 `.env` 文件读取出来，并让 Python 代码可以像读取系统环境变量一样读取这些值。

## 2. 工程中何时用

- 新建纯 Python 项目，想快速管理本地开发配置
- 你不想每次运行脚本前都手动 `export` 一堆环境变量
- 你的脚本需要读取 API Key、数据库地址、日志级别等配置

## 3. 核心 API / 用法（带注释的完整示例）

先安装依赖：

```bash
uv add python-dotenv
```

创建项目根目录 `.env`：

```dotenv
APP_ENV=development
OPENAI_API_KEY=sk-[TODO: 填写你的 API Key，这里必须是你自己的真实值]
LOG_LEVEL=INFO
```

Python 脚本示例：

```python
import os

from dotenv import load_dotenv


def main() -> None:
    # 不传路径时，python-dotenv 会自动向上查找 .env
    # 默认 override=False，不会覆盖系统里已经存在的同名环境变量
    load_dotenv()

    app_env = os.environ.get("APP_ENV", "development")
    api_key = os.environ.get("OPENAI_API_KEY")
    log_level = os.environ.get("LOG_LEVEL", "INFO")

    # ⚠️ 不要在真实项目里打印完整密钥，这里只演示读取成功
    print(f"APP_ENV={app_env}")
    print(f"OPENAI_API_KEY loaded={bool(api_key)}")
    print(f"LOG_LEVEL={log_level}")


if __name__ == "__main__":
    main()
```

## 4. 工程最佳实践

✅ 推荐：在程序入口尽早执行 `load_dotenv()`。  
✅ 推荐：把 `.env` 放仓库根目录，降低定位成本。  
✅ 推荐：把 `.env` 加入 `.gitignore`，不要提交真实密钥。  
❌ 避免：在业务代码各处重复调用 `load_dotenv()`。  
❌ 避免：把 `.env` 当成生产环境配置来源。  

## 5. 与其他特性的关联

- 真实项目通常会继续配合 `os.environ` 或 `os.getenv()` 读取值
- 当配置项变多时，通常继续配合 `02_layered_config_and_best_practices.md` 里的分层加载方式
