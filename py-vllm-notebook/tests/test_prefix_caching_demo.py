import unittest
from unittest.mock import MagicMock, patch

from scripts.prefix_caching_demo import run_offline


class PrefixCachingDemoTests(unittest.TestCase):
    @patch("scripts.prefix_caching_demo.timed_call")
    @patch("scripts.prefix_caching_demo.default_sampling_params")
    @patch("scripts.prefix_caching_demo.build_prefix_caching_prompts")
    @patch("scripts.prefix_caching_demo.build_offline_llm")
    def test_run_offline_enables_prefix_caching_on_llm(
        self,
        mock_build_offline_llm: MagicMock,
        mock_build_prefix_caching_prompts: MagicMock,
        mock_default_sampling_params: MagicMock,
        mock_timed_call: MagicMock,
    ) -> None:
        fake_llm = MagicMock()
        mock_build_offline_llm.return_value = fake_llm
        mock_build_prefix_caching_prompts.return_value = ("prompt1", "prompt2")
        mock_default_sampling_params.return_value = object()
        mock_timed_call.side_effect = [
            ([MagicMock(num_cached_tokens=0, outputs=[MagicMock(text="a")])], 1.0),
            ([MagicMock(num_cached_tokens=8, outputs=[MagicMock(text="b")])], 0.5),
        ]

        run_offline(max_tokens=64)

        mock_build_offline_llm.assert_called_once_with(enable_prefix_caching=True)


if __name__ == "__main__":
    unittest.main()
