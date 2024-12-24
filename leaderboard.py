from typing import List, Dict, Optional, Union
import redis
from datetime import datetime, timedelta
from enum import Enum

class LeaderboardStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SETTLED = "settled"
    EXPIRED = "expired"

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

class ScheduledLeaderboard(Leaderboard):
    def __init__(self, redis_client: redis.Redis, name: str, settlement_time: str, settlement_cycle: str):
        super().__init__(redis_client, name)
        self.settlement_time = settlement_time
        self.settlement_cycle = settlement_cycle
        self.status = LeaderboardStatus.PENDING
        self.current_period_key = f"{self.name}:current"
        self.history_key = f"{self.name}:history"

    def update_score(self, user_id: str, score: float) -> None:
        if self.status == LeaderboardStatus.IN_PROGRESS:
            super().update_score(user_id, score)
        else:
            raise ValueError("Cannot update score when leaderboard is not in progress")

    def start_new_period(self) -> None:
        self.status = LeaderboardStatus.IN_PROGRESS
        self.redis.rename(self.name, self.current_period_key)

    def settle(self) -> None:
        if self.status != LeaderboardStatus.IN_PROGRESS:
            raise ValueError("Cannot settle leaderboard that is not in progress")

        timestamp = datetime.now().isoformat()
        snapshot = self.get_top_n(self.get_user_count())
        self.redis.hset(self.history_key, timestamp, str(snapshot))
        self.status = LeaderboardStatus.SETTLED

    def get_next_settlement_time(self) -> datetime:
        now = datetime.now()
        settlement_time = datetime.strptime(self.settlement_time, "%H:%M:%S").time()
        next_settlement = datetime.combine(now.date(), settlement_time)

        if next_settlement <= now:
            if self.settlement_cycle == "daily":
                next_settlement += timedelta(days=1)
            elif self.settlement_cycle == "weekly":
                days_ahead = 7 - next_settlement.weekday()
                next_settlement += timedelta(days=days_ahead)
            elif self.settlement_cycle == "monthly":
                if now.month == 12:
                    next_settlement = next_settlement.replace(year=now.year + 1, month=1)
                else:
                    next_settlement = next_settlement.replace(month=now.month + 1)

        return next_settlement

    def get_history(self) -> Dict[str, List[Dict[str, Union[str, float, int]]]]:
        history = self.redis.hgetall(self.history_key)
        return {k.decode(): eval(v.decode()) for k, v in history.items()}

    def manual_settlement(self) -> None:
        if self.status == LeaderboardStatus.IN_PROGRESS:
            self.settle()
        else:
            raise ValueError("Cannot manually settle leaderboard that is not in progress")

    def get_status(self) -> LeaderboardStatus:
        return self.status
