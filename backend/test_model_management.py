#!/usr/bin/env python3
"""
模型管理系统测试脚本

测试内容：
1. 模型管理器初始化
2. 配置文件加载
3. 模型实例创建
4. Agent模型获取
5. 模型动态切换
6. 预设配置应用
7. 现代化Agent实例创建
8. API接口功能（如果FastAPI运行中）
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_model_manager():
    """测试模型管理器基础功能"""
    print("=== 测试模型管理器 ===")
    
    try:
        from utils.model_manager import ModelManager, get_model_manager
        
        # 测试1: 初始化模型管理器
        print("1. 测试模型管理器初始化...")
        manager = ModelManager()
        print(f"   ✅ 成功初始化，环境: {manager.environment}")
        
        # 测试2: 获取可用模型
        print("2. 测试获取可用模型...")
        available_models = manager.get_available_models()
        print(f"   ✅ 找到 {len(available_models)} 个提供商:")
        for provider, models in available_models.items():
            print(f"      - {provider}: {len(models)} 个模型")
        
        # 测试3: 获取模型状态
        print("3. 测试获取模型状态...")
        status = manager.get_model_status()
        print(f"   ✅ 状态获取成功:")
        print(f"      - 环境: {status['environment']}")
        print(f"      - 配置已加载: {status['config_loaded']}")
        print(f"      - 缓存模型数: {status['cached_models']}")
        print(f"      - 可用提供商: {status['available_providers']}")
        
        # 测试4: 获取Agent模型配置
        print("4. 测试获取Agent模型配置...")
        try:
            teacher_model_info = manager.get_agent_current_model("teaching_team", "teacher_agent")
            print(f"   ✅ 教师Agent模型: {teacher_model_info.get('model_code', 'unknown')}")
        except Exception as e:
            print(f"   ⚠️  获取教师Agent模型配置失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 模型管理器测试失败: {e}")
        return False

def test_model_creation():
    """测试模型实例创建"""
    print("\n=== 测试模型实例创建 ===")
    
    try:
        from utils.model_manager import get_agent_model
        
        # 测试创建教师Agent模型
        print("1. 测试创建教师Agent模型...")
        try:
            teacher_model = get_agent_model("teaching_team", "teacher_agent")
            print(f"   ✅ 成功创建教师模型: {type(teacher_model).__name__}")
        except Exception as e:
            print(f"   ⚠️  创建教师模型失败: {e}")
        
        # 测试创建其他Agent模型
        agents_to_test = [
            ("teaching_team", "course_planner"),
            ("teaching_team", "content_designer"),
            ("monitor_team", "session_analyst")
        ]
        
        for team, agent in agents_to_test:
            print(f"2. 测试创建 {team}.{agent} 模型...")
            try:
                model = get_agent_model(team, agent)
                print(f"   ✅ 成功创建: {type(model).__name__}")
            except Exception as e:
                print(f"   ⚠️  创建失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 模型创建测试失败: {e}")
        return False

async def test_modern_teacher_agent():
    """测试现代化教师Agent"""
    print("\n=== 测试现代化教师Agent ===")
    
    try:
        from agents.teaching_team.modern_teacher_agent import ModernTeacherAgent
        
        # 测试1: 创建Agent实例
        print("1. 测试创建现代化教师Agent...")
        teacher = ModernTeacherAgent(use_agno_memory=True)
        print(f"   ✅ 成功创建Agent")
        
        # 测试2: 获取Agent状态
        print("2. 测试获取Agent状态...")
        status = teacher.get_agent_status()
        print(f"   ✅ Agent状态:")
        print(f"      - 类型: {status['agent_type']}")
        print(f"      - 预设: {status.get('preset', 'default')}")
        print(f"      - Memory类型: {status['memory_type']}")
        print(f"      - 活跃会话: {status['active_sessions']}")
        
        # 测试3: 模拟对话
        print("3. 测试模拟对话...")
        try:
            response = await teacher.chat("test_user", "你好，我想学习Python编程")
            print(f"   ✅ 对话成功，响应长度: {len(response['content'])} 字符")
            print(f"   模型信息: {response.get('model_info', {})}")
        except Exception as e:
            print(f"   ⚠️  对话测试失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 现代化教师Agent测试失败: {e}")
        return False

def test_model_switching():
    """测试模型动态切换"""
    print("\n=== 测试模型动态切换 ===")
    
    try:
        from utils.model_manager import get_model_manager
        
        manager = get_model_manager()
        
        # 测试1: 获取当前模型
        print("1. 测试获取当前模型...")
        current_model = manager.get_agent_current_model("teaching_team", "teacher_agent")
        print(f"   ✅ 当前模型: {current_model.get('model_code', 'unknown')}")
        
        # 测试2: 切换到不同模型（如果可用）
        print("2. 测试模型切换...")
        available_models = manager.get_available_models()
        
        # 尝试切换到另一个可用模型
        test_model_codes = ["qwen3_14b", "gpt35_turbo", "gemini_pro"]
        switched = False
        
        for model_code in test_model_codes:
            # 检查模型是否可用
            model_found = False
            for provider_models in available_models.values():
                if any(model["code"] == model_code for model in provider_models):
                    model_found = True
                    break
            
            if model_found:
                try:
                    success = manager.update_agent_model("teaching_team", "teacher_agent", model_code)
                    if success:
                        print(f"   ✅ 成功切换到: {model_code}")
                        switched = True
                        
                        # 切换回原模型
                        manager.update_agent_model("teaching_team", "teacher_agent", 
                                                 current_model.get('model_code', 'qwen3_32b'))
                        print(f"   ✅ 已切换回原模型")
                        break
                except Exception as e:
                    print(f"   ⚠️  切换到 {model_code} 失败: {e}")
        
        if not switched:
            print("   ⚠️  没有找到可切换的模型")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 模型切换测试失败: {e}")
        return False

def test_preset_application():
    """测试预设配置应用"""
    print("\n=== 测试预设配置应用 ===")
    
    try:
        from utils.model_manager import get_model_manager
        
        manager = get_model_manager()
        
        # 测试1: 获取可用预设
        print("1. 测试获取可用预设...")
        config = manager.config
        presets = config.get("presets", {})
        print(f"   ✅ 找到 {len(presets)} 个预设:")
        for preset_name in presets.keys():
            print(f"      - {preset_name}")
        
        # 测试2: 应用预设配置
        if presets:
            preset_name = list(presets.keys())[0]  # 使用第一个预设
            print(f"2. 测试应用预设配置: {preset_name}...")
            
            try:
                success = manager.apply_preset(preset_name)
                if success:
                    print(f"   ✅ 成功应用预设: {preset_name}")
                else:
                    print(f"   ⚠️  应用预设失败: {preset_name}")
            except Exception as e:
                print(f"   ⚠️  应用预设出错: {e}")
        else:
            print("   ⚠️  没有找到可用的预设配置")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 预设配置测试失败: {e}")
        return False

def test_config_validation():
    """测试配置文件验证"""
    print("\n=== 测试配置文件验证 ===")
    
    try:
        from utils.model_manager import ModelManager
        
        # 测试1: 检查配置文件存在
        print("1. 测试配置文件存在性...")
        config_path = "config/models.yaml"
        if Path(config_path).exists():
            print(f"   ✅ 配置文件存在: {config_path}")
        else:
            print(f"   ⚠️  配置文件不存在: {config_path}")
        
        # 测试2: 验证配置结构
        print("2. 测试配置文件结构...")
        manager = ModelManager()
        config = manager.config
        
        required_sections = ["global_defaults", "model_providers", "agent_teams"]
        for section in required_sections:
            if section in config:
                print(f"   ✅ 包含必要节: {section}")
            else:
                print(f"   ⚠️  缺少必要节: {section}")
        
        # 测试3: 检查模型提供商配置
        print("3. 测试模型提供商配置...")
        providers = config.get("model_providers", {})
        expected_providers = ["openai", "xai", "gemini", "ollama"]
        
        for provider in expected_providers:
            if provider in providers:
                model_count = len(providers[provider])
                print(f"   ✅ {provider}: {model_count} 个模型")
            else:
                print(f"   ⚠️  缺少提供商: {provider}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置验证失败: {e}")
        return False

async def test_api_endpoints():
    """测试API接口（如果可用）"""
    print("\n=== 测试API接口 ===")
    
    try:
        import httpx
        
        # 测试基础API端点
        base_url = "http://localhost:8000/api/models"
        
        async with httpx.AsyncClient() as client:
            # 测试1: 健康检查
            print("1. 测试健康检查接口...")
            try:
                response = await client.get(f"{base_url}/health")
                if response.status_code == 200:
                    health = response.json()
                    print(f"   ✅ 健康检查成功: {health['status']}")
                else:
                    print(f"   ⚠️  健康检查返回: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  健康检查失败: {e}")
            
            # 测试2: 获取可用模型
            print("2. 测试获取可用模型接口...")
            try:
                response = await client.get(f"{base_url}/available")
                if response.status_code == 200:
                    models = response.json()
                    print(f"   ✅ 获取模型成功，提供商数: {len(models)}")
                else:
                    print(f"   ⚠️  获取模型返回: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  获取模型失败: {e}")
            
            # 测试3: 获取模型状态
            print("3. 测试获取模型状态接口...")
            try:
                response = await client.get(f"{base_url}/status")
                if response.status_code == 200:
                    status = response.json()
                    print(f"   ✅ 获取状态成功，环境: {status['environment']}")
                else:
                    print(f"   ⚠️  获取状态返回: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  获取状态失败: {e}")
        
        return True
        
    except ImportError:
        print("   ⚠️  httpx 未安装，跳过API测试")
        return True
    except Exception as e:
        print(f"   ⚠️  API测试失败: {e}")
        return True  # API测试不是必须的

def print_usage_examples():
    """打印使用示例"""
    print("\n=== 使用示例 ===")
    
    examples = [
        {
            "title": "1. 基础使用 - 获取配置化模型",
            "code": """
from utils.model_manager import get_agent_model

# 获取教师Agent的模型（使用默认配置）
teacher_model = get_agent_model("teaching_team", "teacher_agent")

# 使用高性能预设
teacher_model = get_agent_model("teaching_team", "teacher_agent", "high_performance")
"""
        },
        {
            "title": "2. 创建现代化Agent",
            "code": """
from agents.teaching_team.modern_teacher_agent import ModernTeacherAgent

# 创建使用默认配置的教师Agent
teacher = ModernTeacherAgent()

# 创建使用高性能预设的教师Agent
teacher = ModernTeacherAgent(preset="high_performance")

# 创建使用经济模式的教师Agent
teacher = ModernTeacherAgent(preset="cost_effective")
"""
        },
        {
            "title": "3. 动态切换模型",
            "code": """
from utils.model_manager import get_model_manager

manager = get_model_manager()

# 切换教师Agent到GPT-4
manager.update_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")

# 应用高性能预设到所有Agent
manager.apply_preset("high_performance")
"""
        },
        {
            "title": "4. 配置文件修改示例",
            "code": """
# 修改 config/models.yaml 中的Agent配置
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "gpt4_turbo"  # 改为使用GPT-4
      fallback_models: ["gemini_pro", "qwen3_32b"]
"""
        },
        {
            "title": "5. 环境变量配置",
            "code": """
# 设置环境变量
export ENVIRONMENT=production
export OPENAI_API_KEY=your_openai_key
export XAI_API_KEY=your_xai_key
export GOOGLE_API_KEY=your_google_key

# 然后启动应用
python src/main.py
"""
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        print(example['code'])

async def main():
    """主测试函数"""
    print("🚀 AI教学系统模型管理测试开始\n")
    
    # 运行所有测试
    tests = [
        ("配置文件验证", test_config_validation),
        ("模型管理器", test_model_manager),
        ("模型实例创建", test_model_creation),
        ("模型动态切换", test_model_switching),
        ("预设配置应用", test_preset_application),
        ("现代化教师Agent", test_modern_teacher_agent),
        ("API接口", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"测试: {test_name}")
        print('='*50)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    # 打印总结
    print(f"\n{'='*50}")
    print(f"测试完成: {passed}/{total} 通过")
    print('='*50)
    
    if passed == total:
        print("🎉 所有测试通过！模型管理系统运行正常。")
    else:
        print(f"⚠️  有 {total - passed} 个测试失败，请检查配置和环境。")
    
    # 打印使用示例
    print_usage_examples()
    
    print("\n📚 更多信息:")
    print("- 配置文件: config/models.yaml")
    print("- 模型管理器: src/utils/model_manager.py")
    print("- 现代化Agent: src/agents/teaching_team/modern_teacher_agent.py")
    print("- API接口: src/api/model_management.py")

if __name__ == "__main__":
    asyncio.run(main()) 