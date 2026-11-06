# TRASH-PUT(1) — 命令行垃圾桶工具

---

## 名称（NAME）

**trash-put** — 命令行垃圾桶工具。

---

## 语法（SYNOPSIS）

```
trash [选项] ...  [参数] ...
trash-put [选项] ...  [参数] ...
```

---

## 描述（DESCRIPTION）

Trash-cli 软件包提供了一个符合 FreeDesktop.org 垃圾桶规范（Trash Specification）的命令行垃圾桶工具。它会记录每个被丢弃文件的**名称**、**原始路径**、**删除日期**和**权限信息**。

从 home 分区丢弃的文件将存放在以下两个位置之一：
- `$XDG_DATA_HOME/Trash`
- `~/.local/share/Trash/`（当 `$XDG_DATA_HOME` 未定义或为空时）

从其他分区丢弃的文件将存放在以下两个位置之一：
- `$top_dir/.Trash/$uid`
- `$top_dir/.Trash-$uid`

其中：
- **$top_dir**：包含被删除文件的卷的挂载点
- **$uid**：执行删除操作的用户的数字 ID

第一个选项 `$top_dir/.Trash/$uid` 仅在 `.Trash` 目录设置了粘滞位（sticky bit）时可用。第二个选项在第一个选项不可用时使用。

---

## 参数（ARGUMENTS）

要移动到垃圾桶的文件或目录的名称。

---

## 选项（OPTIONS）

| 选项 | 说明 |
| --- | --- |
| `-f` | 静默忽略任何不存在的文件或目录。对于不存在的参数，不打印错误信息，也不向调用者返回非零状态码。 |
| `-h`, `--help` | 显示帮助信息并退出。 |
| `--trash-dir=TRASHDIR` | 使用 TRASHDIR 作为垃圾桶文件夹。 |
| `-v`, `--verbose` | 显示正在执行的操作的详细说明。 |
| `--version` | 显示程序的版本号并退出。 |

---

## 示例（EXAMPLES）

```bash
$ trash-put foo   # 将 foo 文件移入垃圾桶
```

---

## 已知问题（BUGS）

请将 bug 报告提交至：[https://github.com/andreafrancia/trash-cli/issues](https://github.com/andreafrancia/trash-cli/issues)

---

## 致谢方式（IF YOU WANT SAY THANKS）

发送推文（@andreafrancia 或 #trash-cli）或通过 PayPal 捐赠 1、2 或 5 欧元：
[https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=93L6PYT4WBN5A](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=93L6PYT4WBN5A)

---

## 贡献者（CREDITS）

- **Trash** 由 Andrea Francia <andrea@andreafrancia.it> 编写。
- **trash-empty** 原始版本由 Einar Orn Olason <eoo@hi.is> 贡献。
- **手册页**第一版由 Steve Stalcup <vorian@ubuntu.com> 编写，由 Massimo Cavalleri <submax@tiscalinet.it> 修改。

---

## 参见（SEE ALSO）

- `trash-list(1)` — 列出垃圾桶中的文件
- `trash-restore(1)` — 从垃圾桶恢复文件
- `trash-empty(1)` — 清空垃圾桶
- `trash-rm(1)` — 从垃圾桶中永久删除文件
- FreeDesktop.org 垃圾桶规范：[https://specifications.freedesktop.org/trash-spec/trashspec-1.0.html](https://specifications.freedesktop.org/trash-spec/trashspec-1.0.html)

以上软件均基于 **GNU 通用公共许可证（GPL）第 2 版或更高版本** 发布。