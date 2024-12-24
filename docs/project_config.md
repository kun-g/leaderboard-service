# 项目配置文档

## 文件存放规范

1. api/：存放所有API实现相关的文件
   - 所有API端点的实现应该放在这个目录下
   - 每个主要功能模块应该有自己的文件，例如 `user_api.py`, `leaderboard_api.py` 等

2. docs/：存放项目文档
   - project_config.md：当前文件，包含项目基础信息和文件存放规范
   - 其他文档文件也应该放在这个目录下，例如API文档、部署指南等

3. 根目录：
   - main.py：项目的入口文件
   - config.py：配置文件
   - requirements.txt：项目依赖
   - README.md：项目说明文件
   - .gitignore：Git忽略文件
   - 其他直接相关的核心模块文件

## 项目结构

```
leaderboard-service/
│
├── api/
│   └── (API实现文件)
│
├── docs/
│   └── project_config.md
│
├── main.py
├── config.py
├── leaderboard.py
├── storage.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 编码规范

1. 遵循PEP 8 Python编码规范
2. 使用有意义的变量和函数名称
3. 添加适当的注释和文档字符串
4. 保持代码模块化和可重用

## 版本控制

使用Git进行版本控制，主分支为main。

## 依赖管理

使用requirements.txt管理项目依赖。添加新依赖时，请更新此文件。

## 配置管理

使用config.py和.env文件管理配置。敏感信息应存储在.env文件中，并且不应提交到版本控制系统。
