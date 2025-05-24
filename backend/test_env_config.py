#!/usr/bin/env python3
"""
测试环境配置系统

验证参考 agno 框架的API密钥管理方式是否正常工作
"""

import sys
import os
sys.path.append('src')

from config.env_config import get_env_config, validate_environment
from utils.model_manager import get_model_manager

def test_env_config():
    """测试环境配置"""
    print("=== 环境配置测试 ===")
    
    # 获取环境配置
    env_config = get_env_config()
    
    print(f"项目根目录: {env_config.project_root}")
    print(f"环境文件路径: {env_config.env_path}")
    print(f"当前环境: {env_config.get_environment()}")
    print(f"日志级别: {env_config.get_log_level()}")
    
    print("\n=== API密钥验证 ===")
    
    # 验证各提供商配置
    providers = ["openai", "xai", "gemini", "anthropic", "ollama"]
    
    for provider in providers:
        config = env_config.get_model_provider_config(provider)
        print(f"{provider.upper()}:")
        for key, value in config.items():
            if "api_key" in key.lower():
                # 隐藏API密钥内容
                display_value = "***已设置***" if value else "未设置"
                print(f"  {key}: {display_value}")
            else:
                print(f"  {key}: {value}")
        print()
    
    # API密钥状态
    api_status = env_config.validate_api_keys()
    print("API密钥状态:")
    for provider, is_valid in api_status.items():
        status = "✓" if is_valid else "✗"
        print(f"  {provider}: {status}")
    
    missing_keys = env_config.get_missing_api_keys()
    if missing_keys:
        print(f"\n缺失的API密钥: {missing_keys}")
    else:
        print("\n所有必需的API密钥都已配置")

def test_model_manager():
    """测试模型管理器"""
    print("\n=== 模型管理器测试 ===")
    
    try:
        # 获取模型管理器
        manager = get_model_manager()
        
        # 获取状态信息
        status = manager.get_model_status()
        print("模型管理器状态:")
        print(f"  配置已加载: {status['config_loaded']}")
        print(f"  缓存的模型: {status['cached_models']}")
        print(f"  可用提供商: {status['available_providers']}")
        print(f"  当前环境: {status['environment']}")
        
        if status['missing_api_keys']:
            print(f"  缺失API密钥: {status['missing_api_keys']}")
        
        print("\nAgent团队配置:")
        for team_name, team_agents in status['agent_teams'].items():
            print(f"  {team_name}:")
            for agent_name, agent_info in team_agents.items():
                if isinstance(agent_info, dict):
                    model_code = agent_info.get('model_code', 'N/A')
                    provider = agent_info.get('provider', 'N/A')
                    print(f"    {agent_name}: {model_code} ({provider})")
        
        # 测试获取具体Agent的模型
        print("\n=== Agent模型测试 ===")
        try:
            # 测试课程规划师（使用本地模型）
            print("测试获取course_planner模型...")
            course_planner_model = manager.get_model_for_agent("teaching_team", "course_planner")
            print(f"课程规划师模型: {type(course_planner_model).__name__}")
            
            model_info = manager.get_agent_current_model("teaching_team", "course_planner")
            print(f"模型信息: {model_info}")
            
        except Exception as e:
            print(f"获取模型失败: {e}")
        
        # 环境信息
        env_info = manager.get_environment_info()
        print(f"\n环境信息:")
        print(f"  运行环境: {env_info['environment']}")
        print(f"  配置文件路径: {env_info['model_config_path']}")
        
    except Exception as e:
        print(f"模型管理器测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("AI教学系统环境配置测试")
    print("参考 agno 框架的API密钥管理方式")
    print("=" * 50)
    
    # 测试环境配置
    test_env_config()
    
    # 测试模型管理器
    test_model_manager()
    
    print("\n" + "=" * 50)
    print("测试完成")
    
    # 给出配置建议
    env_config = get_env_config()
    missing_keys = env_config.get_missing_api_keys()
    
    if missing_keys:
        print(f"\n配置建议:")
        print(f"1. 复制 .env.example 为 .env")
        print(f"2. 在 .env 文件中设置以下API密钥:")
        for provider in missing_keys:
            key_name = f"{provider.upper()}_API_KEY"
            print(f"   {key_name}=your_actual_api_key")
        print(f"3. 重启应用程序")
    else:
        print("\n✓ 所有配置都已正确设置")

if __name__ == "__main__":
    main() 