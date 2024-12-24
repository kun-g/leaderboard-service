import redis
from config import load_config

def get_redis_connection():
    config = load_config()
    redis_config = config['redis']
    return redis.Redis(
        host=redis_config['host'],
        port=redis_config['port'],
        db=redis_config['db']
    )
