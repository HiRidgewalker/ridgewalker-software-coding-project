import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from learning_langchain.config import AppConfig, load_config


class AppConfigTest(unittest.TestCase):
    def test_load_config_reads_defaults(self) -> None:
        old_api_key = os.environ.get("OPENAI_API_KEY")
        old_model = os.environ.get("OPENAI_MODEL")
        try:
            os.environ["OPENAI_API_KEY"] = "test-key"
            os.environ.pop("OPENAI_MODEL", None)

            config = load_config()

            self.assertEqual(config.openai_api_key, "test-key")
            self.assertEqual(config.openai_model, "gpt-4.1-mini")
        finally:
            if old_api_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = old_api_key

            if old_model is None:
                os.environ.pop("OPENAI_MODEL", None)
            else:
                os.environ["OPENAI_MODEL"] = old_model

    def test_load_config_supports_optional_base_url(self) -> None:
        old_api_key = os.environ.get("OPENAI_API_KEY")
        old_base_url = os.environ.get("OPENAI_BASE_URL")
        try:
            os.environ["OPENAI_API_KEY"] = "test-key"
            os.environ["OPENAI_BASE_URL"] = "https://api.example.com/v1"

            config = load_config()

            self.assertEqual(config.openai_base_url, "https://api.example.com/v1")
        finally:
            if old_api_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = old_api_key

            if old_base_url is None:
                os.environ.pop("OPENAI_BASE_URL", None)
            else:
                os.environ["OPENAI_BASE_URL"] = old_base_url

    def test_app_config_rejects_blank_api_key(self) -> None:
        with self.assertRaises(ValueError):
            AppConfig(openai_api_key="  ")


if __name__ == "__main__":
    unittest.main()
