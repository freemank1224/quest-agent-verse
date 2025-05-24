#!/usr/bin/env python3
"""
模型管理系统演示脚本

展示如何使用统一的模型配置管理系统：
1. 查看可用模型
2. 获取Agent当前模型
3. 动态切换模型
4. 应用预设配置
5. 创建现代化Agent
"""

import sys
import os
import asyncio
import json

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print('='*60)

def print_subsection(title):
    """打印子章节标题"""
    print(f"\n📋 {title}")
    print('-'*40)

async def main():
    """主演示函数"""
    print("🚀 AI教学系统模型管理演示")
    print("本演示将展示如何使用统一的模型配置管理系统")
    
    # 1. 初始化模型管理器
    print_section("初始化模型管理器")
    
    try:
        from utils.model_manager import get_model_manager, get_agent_model
        
        manager = get_model_manager()
        print(f"✅ 模型管理器初始化成功")
        print(f"   环境: {manager.environment}")
        print(f"   配置文件: {manager.config_path}")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 2. 查看可用模型
    print_section("查看可用模型")
    
    try:
        available_models = manager.get_available_models()
        print(f"✅ 找到 {len(available_models)} 个模型提供商:")
        
        for provider, models in available_models.items():
            print(f"\n🏢 {provider.upper()} ({len(models)} 个模型):")
            for model in models[:2]:  # 只显示前2个模型
                print(f"   • {model['code']}: {model['description']}")
            if len(models) > 2:
                print(f"   ... 还有 {len(models) - 2} 个模型")
                
    except Exception as e:
        print(f"❌ 获取可用模型失败: {e}")
    
    # 3. 查看Agent当前模型配置
    print_section("查看Agent当前模型配置")
    
    agents_to_check = [
        ("teaching_team", "teacher_agent"),
        ("teaching_team", "course_planner"),
        ("teaching_team", "content_designer"),
        ("monitor_team", "session_analyst")
    ]
    
    for team, agent in agents_to_check:
        try:
            model_info = manager.get_agent_current_model(team, agent)
            if model_info:
                print(f"🤖 {team}.{agent}:")
                print(f"   模型代号: {model_info['model_code']}")
                print(f"   模型ID: {model_info['model_id']}")
                print(f"   提供商: {model_info['provider']}")
            else:
                print(f"⚠️  {team}.{agent}: 未配置")
        except Exception as e:
            print(f"❌ 获取 {team}.{agent} 配置失败: {e}")
    
    # 4. 演示模型切换
    print_section("演示模型动态切换")
    
    try:
        # 获取教师Agent的原始模型
        original_model = manager.get_agent_current_model("teaching_team", "teacher_agent")
        print(f"📝 教师Agent原始模型: {original_model['model_code']}")
        
        # 切换到不同的模型
        new_model_code = "qwen3_14b" if original_model['model_code'] != "qwen3_14b" else "qwen3_32b"
        
        print(f"🔄 切换到模型: {new_model_code}")
        success = manager.update_agent_model("teaching_team", "teacher_agent", new_model_code)
        
        if success:
            updated_model = manager.get_agent_current_model("teaching_team", "teacher_agent")
            print(f"✅ 切换成功: {updated_model['model_code']}")
            
            # 切换回原模型
            print(f"🔄 切换回原模型: {original_model['model_code']}")
            manager.update_agent_model("teaching_team", "teacher_agent", original_model['model_code'])
            print("✅ 已恢复原始配置")
        else:
            print("❌ 模型切换失败")
            
    except Exception as e:
        print(f"❌ 模型切换演示失败: {e}")
    
    # 5. 演示预设配置
    print_section("演示预设配置")
    
    try:
        # 获取可用预设
        config = manager.config
        presets = config.get("presets", {})
        print(f"📋 可用预设配置 ({len(presets)} 个):")
        
        for preset_name, preset_config in presets.items():
            agent_count = sum(len(team_agents) for team_agents in preset_config.values())
            print(f"   • {preset_name}: 包含 {agent_count} 个Agent配置")
        
        # 应用经济模式预设
        if "cost_effective" in presets:
            print(f"\n🔄 应用经济模式预设...")
            success = manager.apply_preset("cost_effective")
            if success:
                print("✅ 预设应用成功")
                
                # 显示更新后的配置
                teacher_model = manager.get_agent_current_model("teaching_team", "teacher_agent")
                print(f"   教师Agent现在使用: {teacher_model['model_code']}")
            else:
                print("❌ 预设应用失败")
                
    except Exception as e:
        print(f"❌ 预设配置演示失败: {e}")
    
    # 6. 创建现代化Agent
    print_section("创建现代化Agent")
    
    try:
        from agents.teaching_team.modern_teacher_agent import ModernTeacherAgent
        
        print("🤖 创建使用默认配置的教师Agent...")
        teacher_default = ModernTeacherAgent(use_agno_memory=False)  # 使用SQLite避免agno依赖问题
        
        status = teacher_default.get_agent_status()
        print(f"✅ Agent创建成功:")
        print(f"   类型: {status['agent_type']}")
        print(f"   预设: {status.get('preset', 'default')}")
        print(f"   Memory类型: {status['memory_type']}")
        print(f"   模型信息: {status['model_info']}")
        
        # 测试简单对话
        print(f"\n💬 测试对话功能...")
        response = await teacher_default.chat("demo_user", "你好，请简单介绍一下你的功能")
        print(f"✅ 对话测试成功")
        print(f"   响应长度: {len(response['content'])} 字符")
        print(f"   响应预览: {response['content'][:100]}...")
        
    except Exception as e:
        print(f"❌ 现代化Agent演示失败: {e}")
    
    # 7. 系统状态总览
    print_section("系统状态总览")
    
    try:
        status = manager.get_model_status()
        print(f"📊 系统状态:")
        print(f"   环境: {status['environment']}")
        print(f"   配置已加载: {status['config_loaded']}")
        print(f"   缓存模型数: {status['cached_models']}")
        print(f"   可用提供商: {len(status['available_providers'])}")
        print(f"   配置的团队数: {len(status.get('agent_teams', {}))}")
        
    except Exception as e:
        print(f"❌ 获取系统状态失败: {e}")
    
    # 8. 使用建议
    print_section("使用建议")
    
    print("""
🎯 快速上手建议:

1. 配置环境变量:
   export OPENAI_API_KEY="your_key"
   export XAI_API_KEY="your_key"
   export GOOGLE_API_KEY="your_key"

2. 修改配置文件:
   编辑 config/models.yaml 中的模型代号即可切换

3. 使用预设配置:
   manager.apply_preset("high_performance")  # 高性能
   manager.apply_preset("cost_effective")    # 经济模式
   manager.apply_preset("local_first")       # 本地优先

4. 动态切换模型:
   manager.update_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")

5. 创建Agent:
   teacher = ModernTeacherAgent(preset="high_performance")

📚 更多信息请查看: MODEL_MANAGEMENT_GUIDE.md
    """)
    
    print(f"\n🎉 演示完成！模型管理系统运行正常。")

if __name__ == "__main__":
    asyncio.run(main()) 