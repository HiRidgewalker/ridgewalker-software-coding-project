---
name: git-commit-on-demand
description: Stage and commit the current project's git changes only when the user explicitly invokes $git-commit-on-demand and provides a commit message. Use for on-demand local git commits where Codex should first check git status, add changed files, and commit with the exact user-provided message. Do not use implicitly.
---

# Git Commit On Demand

执行一个受控的本地 git 提交流程。只有在用户显式调用 `$git-commit-on-demand` 时才执行。

## Workflow

1. 读取当前仓库的 `git status --short`。
2. 判断是否存在未暂存、未跟踪或已暂存但未提交的变更。
3. 如果没有任何变更，明确告知用户“当前没有可提交内容”，不要创建空提交。
4. 如果存在变更，执行 `git add -A`，将当前工作区变更加入暂存区。
5. 使用用户在本次调用中明确提供的提交信息执行 `git commit -m "<message>"`。
6. 返回提交结果摘要，例如提交哈希、提交信息、涉及文件数量。

## Rules

- 只在用户显式调用 `$git-commit-on-demand` 时使用，不允许隐式触发。
- 提交信息必须来自用户本次调用中提供的文本，不要自行总结或改写，除非用户明确要求润色。
- 默认只执行本地提交，不执行 `git push`。
- 不要使用破坏性 git 命令，例如 `git reset --hard`、`git checkout --`。
- 如果工作区没有变更，不要创建空提交。
- 如果 `git add -A` 后仍然没有可提交内容，停止并告知用户。
- 如果仓库存在明显冲突状态或提交会失败，先向用户报告阻塞原因。

## Invocation Contract

把用户输入解释为：

- 目标：执行一次本地 git 提交
- 参数：提交信息

如果用户没有提供提交信息，先要求用户补充一句明确的 commit message，再继续。

## Example

用户示例：

```text
$git-commit-on-demand commit message: docs: add tokenizer and quantization notes
```

执行要点：

- 先检查 `git status --short`
- 有变更时执行 `git add -A`
- 使用 `docs: add tokenizer and quantization notes` 作为原样提交信息
- 不执行 `push`
