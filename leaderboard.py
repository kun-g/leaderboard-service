from typing import List, Dict, Optional, Union
import redis

class Leaderboard:
    def __init__(self, redis_client: redis.Redis, name: str):
        self.redis = redis_client
        self.name = name

    def update_score(self, user_id: str, score: float) -> None:
        self.redis.zadd(self.name, {user_id: score})

    def get_rank(self, user_id: str) -> Optional[int]:
        rank = self.redis.zrevrank(self.name, user_id)
        return rank + 1 if rank is not None else None

    def get_score(self, user_id: str) -> Optional[float]:
        score = self.redis.zscore(self.name, user_id)
        return float(score) if score is not None else None

    def get_top_n(self, n: int) -> List[Dict[str, Union[str, float, int]]]:
        results = self.redis.zrevrange(self.name, 0, n - 1, withscores=True)
        return [
            {"user_id": user_id.decode(), "score": score, "rank": i + 1}
            for i, (user_id, score) in enumerate(results)
        ]

    def get_user_count(self) -> int:
        return self.redis.zcard(self.name)

    def remove_user(self, user_id: str) -> None:
        self.redis.zrem(self.name, user_id)

    def reset(self) -> None:
        self.redis.delete(self.name)
