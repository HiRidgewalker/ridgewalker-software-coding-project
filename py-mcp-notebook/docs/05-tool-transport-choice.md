# MCP Tool 传输方式选型：stdio 还是 Streamable HTTP

MCP 的 tool 表示“客户端可以请求 server 执行的动作”。同一个 tool 的业务逻辑可以放在不同传输方式后面，但 `stdio` 和 `Streamable HTTP` 面向的运行方式不同，适合的场景也不同。

一句话判断：

```text
只服务本机、由客户端启动、偏个人/IDE/桌面使用：优先 stdio
需要远程访问、统一部署、多用户共享、服务化治理：优先 Streamable HTTP
```

## stdio 适合什么 tool

`stdio` 模式下，MCP Client 会在本机启动 MCP Server 子进程，然后通过标准输入输出交换协议消息。

适合这些 tool：

- 本地文件相关：读取项目文件、分析代码、搜索本地文档、生成本地报告。
- 本地开发工具：调用 formatter、linter、test runner、git 查询、构建脚本。
- IDE 或桌面客户端集成：只给当前用户、当前机器、当前工作区使用。
- 轻量个人工具：不需要部署服务器，不需要端口，不需要公网访问。
- 权限天然绑定本机用户：tool 使用当前用户的文件系统权限、环境变量、SSH key、CLI 登录态。
- 安全边界要求“不暴露网络服务”：希望能力只能由本地客户端启动和访问。

典型例子：

```text
search_project_files(query)
run_pytest(test_path)
read_local_note(note_name)
summarize_git_diff()
format_python_file(path)
```

stdio 的优点：

- 启动简单，不需要监听端口。
- 很适合本地开发和调试。
- 生命周期清楚：客户端启动 server，客户端退出后 server 通常也退出。
- 可以自然复用本机开发环境和本地凭据。

stdio 的限制：

- 不适合多用户共享。
- 不适合远程调用。
- 不适合长时间稳定运行的中心化服务。
- stdout 是协议通道，server 不能随意 `print()` 普通日志。

## Streamable HTTP 适合什么 tool

`Streamable HTTP` 模式下，MCP Server 作为 HTTP 服务运行，Client 通过网络连接它。

适合这些 tool：

- 团队共享能力：多个用户或多个客户端都需要调用同一套 MCP tools。
- 远程系统集成：tool 背后是数据库、内部服务、SaaS API、知识库、工单系统。
- 需要统一鉴权：OAuth、API token、网关、审计、限流、权限分层。
- 需要长期运行：server 作为服务部署，持续对外提供能力。
- 需要跨机器访问：客户端和 server 不在同一台机器上。
- 需要运维治理：日志、监控、告警、版本发布、灰度、容量扩缩。

典型例子：

```text
query_customer_profile(customer_id)
create_jira_ticket(title, description)
search_company_knowledge_base(query)
run_data_warehouse_query(sql)
trigger_ci_pipeline(repo, branch)
```

Streamable HTTP 的优点：

- 可以集中部署和统一管理。
- 适合多客户端、多用户复用。
- 更容易接入企业级认证、审计、限流和监控。
- 可以把敏感后端访问集中在 server 侧，不把数据库或 API 权限散落到每台客户端机器。

Streamable HTTP 的限制：

- 需要部署、网络、端口和服务运维。
- 认证、权限、日志、错误处理要设计得更严谨。
- 本地文件和本地 CLI 场景会更麻烦，因为 server 不一定能访问用户机器上的文件和命令。

## 快速决策表

| 问题 | 更适合 stdio | 更适合 Streamable HTTP |
| --- | --- | --- |
| tool 只给当前机器使用吗 | 是 | 否 |
| tool 需要读取当前工作区文件吗 | 是 | 通常否 |
| tool 是否依赖本机 CLI 登录态 | 是 | 通常否 |
| 是否需要多人共享 | 否 | 是 |
| 是否需要远程访问 | 否 | 是 |
| 是否需要统一鉴权、审计、限流 | 通常不需要 | 是 |
| 是否要长期作为服务运行 | 通常不需要 | 是 |
| 是否要接企业内部系统 | 可以，但偏个人配置 | 更适合 |

## 选型规则

优先选 `stdio`：

- 这个 tool 本质上是“AI 客户端的本地助手”。
- 输入输出围绕当前项目、当前文件系统、当前用户环境。
- 你希望用户安装后立即可用，而不是先部署一个服务。
- 失败影响范围只在当前用户或当前机器。

优先选 `Streamable HTTP`：

- 这个 tool 本质上是“团队或组织共享的 AI 能力服务”。
- 背后连接的是中心化系统，例如数据库、CRM、工单、知识库、CI/CD。
- 你需要权限控制、审计日志、流量控制、服务监控。
- 你不希望每个用户都在本机配置同一套密钥和后端访问权限。

## 容易踩的坑

- 不要因为 tool 简单就默认用 `stdio`。如果它要访问生产系统或多人共享，HTTP 服务化通常更稳。
- 不要因为 HTTP 更“像后端服务”就默认用 HTTP。本地代码搜索、读文件、跑测试这类能力用 stdio 更自然。
- 不要在 stdio server 中把调试信息写到 stdout。stdout 是 MCP 协议通道，普通日志应该写 stderr 或日志文件。
- 不要让远程 HTTP tool 随意执行用户传入的命令或路径。远程 server 的安全边界和本地工具不同。

## 对当前项目的建议

当前项目是入门教程，tool 都是本地演示性质：

- `add(a, b)`：纯计算示例。
- `explain_concept(name)`：读取内置概念字典。

它们不需要部署、不需要多用户共享、不需要远程访问，所以用 `stdio` 最合适。等你要把 tool 接到团队知识库、数据库、工单系统或统一服务时，再考虑改成 `Streamable HTTP`。
