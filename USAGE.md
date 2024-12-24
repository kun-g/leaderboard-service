# 排行榜服务使用指南

## 目录
- [项目介绍](#项目介绍)
- [快速开始](#快速开始)
- [功能特性](#功能特性)
- [API 接口](#api-接口)
- [SDK 使用](#sdk-使用)
- [配置说明](#配置说明)
- [最佳实践](#最佳实践)

## 项目介绍

排行榜服务（Leaderboard Service）是一个高性能、可扩展的通用排名系统，为各类应用场景提供实时的排名数据服务。无论是游戏排行榜、竞赛积分榜，还是用户活跃度排名，都可以通过简单的接入快速实现。

### 核心特点
- 高性能：毫秒级响应，支持高并发读写
- 实时性：数据实时更新，排名即时生效
- 可扩展：支持水平扩展，轻松应对业务增长
- 多功能：支持多种排行榜类型和排名规则
- 安全性：内置防作弊机制和访问控制

## 快速开始

### 1. 环境要求
- Python 3.8+
- Redis 6.0+
- AWS S3（用于历史数据存储）

### 2. 安装

```bash
pip install leaderboard-service
```

### 3. 基础配置

```python
from leaderboard_service import LeaderboardClient

# 创建客户端实例
client = LeaderboardClient(
    redis_url="redis://localhost:6379",
    s3_bucket="your-bucket-name",
    api_key="your-api-key"
)

# 创建排行榜
leaderboard_id = client.create_leaderboard(
    name="game_scores",
    reset_period="daily",  # 可选：daily, weekly, monthly, never
    sort_order="desc"      # 默认降序排列
)

# 更新分数
client.update_score(
    leaderboard_id="game_scores",
    user_id="player123",
    score=1000
)

# 获取排行榜前10名
top_players = client.get_top_n(
    leaderboard_id="game_scores",
    limit=10
)
```

## 功能特性

### 1. 基础排行榜功能

#### 创建和管理排行榜
- 支持创建多个独立排行榜
- 可设置排行榜重置周期
- 支持自定义排名规则

#### 分数管理
- 实时更新用户分数
- 支持批量更新分数
- 支持分数变化记录

#### 排名查询
- 获取排行榜前N名
- 查询指定用户排名
- 查询用户周边排名
- 支持分页查询

### 2. 高级特性

#### 多维度排序
```python
# 创建多维度排行榜
leaderboard = client.create_leaderboard(
    name="game_ranking",
    dimensions=["score", "time"],
    weights=[0.7, 0.3]  # 分数权重70%，时间权重30%
)
```

#### 定时重置
```python
# 创建每周重置的排行榜
weekly_board = client.create_leaderboard(
    name="weekly_challenge",
    reset_period="weekly",
    reset_day=1  # 每周一重置
)
```

#### 历史数据查询
```python
# 查询历史排行榜数据
historical_data = client.get_historical_ranking(
    leaderboard_id="game_scores",
    date="2023-12-01"
)
```

## API 接口

### RESTful API

#### 创建排行榜
```http
POST /api/v1/leaderboards
Content-Type: application/json

{
    "name": "game_scores",
    "reset_period": "daily",
    "sort_order": "desc"
}
```

#### 更新分数
```http
PUT /api/v1/leaderboards/{leaderboard_id}/scores
Content-Type: application/json

{
    "user_id": "player123",
    "score": 1000
}
```

#### 获取排名
```http
GET /api/v1/leaderboards/{leaderboard_id}/rankings?limit=10
```

### 批量操作接口

#### 批量更新分数
```http
POST /api/v1/leaderboards/{leaderboard_id}/scores/batch
Content-Type: application/json

{
    "scores": [
        {"user_id": "player1", "score": 100},
        {"user_id": "player2", "score": 200}
    ]
}
```

## SDK 使用

### Python SDK

```python
from leaderboard_service import LeaderboardClient

# 初始化客户端
client = LeaderboardClient(config_path="config.yaml")

# 创建排行榜
leaderboard = client.create_leaderboard(name="my_leaderboard")

# 更新分数
client.update_score(
    leaderboard_id=leaderboard.id,
    user_id="user123",
    score=500
)

# 获取用户排名
ranking = client.get_user_ranking(
    leaderboard_id=leaderboard.id,
    user_id="user123"
)

# 获取排行榜前N名
top_users = client.get_top_n(
    leaderboard_id=leaderboard.id,
    limit=10
)
```

## 配置说明

### 配置文件示例 (config.yaml)

```yaml
redis:
  host: localhost
  port: 6379
  db: 0

s3:
  bucket: leaderboard-data
  region: us-west-2

api:
  rate_limit: 1000  # 每分钟请求限制
  timeout: 5        # 请求超时时间（秒）

security:
  enable_encryption: true
  access_control: true
```

### 环境变量配置

```bash
# 必需的环境变量
export LEADERBOARD_API_KEY=your-api-key
export REDIS_URL=redis://localhost:6379
export S3_BUCKET=your-bucket-name

# 可选的环境变量
export LEADERBOARD_LOG_LEVEL=INFO
export LEADERBOARD_RATE_LIMIT=1000
```

## 最佳实践

### 1. 性能优化

- 使用批量接口进行数据更新
- 合理设置缓存策略
- 避免频繁请求完整排行榜数据

```python
# 推荐：使用批量更新接口
client.batch_update_scores(
    leaderboard_id="game_scores",
    scores=[
        {"user_id": "player1", "score": 100},
        {"user_id": "player2", "score": 200}
    ]
)

# 不推荐：多次调用单条更新接口
client.update_score("game_scores", "player1", 100)
client.update_score("game_scores", "player2", 200)
```

### 2. 错误处理

```python
from leaderboard_service.exceptions import LeaderboardError

try:
    client.update_score(
        leaderboard_id="game_scores",
        user_id="player1",
        score=100
    )
except LeaderboardError as e:
    logger.error(f"更新分数失败: {e}")
    # 进行错误处理
```

### 3. 数据安全

- 启用数据加密
- 实施访问控制
- 定期备份数据

```python
# 启用加密传输
client = LeaderboardClient(
    config_path="config.yaml",
    enable_encryption=True
)

# 设置访问权限
client.set_access_control(
    leaderboard_id="game_scores",
    read_roles=["player", "admin"],
    write_roles=["admin"]
)
```

### 4. 监控和告警

- 设置性能监控
- 配置错误告警
- 定期检查数据一致性

```python
# 启用监控
client.enable_monitoring(
    prometheus_port=9090,
    metrics_path="/metrics"
)
