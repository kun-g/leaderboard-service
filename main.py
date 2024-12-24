import uvicorn
from fastapi import FastAPI
from api import router
from config import load_config

app = FastAPI(title="排行榜服务", description="高性能、可扩展的通用排名系统")

# 加载配置
config = load_config()

# 注册路由
app.include_router(router, prefix="/api/v1")

# 配置可以在这里使用，例如：
# app.config = config
