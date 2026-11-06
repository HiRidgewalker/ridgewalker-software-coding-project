---
name: git-commit
description: |
  显式调用执行 git add 和 git commit 的 skill。
  当用户使用 slash command `/git-commit <message>` 显式调用时触发。
  不自动触发，仅当用户明确要求提交代码时使用。
---

# Git Commit Skill

此 skill 执行 `git add` 和 `git commit -m`，用于提交代码变更。

## 输入要求

**必须提供 commit message 参数**，格式为：
```
/git-commit <commit message>
```

**如果未提供 commit message**，立即告知用户：
> "请提供 commit message，例如：`/git-commit 添加新功能`"

## 执行流程

### Step 1: 检查 git status

执行 `git status -s`（简短格式），查看当前工作区状态。

- 如果输出为空或显示 "nothing to commit, working tree clean"，告知用户：
  > "当前没有待提交的变更，无需执行 commit。"
  > 然后**终止流程，不再执行后续步骤**。

### Step 2: 执行 git add

执行 `git add -A` 暂存所有变更。

### Step 3: 执行 git commit

使用用户提供的 message 执行：
```bash
git commit -m "<commit message>"
```

### Step 4: 返回结果

成功时返回：
> "✅ 提交成功"
> 显示 commit hash 和简短描述

失败时（如 empty commit message、引用问题等），将错误信息返回给用户。

## 注意事项

- 不自动触发，仅响应显式调用
- commit message 必须非空
- 不执行 `git push`，仅处理 add 和 commit
- 不修改 message 格式，直接使用用户提供的原始文本
