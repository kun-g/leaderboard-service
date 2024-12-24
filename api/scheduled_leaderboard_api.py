from fastapi import APIRouter, HTTPException
from typing import List, Dict
from leaderboard import ScheduledLeaderboard, LeaderboardStatus
from storage import get_redis_connection, store_scheduled_leaderboard_config, get_scheduled_leaderboard_config, get_all_scheduled_leaderboards
from config import load_config

router = APIRouter()
config = load_config()

@router.post("/scheduled-leaderboards/")
async def create_scheduled_leaderboard(name: str, settlement_time: str, settlement_cycle: str):
    if settlement_cycle not in config["scheduled_leaderboard"]["supported_cycles"]:
        raise HTTPException(status_code=400, detail=f"Unsupported settlement cycle. Supported cycles are: {config['scheduled_leaderboard']['supported_cycles']}")
    
    redis_client = get_redis_connection()
    leaderboard = ScheduledLeaderboard(redis_client, name, settlement_time, settlement_cycle)
    store_scheduled_leaderboard_config(name, settlement_time, settlement_cycle)
    return {"message": f"Scheduled leaderboard '{name}' created successfully"}

@router.get("/scheduled-leaderboards/{name}/status")
async def get_leaderboard_status(name: str):
    config = get_scheduled_leaderboard_config(name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Leaderboard '{name}' not found")
    
    redis_client = get_redis_connection()
    leaderboard = ScheduledLeaderboard(redis_client, name, config["settlement_time"], config["settlement_cycle"])
    status = leaderboard.get_status()
    return {"name": name, "status": status.value}

@router.post("/scheduled-leaderboards/{name}/update-score")
async def update_score(name: str, user_id: str, score: float):
    config = get_scheduled_leaderboard_config(name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Leaderboard '{name}' not found")
    
    redis_client = get_redis_connection()
    leaderboard = ScheduledLeaderboard(redis_client, name, config["settlement_time"], config["settlement_cycle"])
    try:
        leaderboard.update_score(user_id, score)
        return {"message": f"Score updated for user {user_id} in leaderboard '{name}'"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scheduled-leaderboards/{name}/top-n")
async def get_top_n(name: str, n: int):
    config = get_scheduled_leaderboard_config(name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Leaderboard '{name}' not found")
    
    redis_client = get_redis_connection()
    leaderboard = ScheduledLeaderboard(redis_client, name, config["settlement_time"], config["settlement_cycle"])
    top_n = leaderboard.get_top_n(n)
    return {"name": name, "top_n": top_n}

@router.post("/scheduled-leaderboards/{name}/manual-settlement")
async def manual_settlement(name: str):
    config = get_scheduled_leaderboard_config(name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Leaderboard '{name}' not found")
    
    redis_client = get_redis_connection()
    leaderboard = ScheduledLeaderboard(redis_client, name, config["settlement_time"], config["settlement_cycle"])
    try:
        leaderboard.manual_settlement()
        return {"message": f"Leaderboard '{name}' manually settled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scheduled-leaderboards/{name}/history")
async def get_leaderboard_history(name: str):
    config = get_scheduled_leaderboard_config(name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Leaderboard '{name}' not found")
    
    redis_client = get_redis_connection()
    leaderboard = ScheduledLeaderboard(redis_client, name, config["settlement_time"], config["settlement_cycle"])
    history = leaderboard.get_history()
    return {"name": name, "history": history}

@router.get("/scheduled-leaderboards/")
async def get_all_leaderboards():
    leaderboards = get_all_scheduled_leaderboards()
    return {"leaderboards": leaderboards}
