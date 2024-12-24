import os
from dotenv import load_dotenv
from pathlib import Path

def load_config():
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)

    config = {
        "redis": {
            "host": os.getenv("REDIS_HOST"),
            "port": int(os.getenv("REDIS_PORT")),
            "db": int(os.getenv("REDIS_DB"))
        },
        "api": {
            "host": os.getenv("API_HOST"),
            "port": int(os.getenv("API_PORT"))
        },
        "security": {
            "api_key": os.getenv("SECURITY_API_KEY")
        }
    }
    return config
