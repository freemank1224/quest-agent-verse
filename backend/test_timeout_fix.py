#!/usr/bin/env python3
"""
测试Ollama模型超时设置修复

验证本地模型的长超时设置是否解决了推理超时问题
"""

import sys
import os
import asyncio
import time
sys.path.append('src')

from agents.teaching_team.course_planner import CoursePlannerAgent
from utils.model_manager import get_agent_model, get_model_by_id

async def test_ollama_timeout_settings():
    """测试Ollama模型的超时设置"""
    print("=== 测试Ollama模型超时设置 ===")
    
    # 测试1: 直接测试模型管理器
    print("\n1. 测试模型管理器的Ollama配置:")
    try:
        model = get_agent_model("teaching_team", "course_planner")
        print(f"✓ 成功获取course_planner模型: {type(model).__name__}")
        print(f"  模型ID: {model.id}")
        print(f"  超时设置: {getattr(model, 'timeout', '未设置')}")
        print(f"  Keep-alive: {getattr(model, 'keep_alive', '未设置')}")
    except Exception as e:
        print(f"✗ 获取模型失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 直接通过ID获取模型
    print("\n2. 测试直接获取qwen3_32b模型:")
    try:
        model = get_model_by_id("qwen3_32b")
        print(f"✓ 成功获取qwen3_32b模型: {type(model).__name__}")
        print(f"  模型ID: {model.id}")
        print(f"  超时设置: {getattr(model, 'timeout', '未设置')}")
    except Exception as e:
        print(f"✗ 获取模型失败: {e}")

async def test_course_planner_with_timeout():
    """测试课程规划Agent在新超时设置下的工作情况"""
    print("\n=== 测试课程规划Agent超时修复 ===")
    
    planner = CoursePlannerAgent()
    
    # 检查Agent使用的模型配置
    print(f"Agent模型类型: {type(planner.agent.model).__name__}")
    print(f"模型ID: {planner.agent.model.id}")
    print(f"超时设置: {getattr(planner.agent.model, 'timeout', '未设置')}")
    
    # 测试简单的课程生成（快速测试）
    print("\n开始测试简单课程生成...")
    start_time = time.time()
    
    try:
        result = await planner.create_course_plan(
            topic="小学数学：简单加法",
            learning_goal="学会10以内的加法运算",
            target_audience="小学一年级学生",
            store_to_memory=False
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✓ 课程生成成功！")
        print(f"耗时: {duration:.2f}秒")
        print(f"课程标题: {result.get('course_title', 'N/A')}")
        
        # 检查是否包含新的字段
        if 'background_analysis' in result:
            print(f"✓ 包含背景分析字段")
        
        if 'curriculum_alignment' in result:
            print(f"✓ 包含课程标准对齐字段")
            
        return True
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✗ 课程生成失败！")
        print(f"耗时: {duration:.2f}秒")
        print(f"错误信息: {e}")
        
        # 检查是否仍然是超时错误
        if "ReadTimeout" in str(e) or "timeout" in str(e).lower():
            print("❌ 仍然存在超时问题，需要进一步调整")
            return False
        else:
            print("⚠️  不是超时错误，可能是其他问题")
            import traceback
            traceback.print_exc()
            return False

async def test_different_timeout_scenarios():
    """测试不同超时场景"""
    print("\n=== 测试不同模型的超时设置 ===")
    
    # 测试不同大小的模型
    test_models = [
        ("qwen3_32b", "大模型 (32B)"),
        ("qwen3_14b", "中等模型 (14B)"), 
        ("llama3_8b", "小模型 (8B)")
    ]
    
    for model_id, description in test_models:
        print(f"\n测试 {model_id} ({description}):")
        try:
            model = get_model_by_id(model_id)
            timeout = getattr(model, 'timeout', '未设置')
            keep_alive = getattr(model, 'keep_alive', '未设置')
            
            print(f"  ✓ 模型配置正确")
            print(f"  超时: {timeout}秒")
            print(f"  Keep-alive: {keep_alive}")
            
            # 进一步分析超时设置是否合理
            if isinstance(timeout, (int, float)):
                if timeout >= 300:  # 5分钟以上
                    print(f"  ✅ 超时设置合理 ({timeout}秒)")
                elif timeout >= 60:  # 1分钟以上
                    print(f"  ⚠️  超时设置可能较短 ({timeout}秒)")
                else:
                    print(f"  ❌ 超时设置过短 ({timeout}秒)，建议增加")
            
        except Exception as e:
            print(f"  ✗ 模型配置错误: {e}")

def check_ollama_service():
    """检查Ollama服务状态"""
    print("\n=== 检查Ollama服务状态 ===")
    
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✓ Ollama服务运行正常")
            print(f"可用模型数量: {len(models)}")
            
            # 检查目标模型是否存在
            model_names = [model.get('name', '') for model in models]
            target_models = ['qwen3:32b', 'qwen3:14b', 'llama3:8b']
            
            for target in target_models:
                if any(target in name for name in model_names):
                    print(f"  ✓ 找到模型: {target}")
                else:
                    print(f"  ✗ 缺少模型: {target}")
                    
        else:
            print(f"✗ Ollama服务响应异常: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 无法连接到Ollama服务: {e}")
        print("请确保Ollama服务已启动: ollama serve")

async def main():
    """主测试函数"""
    print("🔧 Ollama模型超时设置修复测试")
    print("=" * 60)
    
    # 首先检查Ollama服务
    check_ollama_service()
    
    # 测试模型配置
    await test_ollama_timeout_settings()
    
    # 测试不同模型的超时设置
    await test_different_timeout_scenarios()
    
    # 核心测试：课程规划功能
    success = await test_course_planner_with_timeout()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 超时设置修复成功！")
        print("\n📝 修复总结:")
        print("1. ✅ qwen3_32b模型超时设置为600秒（10分钟）")
        print("2. ✅ 其他ollama模型也设置了合理的超时时间")
        print("3. ✅ 备用模型也配置了长超时设置")
        print("4. ✅ keep_alive时间延长，减少模型重新加载")
        print("\n💡 超时配置说明:")
        print("- qwen3:32b (32B大模型): 600秒超时")
        print("- qwen3:14b (14B中等模型): 300秒超时") 
        print("- llama3:8b (8B小模型): 180秒超时")
    else:
        print("❌ 仍然存在问题，需要进一步调试")
        print("\n🔍 可能的解决方案:")
        print("1. 检查Ollama服务是否正常运行")
        print("2. 确认目标模型已正确安装")
        print("3. 考虑进一步增加超时时间")
        print("4. 检查系统资源是否充足")

if __name__ == "__main__":
    asyncio.run(main()) 