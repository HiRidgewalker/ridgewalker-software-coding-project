import unittest

from scripts.feature_demo_common import (
    DEFAULT_MODEL_ID,
    DEFAULT_ONLINE_BASE_URL,
    build_chat_messages,
    build_prefix_caching_prompts,
    build_structured_output_schema,
    build_weather_tool,
    default_sampling_params,
)


class FeatureDemoCommonTests(unittest.TestCase):
    def test_default_online_base_url_points_to_local_vllm(self) -> None:
        self.assertEqual(DEFAULT_ONLINE_BASE_URL, "http://localhost:8000/v1")

    def test_default_model_id_matches_repo_docs(self) -> None:
        self.assertEqual(DEFAULT_MODEL_ID, "models/Qwen/Qwen3.5-2B")

    def test_build_chat_messages_includes_system_and_user_message(self) -> None:
        messages = build_chat_messages(
            system_prompt="You are a test assistant.",
            user_prompt="Summarize vLLM in one sentence.",
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "You are a test assistant.")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "Summarize vLLM in one sentence.")

    def test_build_chat_messages_can_prepend_shared_prefix(self) -> None:
        messages = build_chat_messages(
            system_prompt="You are a test assistant.",
            user_prompt="Explain the tuning order.",
            shared_prefix="Context block",
        )

        self.assertIn("Context block", messages[1]["content"])
        self.assertIn("Explain the tuning order.", messages[1]["content"])

    def test_structured_output_schema_is_json_object(self) -> None:
        schema = build_structured_output_schema()

        self.assertEqual(schema["type"], "object")
        self.assertIn("summary", schema["properties"])
        self.assertIn("key_parameters", schema["properties"])
        self.assertEqual(schema["required"], ["summary", "key_parameters"])

    def test_weather_tool_has_openai_function_shape(self) -> None:
        tool = build_weather_tool()

        self.assertEqual(tool["type"], "function")
        self.assertEqual(tool["function"]["name"], "get_weather")
        self.assertEqual(
            tool["function"]["parameters"]["required"],
            ["city"],
        )

    def test_default_sampling_params_wraps_structured_outputs_for_vllm(self) -> None:
        params = default_sampling_params(
            max_tokens=64,
            temperature=0.0,
            structured_json_schema=build_structured_output_schema(),
        )

        self.assertIsNotNone(params.structured_outputs)
        self.assertTrue(hasattr(params.structured_outputs, "json"))
        self.assertEqual(params.structured_outputs.json["type"], "object")

    def test_prefix_caching_prompts_share_long_prefix_and_differ_in_question(self) -> None:
        first_prompt, second_prompt = build_prefix_caching_prompts()

        self.assertGreater(len(first_prompt), 200)
        self.assertGreater(len(second_prompt), 200)
        self.assertNotEqual(first_prompt, second_prompt)
        self.assertIn("问题1：", first_prompt)
        self.assertIn("问题2：", second_prompt)
        self.assertIn("vLLM 本地部署说明", first_prompt)
        self.assertIn("vLLM 本地部署说明", second_prompt)


if __name__ == "__main__":
    unittest.main()
