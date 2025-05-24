#!/usr/bin/env python3
"""
环境变量配置管理模块

参考 agno 框架的最佳实践，提供统一的环境变量管理
支持多种模型提供商的API密钥配置
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class EnvironmentConfig:
    """
    环境变量配置管理器
    
    参考 agno 框架的配置方式，支持：
    1. .env 文件加载
    2. 多种API密钥格式
    3. 环境特定配置
    4. 默认值处理
    """
    
    def __init__(self, env_path: Optional[str] = None):
        """
        初始化环境配置管理器
        
        Args:
            env_path: .env 文件路径，默认为项目根目录
        """
        self.project_root = self._find_project_root()
        self.env_path = env_path or self.project_root / ".env"
        self._load_environment()
        
        logger.info(f"Environment config loaded from: {self.env_path}")
    
    def _find_project_root(self) -> Path:
        """查找项目根目录"""
        current_path = Path(__file__).resolve()
        
        # 向上查找到包含 backend 目录的父目录
        for parent in current_path.parents:
            if (parent / "backend").exists() or (parent / "config").exists():
                return parent / "backend" if (parent / "backend").exists() else parent
        
        # 如果没找到，使用当前文件的上上级目录
        return current_path.parent.parent.parent
    
    def _load_environment(self):
        """加载环境变量"""
        try:
            if self.env_path.exists():
                load_dotenv(self.env_path)
                logger.info(f"Loaded environment variables from {self.env_path}")
            else:
                logger.warning(f"Environment file not found: {self.env_path}")
                self._create_example_env()
        except Exception as e:
            logger.error(f"Failed to load environment variables: {e}")
    
    def _create_example_env(self):
        """创建示例环境文件"""
        example_content = """# AI教学系统环境变量配置文件
# 复制此文件为 .env 并填入真实的API密钥

# =============================================================================
# 模型提供商API密钥配置
# =============================================================================

# OpenAI 配置 (GPT-4, GPT-3.5等)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_ORG_ID=your_org_id_here

# xAI 配置 (Grok)
XAI_API_KEY=your_xai_api_key_here
XAI_BASE_URL=https://api.x.ai/v1

# Google Gemini 配置
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_google_api_key_here

# Anthropic Claude 配置
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_API_KEY=your_anthropic_api_key_here

# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Ollama 本地配置
OLLAMA_HOST=http://localhost:11434

# =============================================================================
# 应用程序配置
# =============================================================================

# 运行环境
ENVIRONMENT=development

# 数据库配置
DATABASE_URL=sqlite:///memory/teaching_memory.db

# 日志级别
LOG_LEVEL=INFO

# 模型配置文件路径
MODEL_CONFIG_PATH=config/models.yaml
"""
        
        example_path = self.project_root / ".env.example"
        try:
            with open(example_path, 'w', encoding='utf-8') as f:
                f.write(example_content)
            logger.info(f"Created example environment file: {example_path}")
        except Exception as e:
            logger.error(f"Failed to create example environment file: {e}")
    
    # =============================================================================
    # API 密钥获取方法 (参考 agno 框架)
    # =============================================================================
    
    def get_openai_config(self) -> Dict[str, Any]:
        """获取 OpenAI 配置"""
        return {
            "api_key": self.get_env("OPENAI_API_KEY"),
            "base_url": self.get_env("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "organization": self.get_env("OPENAI_ORG_ID"),
        }
    
    def get_xai_config(self) -> Dict[str, Any]:
        """获取 xAI 配置"""
        return {
            "api_key": self.get_env("XAI_API_KEY"),
            "base_url": self.get_env("XAI_BASE_URL", "https://api.x.ai/v1"),
        }
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """获取 Gemini 配置"""
        # 支持多种环境变量名称
        api_key = self.get_env("GOOGLE_API_KEY") or self.get_env("GEMINI_API_KEY")
        return {
            "api_key": api_key,
        }
    
    def get_anthropic_config(self) -> Dict[str, Any]:
        """获取 Anthropic 配置"""
        # 支持多种环境变量名称
        api_key = self.get_env("ANTHROPIC_API_KEY") or self.get_env("CLAUDE_API_KEY")
        return {
            "api_key": api_key,
        }
    
    def get_azure_openai_config(self) -> Dict[str, Any]:
        """获取 Azure OpenAI 配置"""
        return {
            "api_key": self.get_env("AZURE_OPENAI_API_KEY"),
            "azure_endpoint": self.get_env("AZURE_OPENAI_ENDPOINT"),
            "api_version": self.get_env("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        }
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """获取 Ollama 配置"""
        return {
            "host": self.get_env("OLLAMA_HOST", "http://localhost:11434"),
        }
    
    # =============================================================================
    # 通用配置方法
    # =============================================================================
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取环境变量值
        
        Args:
            key: 环境变量名
            default: 默认值
            
        Returns:
            环境变量值或默认值
        """
        value = os.getenv(key, default)
        return value if value and value != "your_api_key_here" and value != "your_" + key.lower() + "_here" else None
    
    def get_env_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔型环境变量"""
        value = self.get_env(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")
    
    def get_env_int(self, key: str, default: int = 0) -> int:
        """获取整型环境变量"""
        value = self.get_env(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    def get_environment(self) -> str:
        """获取运行环境"""
        return self.get_env("ENVIRONMENT", "development")
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get_env("LOG_LEVEL", "INFO")
    
    def get_database_url(self) -> str:
        """获取数据库URL"""
        return self.get_env("DATABASE_URL", "sqlite:///memory/teaching_memory.db")
    
    def get_model_config_path(self) -> str:
        """获取模型配置文件路径"""
        return self.get_env("MODEL_CONFIG_PATH", "config/models.yaml")
    
    # =============================================================================
    # 模型特定配置 (兼容 agno 格式)
    # =============================================================================
    
    def get_model_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        获取指定提供商的配置
        
        Args:
            provider: 提供商名称 (openai, xai, gemini, anthropic, ollama等)
            
        Returns:
            提供商配置字典
        """
        provider_configs = {
            "openai": self.get_openai_config,
            "xai": self.get_xai_config,
            "gemini": self.get_gemini_config,
            "anthropic": self.get_anthropic_config,
            "claude": self.get_anthropic_config,  # 别名
            "azure": self.get_azure_openai_config,
            "azure_openai": self.get_azure_openai_config,
            "ollama": self.get_ollama_config,
        }
        
        config_func = provider_configs.get(provider.lower())
        if config_func:
            return config_func()
        else:
            logger.warning(f"Unknown provider: {provider}")
            return {}
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """
        验证所有API密钥是否已设置
        
        Returns:
            各提供商API密钥验证结果
        """
        results = {}
        
        providers = {
            "openai": lambda: bool(self.get_openai_config()["api_key"]),
            "xai": lambda: bool(self.get_xai_config()["api_key"]),
            "gemini": lambda: bool(self.get_gemini_config()["api_key"]),
            "anthropic": lambda: bool(self.get_anthropic_config()["api_key"]),
            "ollama": lambda: True,  # Ollama 不需要API密钥
        }
        
        for provider, validator in providers.items():
            try:
                results[provider] = validator()
            except Exception as e:
                logger.error(f"Error validating {provider} config: {e}")
                results[provider] = False
        
        return results
    
    def get_missing_api_keys(self) -> List[str]:
        """获取缺失的API密钥列表"""
        validation_results = self.validate_api_keys()
        return [provider for provider, is_valid in validation_results.items() 
                if not is_valid and provider != "ollama"]


# 全局配置实例
_env_config = None

def get_env_config() -> EnvironmentConfig:
    """获取全局环境配置实例"""
    global _env_config
    if _env_config is None:
        _env_config = EnvironmentConfig()
    return _env_config

def reload_env_config():
    """重新加载环境配置"""
    global _env_config
    _env_config = None
    return get_env_config()

# 便捷函数
def get_api_key(provider: str) -> Optional[str]:
    """获取指定提供商的API密钥"""
    config = get_env_config()
    provider_config = config.get_model_provider_config(provider)
    return provider_config.get("api_key")

def validate_environment() -> bool:
    """验证环境配置是否完整"""
    config = get_env_config()
    missing_keys = config.get_missing_api_keys()
    
    if missing_keys:
        logger.warning(f"Missing API keys for providers: {missing_keys}")
        logger.info("Please set the required environment variables in .env file")
        return False
    
    logger.info("All required API keys are configured")
    return True 