import unittest
from types import SimpleNamespace

from scripts.streaming_demo import iter_online_text_chunks, iter_request_output_text_deltas


class StreamingDemoOnlineTests(unittest.TestCase):
    def test_iter_online_text_chunks_yields_only_non_empty_deltas(self) -> None:
        stream = [
            SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content="你好"))]
            ),
            SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content="，世界"))]
            ),
            SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content=""))]
            ),
            SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content=None))]
            ),
        ]

        self.assertEqual(list(iter_online_text_chunks(stream)), ["你好", "，世界"])


class StreamingDemoOfflineTests(unittest.IsolatedAsyncioTestCase):
    async def test_iter_request_output_text_deltas_yields_incremental_text(self) -> None:
        async def fake_request_stream():
            yield SimpleNamespace(outputs=[SimpleNamespace(text="第一段")])
            yield SimpleNamespace(outputs=[SimpleNamespace(text="第二段")])
            yield SimpleNamespace(outputs=[SimpleNamespace(text="")])

        chunks = []
        async for chunk in iter_request_output_text_deltas(fake_request_stream()):
            chunks.append(chunk)

        self.assertEqual(chunks, ["第一段", "第二段"])


if __name__ == "__main__":
    unittest.main()
