#!/usr/bin/env python3
"""
模型切换功能测试

验证新的 model_id 参数功能，支持动态指定具体模型
"""

import sys
import os
sys.path.append('src')

from utils.model_manager import get_agent_model, get_model_by_id, list_available_models, get_model_manager

def test_default_model():
    """测试默认模型获取"""
    print("=== 测试默认模型获取 ===")
    
    try:
        # 使用默认配置的模型
        default_model = get_agent_model("teaching_team", "course_planner")
        print(f"✓ 默认模型: {type(default_model).__name__}")
        
        # 获取当前配置信息
        manager = get_model_manager()
        config = manager.get_agent_current_model("teaching_team", "course_planner")
        print(f"✓ 默认配置: {config['model_code']} ({config['provider']})")
        
    except Exception as e:
        print(f"✗ 默认模型获取失败: {e}")

def test_specific_model_switching():
    """测试指定模型切换"""
    print("\n=== 测试指定模型切换 ===")
    
    # 测试不同的模型
    test_models = [
        "qwen3_32b",    # 本地Ollama模型
        "qwen3_14b",    # 另一个本地模型
        "llama3_8b",    # 第三个本地模型
        "gpt4_turbo",   # OpenAI模型 (可能需要API密钥)
        "grok_beta",    # xAI模型 (可能需要API密钥)
    ]
    
    for model_id in test_models:
        try:
            print(f"\n测试切换到模型: {model_id}")
            
            # 使用指定模型
            model = get_agent_model("teaching_team", "course_planner", model_id)
            print(f"✓ 成功切换到: {model_id} ({type(model).__name__})")
            
        except Exception as e:
            print(f"✗ 切换到 {model_id} 失败: {e}")

def test_direct_model_access():
    """测试直接模型访问"""
    print("\n=== 测试直接模型访问 ===")
    
    test_models = ["qwen3_32b", "qwen3_14b", "llama3_8b"]
    
    for model_id in test_models:
        try:
            print(f"\n直接获取模型: {model_id}")
            
            # 直接通过ID获取模型
            model = get_model_by_id(model_id)
            print(f"✓ 直接获取成功: {model_id} ({type(model).__name__})")
            
        except Exception as e:
            print(f"✗ 直接获取 {model_id} 失败: {e}")

def test_model_caching():
    """测试模型缓存机制"""
    print("\n=== 测试模型缓存机制 ===")
    
    try:
        # 第一次获取模型（会创建并缓存）
        print("第一次获取模型 (创建缓存):")
        model1 = get_agent_model("teaching_team", "teacher_agent", "qwen3_32b")
        print(f"✓ 第一次获取: {type(model1).__name__}")
        
        # 第二次获取相同模型（应该从缓存获取）
        print("第二次获取相同模型 (从缓存):")
        model2 = get_agent_model("teaching_team", "teacher_agent", "qwen3_32b")
        print(f"✓ 第二次获取: {type(model2).__name__}")
        
        # 验证是否是同一个实例
        if model1 is model2:
            print("✓ 缓存生效 - 返回了相同的模型实例")
        else:
            print("? 可能创建了新实例（缓存键不同）")
        
        # 获取不同模型（应该创建新实例）
        print("获取不同模型:")
        model3 = get_agent_model("teaching_team", "teacher_agent", "qwen3_14b")
        print(f"✓ 不同模型获取: {type(model3).__name__}")
        
    except Exception as e:
        print(f"✗ 缓存测试失败: {e}")

def test_available_models():
    """测试可用模型列表"""
    print("\n=== 测试可用模型列表 ===")
    
    try:
        models = list_available_models()
        
        print("可用模型提供商:")
        for provider, model_list in models.items():
            print(f"\n{provider.upper()}:")
            for model_info in model_list:
                if isinstance(model_info, dict):
                    print(f"  - {model_info['code']}: {model_info['description']}")
                else:
                    print(f"  - {model_info}")
        
    except Exception as e:
        print(f"✗ 获取可用模型失败: {e}")

def test_mixed_usage_scenarios():
    """测试混合使用场景"""
    print("\n=== 测试混合使用场景 ===")
    
    scenarios = [
        {
            "name": "场景1: 同一个Agent使用不同模型",
            "calls": [
                ("teaching_team", "teacher_agent", None),          # 默认模型
                ("teaching_team", "teacher_agent", "qwen3_14b"),   # 指定模型
                ("teaching_team", "teacher_agent", None),          # 再次使用默认
            ]
        },
        {
            "name": "场景2: 不同Agent使用相同指定模型",
            "calls": [
                ("teaching_team", "teacher_agent", "qwen3_32b"),
                ("teaching_team", "course_planner", "qwen3_32b"),
                ("learning_team", "learning_analyst", "qwen3_32b"),
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        
        for i, (team, agent, model_id) in enumerate(scenario['calls'], 1):
            try:
                model = get_agent_model(team, agent, model_id)
                model_desc = model_id or "默认"
                print(f"  {i}. {team}.{agent} -> {model_desc}: ✓ {type(model).__name__}")
            except Exception as e:
                print(f"  {i}. {team}.{agent} -> {model_id or '默认'}: ✗ {e}")

def main():
    """主测试函数"""
    print("🚀 模型切换功能测试")
    print("验证新的 model_id 参数功能")
    print("=" * 50)
    
    try:
        test_default_model()
        test_specific_model_switching()
        test_direct_model_access()
        test_model_caching()
        test_available_models()
        test_mixed_usage_scenarios()
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ 模型切换功能测试完成")
    
    print(f"\n💡 使用示例:")
    print(f"# 使用默认配置的模型")
    print(f"model = get_agent_model('teaching_team', 'teacher_agent')")
    print(f"")
    print(f"# 临时切换到指定模型")
    print(f"model = get_agent_model('teaching_team', 'teacher_agent', 'gpt4_turbo')")
    print(f"")
    print(f"# 直接获取指定模型")
    print(f"model = get_model_by_id('qwen3_32b')")

if __name__ == "__main__":
    main() 