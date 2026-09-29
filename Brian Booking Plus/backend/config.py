"""Backend configuration loaded once at process startup."""
import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)
GEOAPIFY_API_KEY = os.environ.get("GEOAPIFY_API_KEY", "").strip()


def geoapify_key_status() -> str:
    return "key is configured" if GEOAPIFY_API_KEY else "key is not configured"
