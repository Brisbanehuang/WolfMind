# 狼人杀游戏 - 后端

基于 AgentScope 的多智能体狼人杀游戏后端。

## 项目结构

```
backend/
├── main.py              # 应用入口 ⭐
├── config.py            # 配置管理
├── core/                # 核心游戏逻辑
│   ├── __init__.py
│   ├── game_engine.py   # 游戏引擎
│   ├── game_logger.py   # 游戏日志记录器 ⭐
│   ├── roles.py         # 角色系统
│   ├── prompts.py       # 提示词
│   ├── structured_model.py  # 结构化模型
│   └── utils.py         # 工具函数
├── api/                 # API 路由（待实现）
│   └── __init__.py
├── services/            # 业务服务（待实现）
│   └── __init__.py
├── models/              # 数据模型（待实现）
│   └── __init__.py
├── data/                # 数据目录
│   ├── checkpoints/     # 游戏检查点
│   └── game_logs/       # 游戏日志
├── test_import.py       # 导入测试
├── .env                 # 环境变量
├── .env.example         # 环境变量示例
├── requirements.txt     # Python 依赖
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置文件
copy .env.example .env

# 编辑 .env 文件，填入你的 API Key
# 例如：
# MODEL_PROVIDER=dashscope
# DASHSCOPE_API_KEY=your_api_key_here
# GAME_LANGUAGE=zh
```

### 3. 测试导入（可选）

```bash
python test_import.py
```

### 4. 运行游戏

```bash
python main.py
```

## 运行方式

```bash
# 进入后端目录
cd backend

# 运行游戏
python main.py
```

就这么简单！

## 配置说明

所有配置都在 `.env` 文件中管理：

### 必需配置

```bash
# 模型提供商
MODEL_PROVIDER=dashscope  # dashscope/openai/ollama

# API Keys（根据选择的提供商）
DASHSCOPE_API_KEY=your_key_here
# 或
OPENAI_API_KEY=your_key_here

# 游戏语言
GAME_LANGUAGE=zh  # zh=中文, en=英文
```

### 可选配置

```bash
# OpenAI 配置
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-3.5-turbo

# Ollama 配置
OLLAMA_MODEL_NAME=qwen2.5:1.5b

# 游戏参数
MAX_GAME_ROUND=30
MAX_DISCUSSION_ROUND=3

# AgentScope Studio
ENABLE_STUDIO=false
STUDIO_URL=http://localhost:3001
STUDIO_PROJECT=werewolf_game

# 检查点配置（相对于 backend 目录）
CHECKPOINT_DIR=./data/checkpoints
CHECKPOINT_ID=players_checkpoint
```

详细配置请参考 `.env.example` 文件。

## 核心模块说明

### main.py
应用入口，负责初始化游戏、创建玩家、加载/保存检查点

### config.py
配置管理模块，从 .env 文件读取配置

### core/game_engine.py
游戏引擎，控制游戏流程（夜晚/白天阶段切换、投票、胜负判定等）

### core/roles.py
角色系统，每个角色（狼人、村民、预言家、女巫、猎人）都有独立的类和行为逻辑

### core/prompts.py
游戏提示词，支持中英文

### core/structured_model.py
结构化输出模型，用于解析 AI 代理的决策

### core/utils.py
工具函数，包括投票统计、玩家管理等

### core/game_logger.py
游戏日志记录器，自动记录每局游戏的详细信息到 `.log` 文件

## 游戏日志

每局游戏都会自动生成详细的日志文件，保存在 `backend/data/game_logs/` 目录下。

### 日志格式

日志文件名格式：`game_YYYYMMDD_HHMMSS.log`

日志内容包括：
- 游戏基本信息（游戏ID、开始时间）
- 玩家列表及角色分配
- 每回合的详细记录：
  - 夜晚阶段：狼人讨论、狼人投票、女巫行动、预言家查验、猎人开枪
  - 白天阶段：公告、白天讨论、投票、遗言
  - 死亡信息

### 日志示例

```
================================================================================
狼人杀游戏日志
游戏ID: 20251123_173343
开始时间: 2025-11-23 17:33:43
================================================================================

玩家列表:
- Player1: werewolf
- Player2: villager
- Player3: seer
...

第 1 回合
--------------------------------------------------------------------------------

【夜晚阶段】
[17:33:44] [狼人讨论] Player1: 我们淘汰Player5吧。
[17:33:50] [狼人投票] Player1 投票给 Player5
[17:33:55] [狼人投票结果] Player5 被选中击杀 (票数: Player5: 3)
[17:33:57] [女巫行动] 使用解药救了 Player5
[17:33:59] [预言家查验] 查验 Player4, 结果: villager
[17:33:59] [夜晚死亡] 无

【白天阶段】
[17:33:59] [公告] 天亮了，请所有玩家睁眼。昨晚平安夜，无人被淘汰。
[17:34:02] [白天讨论] Player4: 我认为我们应该仔细观察...
[17:34:24] [投票] Player4 投票给 Player5
[17:34:44] [投票结果] Player5 被投出 (票数: Player4: 2, Player5: 7)
[17:34:46] [遗言] Player5: 我认为我们应该继续保持警惕...
[17:34:46] [白天死亡] Player5
```

## 测试

```bash
# 测试模块导入
python test_import.py

# 测试日志功能
python test_logger.py

# 应该看到所有模块导入成功
```

## 下一步开发

- [ ] 实现 FastAPI REST API
- [ ] 实现 WebSocket 实时通信
- [ ] 添加游戏房间管理
- [ ] 添加游戏历史记录
- [ ] 添加用户认证

## 常见问题

### 找不到 .env 文件

```bash
copy .env.example .env
# 然后编辑 .env 文件
```

### API Key 错误

检查 `.env` 文件中的配置是否正确，确保 API Key 有效。

### 模块导入错误

确保在 backend 目录下运行：
```bash
cd backend
python main.py
```
