# 🐺⚔️👨‍🌾 Nine-Player Werewolves Game

This is a nine-players werewolves game example built using AgentScope, showcasing **multi-agent interactions**,
**role-based gameplay**, and **structured output handling**.
Specifically, this game is consisted of

- three villagers 👨‍🌾,
- three werewolves 🐺,
- one seer 🔮,
- one witch 🧙‍♀️ and
- one hunter 🏹.

## ✨Changelog

- **2025-11-23**: Configuration management system:
    - ✅ Added `.env` file support for secure configuration management
    - ✅ Created `config.py` module for centralized configuration
    - ✅ All API keys and settings now managed through `.env` file
    - ✅ No need to modify code to change configurations
    - ✅ Added comprehensive configuration documentation
    - See `配置说明.md` for detailed guide

- **2025-11-22**: Major refactoring - Role-based architecture:
    - Refactored each identity into independent classes (Werewolf, Villager, Seer, Witch, Hunter)
    - Better code organization and easier to extend with new roles
    - Each role maintains its own state (e.g., witch's potions, seer's checked players)
    - Added `RoleFactory` for creating role instances
    - See `角色系统说明.md` for detailed documentation

- 2025-10: We update the example to support more features:
    - Allow the dead players to leave messages.
    - Support Chinese now.
    - Support **continuous gaming** by loading and saving session states, so the same agents can play multiple games and continue learning and optimizing their strategies.


## QuickStart

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Settings

```bash
# Copy the example config file
cp .env.example .env

# Edit .env and fill in your API key
# For example:
# MODEL_PROVIDER=dashscope
# DASHSCOPE_API_KEY=your_api_key_here
# GAME_LANGUAGE=zh
```

### 3. Run the Game

```bash
python main.py
```

> Note:
> - All configurations are managed in the `.env` file
> - See `配置说明.md` (Configuration Guide) for detailed settings
> - Different models may yield different game experiences

Running the example with AgentScope Studio provides a more interactive experience.

- Demo Video in Chinese (click to play):

[![Werewolf Game in Chinese](https://img.alicdn.com/imgextra/i3/6000000007235/O1CN011pK6Be23JgcdLWmLX_!!6000000007235-0-tbvideo.jpg)](https://cloud.video.taobao.com/vod/KxyR66_CWaWwu76OPTvOV2Ye1Gas3i5p4molJtzhn_s.mp4)

- Demo Video in English (click to play):

[![Werewolf Game in English](https://img.alicdn.com/imgextra/i3/6000000007389/O1CN011alyGK24SDcFBzHea_!!6000000007389-0-tbvideo.jpg)](https://cloud.video.taobao.com/vod/bMiRTfxPg2vm76wEoaIP2eJfkCi8CUExHRas-1LyK1I.mp4)

## Details

The game is built with the ``ReActAgent`` in AgentScope, utilizing its ability to generate structured outputs to
control the game flow and interactions.
We also use the ``MsgHub`` and pipelines in AgentScope to manage the complex interactions like discussion and voting.
It's very interesting to see how agents play the werewolf game with different roles and objectives.

### Project Structure

```
.
├── main.py                 # Entry point
├── game.py                 # Game main logic
├── roles.py                # Role classes (NEW!)
├── config.py               # Configuration management (NEW!)
├── utils.py                # Utility functions
├── structured_model.py     # Structured output models
├── prompt.py               # Game prompts
├── test_roles.py           # Role system tests (NEW!)
├── .env.example            # Example configuration (NEW!)
├── .env                    # Your configuration (NEW!)
├── 角色系统说明.md          # Role system documentation (NEW!)
└── 配置说明.md             # Configuration guide (NEW!)
```

### Role System

Each identity is now implemented as a separate class:

- **BaseRole**: Abstract base class for all roles
- **Werewolf**: Team discussion and voting
- **Villager**: Basic role with no special abilities
- **Seer**: Check one player's identity each night
- **Witch**: Use healing/poison potions
- **Hunter**: Shoot someone when eliminated

Benefits:
- ✅ Clear code organization
- ✅ Easy to add new roles
- ✅ Better state management
- ✅ Type-safe and testable

# Advanced Usage

## Change Language

Simply edit the `.env` file:

```bash
GAME_LANGUAGE=zh  # Chinese
# or
GAME_LANGUAGE=en  # English
```

## Change Models

Edit the `.env` file to switch between different model providers:

```bash
# Use DashScope (Alibaba Cloud)
MODEL_PROVIDER=dashscope
DASHSCOPE_API_KEY=your_key

# Use OpenAI-compatible API (e.g., Zhipu AI)
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
OPENAI_MODEL_NAME=glm-4.5-air

# Use local Ollama model
MODEL_PROVIDER=ollama
OLLAMA_MODEL_NAME=qwen2.5:1.5b
```

## Enable AgentScope Studio

Edit the `.env` file:

```bash
ENABLE_STUDIO=true
STUDIO_URL=http://localhost:3001
STUDIO_PROJECT=werewolf_game
```

## Play with Agents

You can replace one of the agents with a `UserAgent` to play with AI agents by modifying `main.py`.

## Further Reading

- [Structured Output](https://doc.agentscope.io/tutorial/task_agent.html#structured-output)
- [MsgHub and Pipelines](https://doc.agentscope.io/tutorial/task_pipeline.html)
- [Prompt Formatter](https://doc.agentscope.io/tutorial/task_prompt.html)
- [AgentScope Studio](https://doc.agentscope.io/tutorial/task_studio.html)
