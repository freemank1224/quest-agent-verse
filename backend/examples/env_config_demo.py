#!/usr/bin/env python3
"""
环境配置使用演示

展示如何使用参考 agno 框架的API密钥管理方式来配置AI教学系统
"""

import sys
import os
sys.path.append('../src')

from config.env_config import get_env_config, get_api_key, validate_environment
from utils.model_manager import get_model_manager, get_agent_model, get_model_by_id

def demo_basic_env_config():
    """演示基本环境配置使用"""
    print("=== 基本环境配置演示 ===")
    
    # 获取环境配置实例
    env_config = get_env_config()
    
    # 获取基本配置
    print(f"当前环境: {env_config.get_environment()}")
    print(f"日志级别: {env_config.get_log_level()}")
    print(f"数据库URL: {env_config.get_database_url()}")
    print(f"模型配置路径: {env_config.get_model_config_path()}")
    
    # 获取各种配置项
    print(f"启用缓存: {env_config.get_env_bool('ENABLE_MODEL_CACHE', True)}")
    print(f"缓存TTL: {env_config.get_env_int('CACHE_TTL', 3600)}秒")
    print(f"模型超时: {env_config.get_env_int('MODEL_TIMEOUT', 30)}秒")

def demo_provider_configs():
    """演示各提供商配置获取"""
    print("\n=== 提供商配置演示 ===")
    
    env_config = get_env_config()
    
    # 各种提供商配置
    providers = [
        ("OpenAI", "openai"),
        ("xAI", "xai"), 
        ("Gemini", "gemini"),
        ("Anthropic", "anthropic"),
        ("Ollama", "ollama")
    ]
    
    for display_name, provider_name in providers:
        print(f"\n{display_name} 配置:")
        config = env_config.get_model_provider_config(provider_name)
        
        for key, value in config.items():
            if "api_key" in key.lower() and value:
                # 隐藏API密钥
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"  {key}: {masked_value}")
            else:
                print(f"  {key}: {value}")
    
    # 便捷API密钥获取
    print(f"\n便捷API密钥获取:")
    openai_key = get_api_key("openai")
    print(f"OpenAI API Key: {'已设置' if openai_key else '未设置'}")

def demo_agno_style_usage():
    """演示 agno 风格的使用方式"""
    print("\n=== Agno 风格使用演示 ===")
    
    env_config = get_env_config()
    
    # 1. 环境验证 (agno 风格)
    is_valid = validate_environment()
    print(f"环境验证结果: {'✓ 通过' if is_valid else '✗ 失败'}")
    
    # 2. API密钥状态检查 (agno 风格)
    api_status = env_config.validate_api_keys()
    print("\nAPI密钥状态 (agno 风格):")
    for provider, is_available in api_status.items():
        status_icon = "🟢" if is_available else "🔴"
        print(f"  {status_icon} {provider.upper()}: {'可用' if is_available else '不可用'}")
    
    # 3. 缺失配置提示 (agno 风格)
    missing_keys = env_config.get_missing_api_keys()
    if missing_keys:
        print(f"\n⚠️  缺失API密钥: {', '.join(missing_keys)}")
        print("💡 建议: 在 .env 文件中设置相应的环境变量")
    else:
        print("\n✅ 所有API密钥都已正确配置")

def demo_model_manager_integration():
    """演示模型管理器集成"""
    print("\n=== 模型管理器集成演示 ===")
    
    try:
        # 获取模型管理器
        manager = get_model_manager()
        
        # 显示环境信息
        env_info = manager.get_environment_info()
        print("环境信息:")
        for key, value in env_info.items():
            if isinstance(value, list):
                print(f"  {key}: {', '.join(value) if value else '无'}")
            elif isinstance(value, dict):
                print(f"  {key}: {len(value)} 项")
            else:
                print(f"  {key}: {value}")
        
        # 测试Agent模型获取 - 展示新的三参数功能
        print(f"\n测试Agent模型获取 (新的三参数功能):")
        
        # 1. 使用默认配置的模型
        try:
            print("1. 使用默认配置模型...")
            teacher_model = get_agent_model("teaching_team", "teacher_agent")
            print(f"✓ teacher_agent (默认): {type(teacher_model).__name__}")
        except Exception as e:
            print(f"✗ teacher_agent (默认): {e}")
        
        # 2. 临时切换到指定模型
        try:
            print("2. 临时切换到指定模型...")
            teacher_model_gpt = get_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")
            print(f"✓ teacher_agent (指定gpt4_turbo): {type(teacher_model_gpt).__name__}")
        except Exception as e:
            print(f"✗ teacher_agent (指定gpt4_turbo): {e}")
        
        # 3. 切换到本地模型
        try:
            print("3. 切换到不同的本地模型...")
            teacher_model_qwen = get_agent_model("teaching_team", "teacher_agent", "qwen3_14b")
            print(f"✓ teacher_agent (指定qwen3_14b): {type(teacher_model_qwen).__name__}")
        except Exception as e:
            print(f"✗ teacher_agent (指定qwen3_14b): {e}")
        
        # 4. 直接获取模型 (不绑定Agent)
        try:
            print("4. 直接获取模型...")
            direct_model = get_model_by_id("llama3_8b")
            print(f"✓ 直接获取 llama3_8b: {type(direct_model).__name__}")
        except Exception as e:
            print(f"✗ 直接获取 llama3_8b: {e}")
        
        # 显示模型状态
        status = manager.get_model_status()
        print(f"\n缓存的模型数量: {status['cached_models']}")
        
    except Exception as e:
        print(f"模型管理器演示失败: {e}")

def demo_dynamic_configuration():
    """演示动态配置"""
    print("\n=== 动态配置演示 ===")
    
    manager = get_model_manager()
    
    # 显示当前配置
    current_config = manager.get_agent_current_model("teaching_team", "course_planner")
    print(f"course_planner 当前默认模型: {current_config.get('model_code', 'N/A')}")
    
    # 演示三种不同的模型获取方式
    print("\n演示三种模型获取方式:")
    
    # 方式1: 使用默认配置
    print("方式1: 使用默认配置")
    try:
        default_model = get_agent_model("teaching_team", "course_planner")
        print(f"✓ 默认模型: {type(default_model).__name__}")
    except Exception as e:
        print(f"✗ 默认模型: {e}")
    
    # 方式2: 临时指定模型 (不更改配置)
    print("方式2: 临时指定模型 (不更改配置)")
    temp_models = ["qwen3_14b", "llama3_8b", "gpt4_turbo"]
    for model_id in temp_models:
        try:
            temp_model = get_agent_model("teaching_team", "course_planner", model_id)
            print(f"✓ 临时使用 {model_id}: {type(temp_model).__name__}")
        except Exception as e:
            print(f"✗ 临时使用 {model_id}: {e}")
    
    # 方式3: 更改默认配置
    print("方式3: 更改默认配置")
    if manager.update_agent_model("teaching_team", "course_planner", "qwen3_14b"):
        print("✓ 成功更新默认配置到 qwen3_14b")
        new_config = manager.get_agent_current_model("teaching_team", "course_planner")
        print(f"新默认配置: {new_config.get('model_code', 'N/A')}")
        
        # 现在再次使用默认配置
        new_default_model = get_agent_model("teaching_team", "course_planner")
        print(f"新的默认模型: {type(new_default_model).__name__}")
    else:
        print("✗ 更新默认配置失败")
    
    # 恢复原始配置
    manager.update_agent_model("teaching_team", "course_planner", "qwen3_32b")
    print("已恢复原始配置")

def demo_best_practices():
    """演示最佳实践"""
    print("\n=== 最佳实践演示 ===")
    
    print("1. 环境文件管理:")
    print("   ✓ 使用 .env 文件存储敏感信息")
    print("   ✓ 提供 .env.example 作为模板")
    print("   ✓ 在版本控制中排除 .env 文件")
    
    print("\n2. API密钥安全:")
    print("   ✓ 支持多种环境变量名称 (OPENAI_API_KEY, GEMINI_API_KEY)")
    print("   ✓ 自动过滤占位符值")
    print("   ✓ 在日志中隐藏敏感信息")
    
    print("\n3. 配置验证:")
    print("   ✓ 启动时验证必需的配置")
    print("   ✓ 提供明确的错误信息和修复建议")
    print("   ✓ 支持部分配置的降级使用")
    
    print("\n4. 与 agno 框架兼容:")
    print("   ✓ 统一的API密钥管理方式")
    print("   ✓ 支持多种模型提供商")
    print("   ✓ 环境特定的配置策略")

def main():
    """主演示函数"""
    print("🚀 AI教学系统环境配置演示")
    print("参考 agno 框架的API密钥管理最佳实践")
    print("=" * 60)
    
    try:
        demo_basic_env_config()
        demo_provider_configs()
        demo_agno_style_usage()
        demo_model_manager_integration()
        demo_dynamic_configuration()
        demo_best_practices()
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成")
    
    # 配置建议
    env_config = get_env_config()
    missing_keys = env_config.get_missing_api_keys()
    
    if missing_keys:
        print(f"\n💡 配置建议:")
        print(f"1. 复制示例文件: cp .env.example .env")
        print(f"2. 编辑 .env 文件，设置真实的API密钥")
        print(f"3. 重启应用程序以加载新配置")
    else:
        print(f"\n🎉 所有配置都已正确设置，系统可以正常使用！")

if __name__ == "__main__":
    main() 