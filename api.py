from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from leaderboard import Leaderboard
from storage import get_redis_connection

router = APIRouter()

class ScoreUpdate(BaseModel):
    user_id: str
    score: float

class LeaderboardEntry(BaseModel):
    user_id: str
    score: float
    rank: int

redis_conn = get_redis_connection()

def get_leaderboard(name: str) -> Leaderboard:
    return Leaderboard(redis_conn, name)

@router.post("/leaderboards/{name}/scores")
async def update_score(name: str, score_update: ScoreUpdate):
    leaderboard = get_leaderboard(name)
    leaderboard.update_score(score_update.user_id, score_update.score)
    return {"message": "Score updated successfully"}

@router.get("/leaderboards/{name}/scores/{user_id}")
async def get_user_score(name: str, user_id: str):
    leaderboard = get_leaderboard(name)
    score = leaderboard.get_score(user_id)
    if score is None:
        raise HTTPException(status_code=404, detail="User not found")
    rank = leaderboard.get_rank(user_id)
    return {"user_id": user_id, "score": score, "rank": rank}

@router.get("/leaderboards/{name}/top/{n}", response_model=List[LeaderboardEntry])
async def get_top_n(name: str, n: int):
    leaderboard = get_leaderboard(name)
    return leaderboard.get_top_n(n)

@router.delete("/leaderboards/{name}/users/{user_id}")
async def remove_user(name: str, user_id: str):
    leaderboard = get_leaderboard(name)
    leaderboard.remove_user(user_id)
    return {"message": "User removed successfully"}

@router.delete("/leaderboards/{name}")
async def reset_leaderboard(name: str):
    leaderboard = get_leaderboard(name)
    leaderboard.reset()
    return {"message": "Leaderboard reset successfully"}
