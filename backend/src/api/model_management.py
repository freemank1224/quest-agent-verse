#!/usr/bin/env python3
"""
模型管理API - 提供Web接口来管理Agent模型配置

简化版：专注于基础的Agent模型管理功能
提供以下功能：
1. 查看所有可用模型
2. 查看Agent当前使用的模型
3. 动态切换Agent模型
4. 获取模型状态信息
5. 重新加载配置
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

# 导入模型管理器
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from utils.model_manager import get_model_manager, ModelManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/models", tags=["模型管理"])

# Pydantic模型
class ModelSwitchRequest(BaseModel):
    team_name: str
    agent_name: str
    model_code: str

class ModelInfo(BaseModel):
    code: str
    id: str
    description: str

class AgentModelInfo(BaseModel):
    team: str
    agent: str
    model_code: str
    model_id: str
    provider: str
    description: str

class ModelStatusResponse(BaseModel):
    config_loaded: bool
    cached_models: int
    available_providers: List[str]
    agent_teams: Dict[str, Dict[str, AgentModelInfo]]

# 依赖注入：获取模型管理器
def get_manager() -> ModelManager:
    """获取模型管理器实例"""
    try:
        return get_model_manager()
    except Exception as e:
        logger.error(f"获取模型管理器失败: {e}")
        raise HTTPException(status_code=500, detail="模型管理器初始化失败")

@router.get("/available", summary="获取所有可用模型")
async def get_available_models(manager: ModelManager = Depends(get_manager)) -> Dict[str, List[ModelInfo]]:
    """
    获取所有可用的模型列表
    
    返回按提供商分组的模型信息
    """
    try:
        available_models = manager.get_available_models()
        
        # 转换为响应格式
        result = {}
        for provider, models in available_models.items():
            result[provider] = [
                ModelInfo(
                    code=model["code"],
                    id=model["id"],
                    description=model["description"]
                )
                for model in models
            ]
        
        return result
    except Exception as e:
        logger.error(f"获取可用模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取可用模型失败: {str(e)}")

@router.get("/status", summary="获取模型状态")
async def get_model_status(manager: ModelManager = Depends(get_manager)) -> ModelStatusResponse:
    """
    获取所有模型的状态信息
    
    包括缓存状态、Agent配置等
    """
    try:
        status = manager.get_model_status()
        
        # 转换agent_teams格式
        agent_teams = {}
        for team_name, team_agents in status.get("agent_teams", {}).items():
            agent_teams[team_name] = {}
            for agent_name, agent_info in team_agents.items():
                if agent_info:  # 确保agent_info不为空
                    agent_teams[team_name][agent_name] = AgentModelInfo(**agent_info)
        
        return ModelStatusResponse(
            config_loaded=status["config_loaded"],
            cached_models=status["cached_models"],
            available_providers=status["available_providers"],
            agent_teams=agent_teams
        )
    except Exception as e:
        logger.error(f"获取模型状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型状态失败: {str(e)}")

@router.get("/agent/{team_name}/{agent_name}", summary="获取Agent当前模型")
async def get_agent_model(
    team_name: str, 
    agent_name: str, 
    manager: ModelManager = Depends(get_manager)
) -> AgentModelInfo:
    """
    获取指定Agent当前使用的模型信息
    
    Args:
        team_name: 团队名称 (teaching_team, learning_team, monitor_team)
        agent_name: Agent名称 (teacher_agent, course_planner等)
    """
    try:
        model_info = manager.get_agent_current_model(team_name, agent_name)
        
        if not model_info:
            raise HTTPException(
                status_code=404, 
                detail=f"找不到Agent: {team_name}.{agent_name}"
            )
        
        return AgentModelInfo(**model_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Agent模型信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取Agent模型信息失败: {str(e)}")

@router.post("/agent/switch", summary="切换Agent模型")
async def switch_agent_model(
    request: ModelSwitchRequest,
    manager: ModelManager = Depends(get_manager)
) -> Dict[str, Any]:
    """
    切换指定Agent的模型
    
    Args:
        request: 包含团队名称、Agent名称和新模型代号的请求
    """
    try:
        success = manager.update_agent_model(
            request.team_name, 
            request.agent_name, 
            request.model_code
        )
        
        if success:
            # 获取更新后的模型信息
            updated_info = manager.get_agent_current_model(request.team_name, request.agent_name)
            
            return {
                "success": True,
                "message": f"已成功将 {request.team_name}.{request.agent_name} 的模型切换为 {request.model_code}",
                "model_info": updated_info
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"模型切换失败，请检查模型代号是否正确: {request.model_code}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换Agent模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"切换Agent模型失败: {str(e)}")

@router.post("/reload", summary="重新加载配置")
async def reload_config(manager: ModelManager = Depends(get_manager)) -> Dict[str, str]:
    """
    重新加载模型配置文件
    
    清除缓存并重新读取配置文件
    """
    try:
        manager.reload_config()
        
        return {
            "success": True,
            "message": "配置文件已重新加载，模型缓存已清除"
        }
    except Exception as e:
        logger.error(f"重新加载配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新加载配置失败: {str(e)}")

@router.delete("/cache", summary="清除模型缓存")
async def clear_cache(manager: ModelManager = Depends(get_manager)) -> Dict[str, str]:
    """
    清除模型实例缓存
    
    下次使用时将重新创建模型实例
    """
    try:
        manager.clear_cache()
        
        return {
            "success": True,
            "message": "模型缓存已清除"
        }
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")

@router.get("/health", summary="模型管理健康检查")
async def health_check(manager: ModelManager = Depends(get_manager)) -> Dict[str, Any]:
    """
    检查模型管理系统的健康状态
    """
    try:
        status = manager.get_model_status()
        
        # 检查关键状态
        health_status = {
            "status": "healthy",
            "config_loaded": status["config_loaded"],
            "available_providers": len(status["available_providers"]),
            "cached_models": status["cached_models"],
            "timestamp": "2024-05-23T21:45:00Z"  # 这里应该使用实际时间戳
        }
        
        # 如果配置未加载，标记为不健康
        if not status["config_loaded"]:
            health_status["status"] = "unhealthy"
            health_status["issues"] = ["配置文件加载失败"]
        
        return health_status
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-05-23T21:45:00Z"
        }

# 便捷的路由组合
@router.get("/teams", summary="获取所有团队和Agent")
async def get_teams_and_agents(manager: ModelManager = Depends(get_manager)) -> Dict[str, Any]:
    """
    获取所有团队和其下属Agent的列表
    """
    try:
        config = manager.config
        agent_teams = config.get("agent_teams", {})
        
        result = {}
        for team_name, team_config in agent_teams.items():
            # 获取除了description之外的所有键作为agent列表
            agents = [key for key in team_config.keys() if key != "description"]
            result[team_name] = {
                "name": team_name,
                "description": team_config.get("description", ""),
                "agents": agents
            }
        
        return result
    except Exception as e:
        logger.error(f"获取团队信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取团队信息失败: {str(e)}")

# 批量操作
@router.post("/batch/switch", summary="批量切换模型")
async def batch_switch_models(
    switches: List[ModelSwitchRequest],
    manager: ModelManager = Depends(get_manager)
) -> Dict[str, Any]:
    """
    批量切换多个Agent的模型
    """
    results = []
    errors = []
    
    for switch in switches:
        try:
            success = manager.update_agent_model(
                switch.team_name, 
                switch.agent_name, 
                switch.model_code
            )
            
            if success:
                results.append({
                    "agent": f"{switch.team_name}.{switch.agent_name}",
                    "model": switch.model_code,
                    "status": "success"
                })
            else:
                errors.append({
                    "agent": f"{switch.team_name}.{switch.agent_name}",
                    "model": switch.model_code,
                    "error": "切换失败"
                })
        except Exception as e:
            errors.append({
                "agent": f"{switch.team_name}.{switch.agent_name}",
                "model": switch.model_code,
                "error": str(e)
            })
    
    return {
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    } 