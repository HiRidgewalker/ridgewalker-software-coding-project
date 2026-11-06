from collections.abc import AsyncGenerator
from typing import get_type_hints

import main


class TestApplicationLifespanFunctional:
    """验证 FastAPI 生命周期入口。"""

    def test_lifespan_uses_async_generator_annotation(self) -> None:
        """生命周期函数应准确标注异步生成器类型。"""

        original_lifespan = main.lifespan.__wrapped__
        return_type = get_type_hints(original_lifespan)["return"]

        assert return_type == AsyncGenerator[None]
