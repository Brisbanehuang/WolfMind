# 🐺⚔️👨‍🌾 狼人杀游戏（Nine-Player Werewolves Game）

基于 AgentScope 的多智能体狼人杀游戏，支持前后端分离架构。

## 项目结构

```
werewolf-game/
├── backend/                 # 后端目录
│   ├── main.py             # 应用入口
│   ├── config.py           # 配置管理
│   ├── core/               # 核心游戏逻辑
│   │   ├── game_engine.py  # 游戏引擎
│   │   ├── roles.py        # 角色系统
│   │   ├── prompts.py      # 提示词
│   │   ├── structured_model.py  # 结构化模型
│   │   └── utils.py        # 工具函数
│   ├── api/                # API 路由（待实现）
│   ├── services/           # 业务服务（待实现）
│   ├── models/             # 数据模型（待实现）
│   ├── data/               # 数据目录
│   ├── .env                # 环境变量
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # 前端目录（待实现）
│   └── README.md
│
├── data/                   # 原数据目录（保留）
├── config.py              # 原配置文件（保留）
├── game.py                # 原游戏文件（保留）
├── main.py                # 原入口文件（保留）
└── README.md              # 项目总览
```

## 快速开始

### 方式一：使用重构后的后端（推荐）

```bash
# 1. 进入后端目录
cd backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 4. 运行游戏
python main.py
```

### 方式二：使用原有代码

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
copy .env.example .env
# 编辑 .env 文件

# 3. 运行游戏
python main.py
```

## 项目特点

### ✨ 已实现功能

- ✅ 多智能体交互系统
- ✅ 角色系统（狼人、村民、预言家、女巫、猎人）
- ✅ 完整的游戏流程（夜晚/白天阶段）
- ✅ 结构化输出处理
- ✅ 配置管理系统（.env 文件）
- ✅ 多语言支持（中文/英文）
- ✅ 多模型支持（DashScope/OpenAI/Ollama）
- ✅ 游戏状态保存与加载
- ✅ 清晰的代码结构

### 🚧 待实现功能

- [ ] FastAPI REST API
- [ ] WebSocket 实时通信
- [ ] React 前端界面
- [ ] 游戏房间管理
- [ ] 用户认证系统
- [ ] 游戏历史记录
- [ ] 游戏回放功能

## 游戏规则

- **3 只狼人** 🐺：每晚杀死一名玩家
- **3 名村民** 👨‍🌾：普通玩家
- **1 名预言家** 🔮：每晚查验一名玩家身份
- **1 名女巫** 🧙‍♀️：拥有解药和毒药
- **1 名猎人** 🏹：被淘汰时可以带走一人

## 配置说明

所有配置都在 `.env` 文件中管理：

```bash
# 模型提供商
MODEL_PROVIDER=dashscope  # dashscope/openai/ollama

# API Keys
DASHSCOPE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# 游戏设置
GAME_LANGUAGE=zh  # zh/en
MAX_GAME_ROUND=30
MAX_DISCUSSION_ROUND=3

# AgentScope Studio
ENABLE_STUDIO=false
STUDIO_URL=http://localhost:3001
```

## 开发路线图

### Phase 1: 代码重构 ✅
- [x] 创建清晰的项目结构
- [x] 分离核心逻辑和业务逻辑
- [x] 优化代码组织

### Phase 2: 后端 API（进行中）
- [ ] 实现 FastAPI 应用
- [ ] 创建 REST API 端点
- [ ] 实现 WebSocket 通信
- [ ] 添加游戏房间管理

### Phase 3: 前端开发
- [ ] 搭建 React 项目
- [ ] 实现游戏界面
- [ ] 对接后端 API
- [ ] 实现实时通信

### Phase 4: 功能完善
- [ ] 用户认证
- [ ] 游戏历史
- [ ] 游戏回放
- [ ] 性能优化

## 技术栈

### 后端
- **框架**: AgentScope
- **语言**: Python 3.8+
- **AI 模型**: DashScope / OpenAI / Ollama
- **配置管理**: python-dotenv

### 前端（计划）
- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **状态管理**: Redux Toolkit
- **实时通信**: WebSocket

## 贡献指南

欢迎贡献代码！请查看各子目录的 README 了解详细信息。

## 许可证

MIT License

## 更新日志

- **2025-11-23**: 项目结构优化
  - ✅ 简化后端目录结构（移除 app 嵌套）
  - ✅ 直接使用 main.py 作为入口
  - ✅ 更清晰的代码组织

- **2025-11-23**: 项目结构重构
  - ✅ 创建前后端分离的目录结构
  - ✅ 重构核心代码到 backend/core
  - ✅ 保留原有代码以确保兼容性
  - ✅ 添加详细的 README 文档

- **2025-11-23**: 配置管理系统
  - ✅ 添加 .env 文件支持
  - ✅ 创建 config.py 模块
  - ✅ 所有配置通过 .env 管理

- **2025-11-22**: 角色系统重构
  - ✅ 每个角色独立类实现
  - ✅ 更好的代码组织
  - ✅ 添加 RoleFactory
