from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"


def build_local_model_dir(model_name: str) -> Path:
    # Hugging Face model id like "Qwen/Qwen3.5-2B" becomes "models/Qwen/Qwen3.5-2B".
    return MODELS_DIR / Path(model_name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a Hugging Face model into the local models directory."
    )
    parser.add_argument(
        "--model-name",
        default="Qwen/Qwen3.5-2B",
        help="Hugging Face model id, for example Qwen/Qwen3.5-2B",
    )
    args = parser.parse_args()

    local_dir = build_local_model_dir(args.model_name)
    local_dir.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading model: {args.model_name}")
    print(f"Local path: {local_dir}")

    snapshot_download(
        repo_id=args.model_name,
        local_dir=str(local_dir),
    )

    print("Download completed.")
    print(f"Model is available at: {local_dir}")


if __name__ == "__main__":
    main()
