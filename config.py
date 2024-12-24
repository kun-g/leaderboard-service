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
        },
        "scheduled_leaderboard": {
            "default_settlement_time": os.getenv("DEFAULT_SETTLEMENT_TIME", "22:00:00"),
            "default_settlement_cycle": os.getenv("DEFAULT_SETTLEMENT_CYCLE", "daily"),
            "supported_cycles": ["daily", "weekly", "monthly"]
        }
    }
    return config
