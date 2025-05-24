#!/usr/bin/env python3
"""
模型管理器 - 统一管理AI教学系统中的所有LLM模型

简化版：专注于细粒度的Agent配置管理，集成环境变量配置
支持：
1. 分Agent Team配置
2. 多种LLM提供商 (xAI, Gemini, Ollama, OpenAI)
3. 灵活的模型切换
4. 统一的环境变量管理 (参考 agno 框架)
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json

# 导入agno模型
from agno.models.openai import OpenAIChat
from agno.models.xai import xAI
from agno.models.google import Gemini
from agno.models.ollama import Ollama

# 导入环境配置管理器
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from config.env_config import get_env_config, EnvironmentConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    简化版模型管理器 - 集成环境变量配置
    
    负责根据配置文件动态创建和管理不同Agent的模型实例
    参考 agno 框架的最佳实践进行API密钥管理
    """
    
    def __init__(self, config_path: str = "config/models.yaml"):
        """
        初始化模型管理器
        
        Args:
            config_path: 模型配置文件路径
        """
        self.env_config = get_env_config()
        self.config_path = config_path
        self.config = self._load_config()
        self._model_cache = {}  # 模型实例缓存
        
        # 验证环境配置
        self._validate_environment()
        
        logger.info(f"ModelManager initialized with environment config")
    
    def _validate_environment(self):
        """验证环境配置"""
        validation_results = self.env_config.validate_api_keys()
        missing_keys = self.env_config.get_missing_api_keys()
        
        if missing_keys:
            logger.warning(f"Missing API keys for providers: {missing_keys}")
            logger.info("Some model providers may not work without proper API keys")
            logger.info("Please check .env file or set environment variables")
        else:
            logger.info("All API keys are properly configured")
        
        # 记录可用的提供商
        available_providers = [provider for provider, is_valid in validation_results.items() if is_valid]
        logger.info(f"Available providers: {available_providers}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载模型配置文件"""
        try:
            # 使用环境配置中的路径
            config_path = self.env_config.get_model_config_path()
            config_file = Path(config_path)
            
            if not config_file.exists():
                # 如果在backend目录下运行，尝试相对路径
                config_file = Path("../config/models.yaml")
                if not config_file.exists():
                    raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"模型配置文件加载成功: {config_file}")
            return config
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            # 返回默认配置
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置（当配置文件不存在时使用）"""
        return {
            "global_defaults": {
                "default_provider": "ollama",
                "default_model_code": "qwen3_32b",
                "timeout": 30
            },
            "model_providers": {
                "ollama": {
                    "qwen3_32b": {
                        "provider": "ollama",
                        "model_id": "qwen3:32b",
                        "config": {"host": "http://localhost:11434"}
                    }
                }
            },
            "agent_teams": {}
        }
    
    def _resolve_config_with_env(self, config: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """
        使用环境配置解析模型配置
        
        Args:
            config: 原始配置
            provider: 提供商名称
            
        Returns:
            解析后的配置
        """
        # 获取环境配置
        env_provider_config = self.env_config.get_model_provider_config(provider)
        
        # 合并配置，环境配置优先
        resolved_config = config.copy()
        for key, value in env_provider_config.items():
            if value is not None:  # 只覆盖非空值
                resolved_config[key] = value
        
        return resolved_config
    
    def get_model_for_agent(self, team_name: str, agent_name: str, model_id: Optional[str] = None):
        """
        为指定Agent获取模型实例
        
        Args:
            team_name: 团队名称 (teaching_team, learning_team, monitor_team)
            agent_name: Agent名称 (teacher_agent, course_planner等)
            model_id: 可选的模型ID，如果指定则使用该模型，否则使用配置文件中的默认模型
            
        Returns:
            配置好的模型实例
        """
        try:
            # 生成缓存键，包含model_id以区分不同模型
            cache_key = f"{team_name}_{agent_name}_{model_id or 'default'}"
            
            # 检查缓存
            if cache_key in self._model_cache:
                logger.debug(f"从缓存获取模型: {cache_key}")
                return self._model_cache[cache_key]
            
            # 获取模型配置
            if model_id:
                # 如果指定了model_id，直接使用该模型
                model_config = self._get_model_config_by_code(model_id)
                logger.info(f"为 {team_name}.{agent_name} 使用指定模型: {model_id}")
            else:
                # 否则使用配置文件中的默认模型
                model_config = self._get_agent_model_config(team_name, agent_name)
                logger.info(f"为 {team_name}.{agent_name} 使用默认模型: {model_config['model_code']}")
            
            # 创建模型实例
            model_instance = self._create_model_instance(model_config)
            
            # 缓存模型实例
            self._model_cache[cache_key] = model_instance
            
            return model_instance
            
        except Exception as e:
            logger.error(f"获取模型失败 {team_name}.{agent_name} (model_id: {model_id}): {e}")
            # 返回默认模型
            return self._get_fallback_model()
    
    def _get_agent_model_config(self, team_name: str, agent_name: str) -> Dict[str, Any]:
        """获取Agent的模型配置"""
        # 使用Agent团队配置
        agent_teams = self.config.get("agent_teams", {})
        if team_name in agent_teams and agent_name in agent_teams[team_name]:
            agent_config = agent_teams[team_name][agent_name]
            model_code = agent_config.get("model_code")
            
            if model_code:
                # 检查是否使用了xAI的Grok模型，如已知被封禁则自动切换到备用模型
                if model_code.startswith("grok"):
                    logger.warning(f"检测到{team_name}.{agent_name}配置使用xAI (Grok) 模型 {model_code}，但该API已被封禁")
                    logger.info("自动切换到备用模型 qwen3_32b")
                    model_code = "qwen3_32b"  # 自动切换到备用模型
                
                return self._get_model_config_by_code(model_code)
        
        # 使用默认配置
        default_code = self.config["global_defaults"]["default_model_code"]
        return self._get_model_config_by_code(default_code)
    
    def _get_model_config_by_code(self, model_code: str) -> Dict[str, Any]:
        """根据模型代号获取配置"""
        providers = self.config.get("model_providers", {})
        
        for provider_name, provider_config in providers.items():
            if model_code in provider_config:
                config = provider_config[model_code].copy()
                config["model_code"] = model_code
                config["provider_name"] = provider_name
                
                # 使用环境配置解析配置
                config["config"] = self._resolve_config_with_env(config["config"], provider_name)
                
                return config
        
        raise ValueError(f"找不到模型配置: {model_code}")
    
    def _create_model_instance(self, model_config: Dict[str, Any]):
        """根据配置创建模型实例"""
        provider = model_config["provider"]
        model_id = model_config["model_id"]
        config = model_config["config"]
        
        try:
            if provider == "openai":
                return OpenAIChat(
                    id=model_id,
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                    organization=config.get("organization"),
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens", 4096),
                    timeout=config.get("timeout", 30)
                )
            
            elif provider == "xai":
                # 检查xAI API是否已知被封禁
                api_key_status = self.env_config.validate_api_keys().get("xai", False)
                if not api_key_status:
                    logger.warning("xAI (Grok) API密钥不可用，自动使用Ollama备用模型")
                    logger.info("如果您确定API密钥有效，请检查网络连接或API状态")
                    # 直接使用备用模型
                    return self._get_fallback_model()
                
                try:
                    return xAI(
                        id=model_id,
                        api_key=config.get("api_key"),
                        base_url=config.get("base_url", "https://api.x.ai/v1"),
                        temperature=config.get("temperature", 0.7),
                        max_tokens=config.get("max_tokens", 4096),
                        timeout=config.get("timeout", 30)
                    )
                except Exception as xai_error:
                    # 特别检查API被封禁的错误
                    error_str = str(xai_error).lower()
                    if "blocked" in error_str or "permission denied" in error_str:
                        logger.error(f"xAI (Grok) API密钥已被封禁: {xai_error}")
                        logger.info("自动使用Ollama备用模型")
                        return self._get_fallback_model()
                    raise  # 其他错误仍然抛出
            
            elif provider == "gemini":
                return Gemini(
                    id=model_id,
                    api_key=config.get("api_key"),
                    temperature=config.get("temperature", 0.7),
                    timeout=config.get("timeout", 30)
                )
            
            elif provider == "ollama":
                return Ollama(
                    id=model_id,
                    host=config.get("host", "http://localhost:11434"),
                    timeout=config.get("timeout", 60),
                    keep_alive=config.get("keep_alive", "5m")
                )
            
            else:
                raise ValueError(f"不支持的模型提供商: {provider}")
                
        except Exception as e:
            logger.error(f"创建 {provider} 模型实例失败: {e}")
            
            # 如果是API密钥相关错误，给出明确提示
            if "api_key" in str(e).lower():
                provider_config = self.env_config.get_model_provider_config(provider)
                if not provider_config.get("api_key"):
                    logger.error(f"{provider.upper()} API密钥未设置，请在.env文件中配置")
                    logger.info(f"请设置环境变量: {provider.upper()}_API_KEY")
            
            # 返回默认模型
            return self._get_fallback_model()
    
    def _get_fallback_model(self):
        """获取最终备用模型"""
        try:
            # 尝试使用Ollama的简单配置，设置长超时时间适应本地模型
            ollama_config = self.env_config.get_ollama_config()
            return Ollama(
                id="qwen3:32b", 
                host=ollama_config["host"],
                timeout=600,  # 10分钟超时，适应本地大模型推理时间
                keep_alive="10m"
            )
        except:
            # 如果Ollama也不可用，使用最简单的配置
            logger.error("所有模型都不可用，请检查配置和环境")
            raise RuntimeError("无法创建任何可用的模型实例")
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """获取所有可用的模型列表"""
        available_models = {}
        
        for provider_name, provider_config in self.config.get("model_providers", {}).items():
            available_models[provider_name] = []
            
            for model_code, model_info in provider_config.items():
                available_models[provider_name].append({
                    "code": model_code,
                    "id": model_info.get("model_id", ""),
                    "description": model_info.get("description", "")
                })
        
        return available_models
    
    def get_agent_current_model(self, team_name: str, agent_name: str) -> Dict[str, Any]:
        """获取Agent当前使用的模型信息"""
        try:
            model_config = self._get_agent_model_config(team_name, agent_name)
            return {
                "team": team_name,
                "agent": agent_name,
                "model_code": model_config["model_code"],
                "model_id": model_config["model_id"],
                "provider": model_config["provider"],
                "description": model_config.get("description", "")
            }
        except Exception as e:
            logger.error(f"获取Agent模型信息失败: {e}")
            return {}
    
    def update_agent_model(self, team_name: str, agent_name: str, model_code: str) -> bool:
        """
        动态更新Agent的模型配置
        
        Args:
            team_name: 团队名称
            agent_name: Agent名称
            model_code: 新的模型代号
            
        Returns:
            更新是否成功
        """
        try:
            # 验证模型代号是否存在
            self._get_model_config_by_code(model_code)
            
            # 更新配置
            if team_name not in self.config["agent_teams"]:
                self.config["agent_teams"][team_name] = {}
            
            if agent_name not in self.config["agent_teams"][team_name]:
                self.config["agent_teams"][team_name][agent_name] = {}
            
            self.config["agent_teams"][team_name][agent_name]["model_code"] = model_code
            
            # 清除缓存
            cache_key = f"{team_name}_{agent_name}"
            if cache_key in self._model_cache:
                del self._model_cache[cache_key]
            
            logger.info(f"已更新 {team_name}.{agent_name} 的模型为: {model_code}")
            return True
            
        except Exception as e:
            logger.error(f"更新Agent模型失败: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """获取所有模型的状态信息"""
        # 获取环境验证结果
        api_key_status = self.env_config.validate_api_keys()
        missing_keys = self.env_config.get_missing_api_keys()
        
        status = {
            "config_loaded": bool(self.config),
            "cached_models": len(self._model_cache),
            "available_providers": list(self.config.get("model_providers", {}).keys()),
            "api_key_status": api_key_status,
            "missing_api_keys": missing_keys,
            "environment": self.env_config.get_environment(),
            "agent_teams": {}
        }
        
        # 获取每个Agent的模型信息
        for team_name, team_config in self.config.get("agent_teams", {}).items():
            status["agent_teams"][team_name] = {}
            for agent_name in team_config.keys():
                if agent_name != "description":  # 跳过描述字段
                    status["agent_teams"][team_name][agent_name] = self.get_agent_current_model(team_name, agent_name)
        
        return status
    
    def clear_cache(self):
        """清除模型实例缓存"""
        self._model_cache.clear()
        logger.info("模型缓存已清除")
    
    def reload_config(self):
        """重新加载配置文件"""
        self.config = self._load_config()
        self.clear_cache()
        logger.info("配置文件已重新加载")
    
    def get_environment_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        return {
            "environment": self.env_config.get_environment(),
            "log_level": self.env_config.get_log_level(),
            "database_url": self.env_config.get_database_url(),
            "model_config_path": self.env_config.get_model_config_path(),
            "api_key_status": self.env_config.validate_api_keys(),
            "missing_api_keys": self.env_config.get_missing_api_keys()
        }

    def get_model_by_id(self, model_id: str):
        """
        直接通过模型ID获取模型实例（不关联特定Agent）
        
        Args:
            model_id: 模型代号 (如 qwen3_32b, gpt4_turbo等)
            
        Returns:
            配置好的模型实例
        """
        try:
            # 生成缓存键
            cache_key = f"direct_{model_id}"
            
            # 检查缓存
            if cache_key in self._model_cache:
                logger.debug(f"从缓存获取直接模型: {cache_key}")
                return self._model_cache[cache_key]
            
            # 获取模型配置
            model_config = self._get_model_config_by_code(model_id)
            
            # 创建模型实例
            model_instance = self._create_model_instance(model_config)
            
            # 缓存模型实例
            self._model_cache[cache_key] = model_instance
            
            logger.info(f"直接创建模型: {model_id}")
            return model_instance
            
        except Exception as e:
            logger.error(f"直接获取模型失败 {model_id}: {e}")
            # 返回默认模型
            return self._get_fallback_model()


# 全局模型管理器实例
_global_model_manager = None

def get_model_manager() -> ModelManager:
    """获取全局模型管理器实例"""
    global _global_model_manager
    if _global_model_manager is None:
        _global_model_manager = ModelManager()
    return _global_model_manager

def get_agent_model(team_name: str, agent_name: str, model_id: Optional[str] = None):
    """
    便捷函数：获取Agent的模型实例
    
    Args:
        team_name: 团队名称
        agent_name: Agent名称
        model_id: 可选的模型ID，如果指定则使用该模型，否则使用配置文件中的默认模型
        
    Returns:
        模型实例
        
    Examples:
        # 使用默认配置的模型
        model = get_agent_model("teaching_team", "teacher_agent")
        
        # 临时切换到指定模型
        model = get_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")
    """
    manager = get_model_manager()
    return manager.get_model_for_agent(team_name, agent_name, model_id)

def get_model_by_id(model_id: str):
    """
    便捷函数：直接通过模型ID获取模型实例
    
    Args:
        model_id: 模型代号 (如 qwen3_32b, gpt4_turbo等)
        
    Returns:
        模型实例
        
    Examples:
        # 直接获取指定模型
        model = get_model_by_id("qwen3_32b")
        model = get_model_by_id("gpt4_turbo")
    """
    manager = get_model_manager()
    return manager.get_model_by_id(model_id)

def list_available_models() -> Dict[str, List[str]]:
    """
    便捷函数：获取所有可用的模型列表
    
    Returns:
        按提供商分组的模型列表
        
    Examples:
        models = list_available_models()
        print(models["ollama"])  # ['qwen3_32b', 'qwen3_14b', ...]
    """
    manager = get_model_manager()
    return manager.get_available_models() 