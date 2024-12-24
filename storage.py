import redis
from config import load_config
import json

_redis_connection = None

def get_redis_connection():
    global _redis_connection
    if _redis_connection is None:
        config = load_config()
        redis_config = config['redis']
        _redis_connection = redis.Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            db=redis_config['db']
        )
    return _redis_connection

def store_scheduled_leaderboard_config(name: str, settlement_time: str, settlement_cycle: str):
    redis_client = get_redis_connection()
    config = {
        "name": name,
        "settlement_time": settlement_time,
        "settlement_cycle": settlement_cycle
    }
    redis_client.hset("scheduled_leaderboards", name, json.dumps(config))

def get_scheduled_leaderboard_config(name: str):
    redis_client = get_redis_connection()
    config = redis_client.hget("scheduled_leaderboards", name)
    if config:
        return json.loads(config)
    return None

def get_all_scheduled_leaderboards():
    redis_client = get_redis_connection()
    leaderboards = redis_client.hgetall("scheduled_leaderboards")
    return {name.decode(): json.loads(config.decode()) for name, config in leaderboards.items()}
