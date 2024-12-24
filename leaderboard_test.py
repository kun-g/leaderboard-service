import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from leaderboard import Leaderboard, ScheduledLeaderboard, LeaderboardStatus

@pytest.fixture
def mock_redis():
    return Mock()

class TestLeaderboard:
    def test_update_score(self, mock_redis):
        leaderboard = Leaderboard(mock_redis, "test_leaderboard")
        leaderboard.update_score("user1", 100)
        mock_redis.zadd.assert_called_once_with("test_leaderboard", {"user1": 100})

    def test_get_rank(self, mock_redis):
        mock_redis.zrevrank.return_value = 2
        leaderboard = Leaderboard(mock_redis, "test_leaderboard")
        assert leaderboard.get_rank("user1") == 3

    def test_get_score(self, mock_redis):
        mock_redis.zscore.return_value = 100
        leaderboard = Leaderboard(mock_redis, "test_leaderboard")
        assert leaderboard.get_score("user1") == 100.0

    def test_get_top_n(self, mock_redis):
        mock_redis.zrevrange.return_value = [(b"user1", 100), (b"user2", 90)]
        leaderboard = Leaderboard(mock_redis, "test_leaderboard")
        expected = [
            {"user_id": "user1", "score": 100, "rank": 1},
            {"user_id": "user2", "score": 90, "rank": 2}
        ]
        assert leaderboard.get_top_n(2) == expected

    def test_get_user_count(self, mock_redis):
        mock_redis.zcard.return_value = 5
        leaderboard = Leaderboard(mock_redis, "test_leaderboard")
        assert leaderboard.get_user_count() == 5

    def test_remove_user(self, mock_redis):
        leaderboard = Leaderboard(mock_redis, "test_leaderboard")
        leaderboard.remove_user("user1")
        mock_redis.zrem.assert_called_once_with("test_leaderboard", "user1")

    def test_reset(self, mock_redis):
        leaderboard = Leaderboard(mock_redis, "test_leaderboard")
        leaderboard.reset()
        mock_redis.delete.assert_called_once_with("test_leaderboard")

class TestScheduledLeaderboard:
    @pytest.fixture
    def scheduled_leaderboard(self, mock_redis):
        return ScheduledLeaderboard(mock_redis, "test_scheduled_leaderboard", "00:00:00", "daily")

    def test_update_score_in_progress(self, scheduled_leaderboard):
        scheduled_leaderboard.status = LeaderboardStatus.IN_PROGRESS
        scheduled_leaderboard.update_score("user1", 100)
        scheduled_leaderboard.redis.zadd.assert_called_once_with("test_scheduled_leaderboard", {"user1": 100})

    def test_update_score_not_in_progress(self, scheduled_leaderboard):
        with pytest.raises(ValueError):
            scheduled_leaderboard.update_score("user1", 100)

    def test_start_new_period(self, scheduled_leaderboard):
        scheduled_leaderboard.start_new_period()
        assert scheduled_leaderboard.status == LeaderboardStatus.IN_PROGRESS
        scheduled_leaderboard.redis.rename.assert_called_once_with(
            "test_scheduled_leaderboard", "test_scheduled_leaderboard:current"
        )

    def test_settle(self, scheduled_leaderboard):
        scheduled_leaderboard.status = LeaderboardStatus.IN_PROGRESS
        scheduled_leaderboard.get_user_count = Mock(return_value=2)
        scheduled_leaderboard.get_top_n = Mock(return_value=[{"user_id": "user1", "score": 100, "rank": 1}])
        
        with patch('leaderboard.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 5, 1, 12, 0, 0)
            scheduled_leaderboard.settle()

        assert scheduled_leaderboard.status == LeaderboardStatus.SETTLED
        scheduled_leaderboard.redis.hset.assert_called_once()

    def test_get_next_settlement_time_daily(self, scheduled_leaderboard):
            now = datetime.now()
            next_settlement = scheduled_leaderboard.get_next_settlement_time()
            assert next_settlement > now

    def test_get_history(self, scheduled_leaderboard):
        mock_history = {b"2023-05-01T00:00:00": b"[{'user_id': 'user1', 'score': 100, 'rank': 1}]"}
        scheduled_leaderboard.redis.hgetall.return_value = mock_history
        expected = {"2023-05-01T00:00:00": [{'user_id': 'user1', 'score': 100, 'rank': 1}]}
        assert scheduled_leaderboard.get_history() == expected

    def test_manual_settlement_in_progress(self, scheduled_leaderboard):
        scheduled_leaderboard.status = LeaderboardStatus.IN_PROGRESS
        scheduled_leaderboard.settle = Mock()
        scheduled_leaderboard.manual_settlement()
        scheduled_leaderboard.settle.assert_called_once()

    def test_manual_settlement_not_in_progress(self, scheduled_leaderboard):
        with pytest.raises(ValueError):
            scheduled_leaderboard.manual_settlement()

    def test_get_status(self, scheduled_leaderboard):
        assert scheduled_leaderboard.get_status() == LeaderboardStatus.PENDING
