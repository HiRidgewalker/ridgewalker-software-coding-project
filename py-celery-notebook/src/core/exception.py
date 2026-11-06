class RetryableTaskError(RuntimeError):
    """表示外部服务暂时不可用等可恢复错误。"""
