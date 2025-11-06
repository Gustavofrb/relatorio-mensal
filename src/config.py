# src/config.py
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'

if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key not in os.environ:
                    os.environ[key] = value

API_BASE_URL = os.getenv("API_BASE_URL", "https://desafio-tecnico--tech.vercel.app")
API_TOKEN = os.getenv("API_TOKEN", "")

if not API_TOKEN:
    raise ValueError("API_TOKEN não configurado! Configure no arquivo .env")

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/database.sqlite")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

DEFAULT_MONTH = os.getenv("DEFAULT_MONTH", "")

