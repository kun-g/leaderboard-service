import uvicorn
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from api import router
from config import load_config
from storage import get_all_scheduled_leaderboards, get_redis_connection
from leaderboard import ScheduledLeaderboard

app = FastAPI(title="排行榜服务", description="高性能、可扩展的通用排名系统")

# 加载配置
config = load_config()

# 注册路由
app.include_router(router, prefix="/api/v1")

# 创建调度器
scheduler = AsyncIOScheduler()

async def settle_leaderboards():
    leaderboards = get_all_scheduled_leaderboards()
    redis_client = get_redis_connection()
    for name, leaderboard_config in leaderboards.items():
        leaderboard = ScheduledLeaderboard(
            redis_client,
            name,
            leaderboard_config["settlement_time"],
            leaderboard_config["settlement_cycle"]
        )
        if leaderboard.should_settle():
            await leaderboard.settle()

@app.on_event("startup")
async def startup_event():
    # 添加定时任务
    scheduler.add_job(
        settle_leaderboards,
        CronTrigger(minute="*"),  # 每分钟检查一次
        id="settle_leaderboards",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

# 配置可以在这里使用，例如：
app.state.config = config
