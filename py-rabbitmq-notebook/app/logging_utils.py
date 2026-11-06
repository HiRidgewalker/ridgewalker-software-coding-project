"""应用日志的中文显示配置。"""

from __future__ import annotations

import logging


def configure_logging() -> None:
    """配置中文日志级别并降低第三方客户端的日志噪声。"""

    logging.addLevelName(logging.DEBUG, "调试")
    logging.addLevelName(logging.INFO, "信息")
    logging.addLevelName(logging.WARNING, "警告")
    logging.addLevelName(logging.ERROR, "错误")
    logging.addLevelName(logging.CRITICAL, "严重错误")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logging.getLogger("pika").setLevel(logging.WARNING)
