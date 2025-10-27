# prompt_loader.py
import yaml, os
from pathlib import Path
from typing import Dict, Any

PROMPTS_DIR = Path(os.getcwd()) / "prompts"

class PromptManager:
    _cache: Dict[str, Dict] = {}

    @classmethod
    def load(cls, name: str) -> Dict[str, Any]:
        if name in cls._cache:
            return cls._cache[name]

        file_path = PROMPTS_DIR / f"{name}.yaml"
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)

        cls._cache[name] = prompt_data
        return prompt_data

    @classmethod
    def get(cls, name: str, variant: str = "default") -> str:
        data = cls.load(name)
        return data["variants"][variant]["prompt"]