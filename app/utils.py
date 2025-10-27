
from pathlib import Path
import os 

def load_env_file(env_path: str = ".env") -> None:
    """
    Manually load environment variables from a .env file
    without using external libraries like python-dotenv.

    Each line should follow the format:
        KEY=VALUE
    Lines starting with '#' are ignored.
    """
    env_file = Path(env_path)
    if not env_file.exists():
        print(f"⚠️  No .env file found at {env_path}. Using existing environment variables.")
        return

    with env_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key not in os.environ:  # don’t overwrite existing env vars
                os.environ[key] = value