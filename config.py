# -*- coding: utf-8 -*-
"""配置管理模块 - 从 .env 文件读取配置"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """配置类 - 管理所有游戏配置"""
    
    def __init__(self):
        """初始化配置，从 .env 文件加载"""
        self._load_env()
        
    def _load_env(self):
        """加载 .env 文件"""
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith("#"):
                        continue
                    # 解析键值对
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        # 只有当环境变量不存在时才设置
                        if key and not os.environ.get(key):
                            os.environ[key] = value
    
    # ==================== API 配置 ====================
    
    @property
    def dashscope_api_key(self) -> Optional[str]:
        """DashScope API Key"""
        return os.environ.get("DASHSCOPE_API_KEY")
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API Key"""
        return os.environ.get("OPENAI_API_KEY")
    
    @property
    def openai_base_url(self) -> str:
        """OpenAI Base URL"""
        return os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    @property
    def openai_model_name(self) -> str:
        """OpenAI Model Name"""
        return os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    
    @property
    def ollama_model_name(self) -> str:
        """Ollama Model Name"""
        return os.environ.get("OLLAMA_MODEL_NAME", "qwen2.5:1.5b")
    
    # ==================== 模型选择 ====================
    
    @property
    def model_provider(self) -> str:
        """模型提供商: dashscope, openai, ollama"""
        return os.environ.get("MODEL_PROVIDER", "dashscope").lower()
    
    # ==================== 游戏配置 ====================
    
    @property
    def game_language(self) -> str:
        """游戏语言: zh, en"""
        return os.environ.get("GAME_LANGUAGE", "zh").lower()
    
    @property
    def max_game_round(self) -> int:
        """最大游戏轮数"""
        return int(os.environ.get("MAX_GAME_ROUND", "30"))
    
    @property
    def max_discussion_round(self) -> int:
        """每个狼人的最大讨论轮数"""
        return int(os.environ.get("MAX_DISCUSSION_ROUND", "3"))
    
    # ==================== AgentScope Studio 配置 ====================
    
    @property
    def enable_studio(self) -> bool:
        """是否启用 Studio"""
        return os.environ.get("ENABLE_STUDIO", "false").lower() == "true"
    
    @property
    def studio_url(self) -> str:
        """Studio URL"""
        return os.environ.get("STUDIO_URL", "http://localhost:3001")
    
    @property
    def studio_project(self) -> str:
        """Studio 项目名称"""
        return os.environ.get("STUDIO_PROJECT", "werewolf_game")
    
    # ==================== 检查点配置 ====================
    
    @property
    def checkpoint_dir(self) -> str:
        """检查点保存目录"""
        return os.environ.get("CHECKPOINT_DIR", "./checkpoints")
    
    @property
    def checkpoint_id(self) -> str:
        """检查点文件名"""
        return os.environ.get("CHECKPOINT_ID", "players_checkpoint")
    
    # ==================== 验证方法 ====================
    
    def validate(self) -> tuple[bool, str]:
        """验证配置是否完整
        
        Returns:
            (is_valid, error_message)
        """
        if self.model_provider == "dashscope":
            if not self.dashscope_api_key:
                return False, "DASHSCOPE_API_KEY 未设置"
        elif self.model_provider == "openai":
            if not self.openai_api_key:
                return False, "OPENAI_API_KEY 未设置"
        elif self.model_provider == "ollama":
            # Ollama 不需要 API Key
            pass
        else:
            return False, f"未知的模型提供商: {self.model_provider}"
        
        if self.game_language not in ["zh", "en"]:
            return False, f"不支持的语言: {self.game_language}"
        
        return True, ""
    
    def print_config(self):
        """打印当前配置（隐藏敏感信息）"""
        print("=" * 50)
        print("当前配置:")
        print("=" * 50)
        print(f"模型提供商: {self.model_provider}")
        
        if self.model_provider == "dashscope":
            api_key = self.dashscope_api_key
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if api_key and len(api_key) > 12 else "未设置"
            print(f"DashScope API Key: {masked_key}")
        elif self.model_provider == "openai":
            api_key = self.openai_api_key
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if api_key and len(api_key) > 12 else "未设置"
            print(f"OpenAI API Key: {masked_key}")
            print(f"OpenAI Base URL: {self.openai_base_url}")
            print(f"OpenAI Model: {self.openai_model_name}")
        elif self.model_provider == "ollama":
            print(f"Ollama Model: {self.ollama_model_name}")
        
        print(f"游戏语言: {self.game_language}")
        print(f"最大游戏轮数: {self.max_game_round}")
        print(f"最大讨论轮数: {self.max_discussion_round}")
        print(f"启用 Studio: {self.enable_studio}")
        print(f"检查点目录: {self.checkpoint_dir}")
        print("=" * 50)


# 全局配置实例
config = Config()
