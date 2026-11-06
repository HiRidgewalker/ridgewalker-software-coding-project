# 02. 分层配置与工程最佳实践

前置阅读：`01_install_and_load.md`

## 1. 是什么

这一部分解决“配置不止一层时怎么管理”的问题，包括只读取文件内容、不直接注入环境变量，以及如何组合 `.env.shared`、`.env.local` 和系统环境变量。

## 2. 工程中何时用

- 团队有共享配置和个人本地配置两层
- 你想先读取配置再自己控制优先级
- 你需要明确知道“系统环境变量是否覆盖 `.env`”

## 3. 核心 API / 用法（带注释的完整示例）

示例文件：

`.env.shared`

```dotenv
APP_ENV=development
API_BASE_URL=https://api.example.com
TIMEOUT_SECONDS=30
```

`.env.local`

```dotenv
OPENAI_API_KEY=sk-[TODO: 填写你的 API Key，这里必须是你自己的真实值]
TIMEOUT_SECONDS=10
```

Python 脚本示例：

```python
import os

from dotenv import dotenv_values, load_dotenv


def load_app_config() -> dict[str, str]:
    # dotenv_values() 只读取文件，不会写入 os.environ
    # 适合你自己决定优先级时使用
    config = {
        **dotenv_values(".env.shared"),
        **dotenv_values(".env.local"),
        # 最后放系统环境变量，表示部署环境优先级最高
        **os.environ,
    }
    return {key: value for key, value in config.items() if value is not None}


def main() -> None:
    # 如果你就是想把 .env 写入环境变量，用 load_dotenv()
    load_dotenv(".env.local")

    config = load_app_config()
    print(config["APP_ENV"])
    print(config["API_BASE_URL"])
    print(config["TIMEOUT_SECONDS"])
    print(bool(config.get("OPENAI_API_KEY")))


if __name__ == "__main__":
    main()
```

补充一个覆盖规则示例：

```python
import os

from dotenv import load_dotenv


os.environ["LOG_LEVEL"] = "WARNING"

load_dotenv(override=False)
print(os.environ["LOG_LEVEL"])  # 仍然是 WARNING

load_dotenv(override=True)
# 这时如果 .env 里定义了 LOG_LEVEL，就会覆盖系统值
```

## 4. 工程最佳实践

✅ 推荐：共享配置和个人密钥分开存，例如 `.env.shared` + `.env.local`。  
✅ 推荐：系统环境变量优先级最高，方便部署环境接管配置。  
✅ 推荐：只有在你明确需要覆盖时才传 `override=True`。  
❌ 避免：默认就用 `override=True`，把外部注入配置悄悄覆盖掉。  
❌ 避免：把 `.env.local`、`.env.secret` 之类的真实密钥文件提交到 Git。  

## 5. 与其他特性的关联

- 如果项目配置项很多，可以继续配合 Pydantic Settings 做类型校验
- 如果你使用 `uv` 管理项目，`python-dotenv` 只负责加载配置，不负责虚拟环境管理
