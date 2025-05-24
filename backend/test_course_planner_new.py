#!/usr/bin/env python3
"""
测试脚本 - 验证CoursePlannerAgent能够正常工作
并确认使用qwen3_32b而非grok模型
"""

import os
import sys
import logging
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """测试CoursePlannerAgent的基本功能"""
    print("导入必要模块...")
    # 导入CoursePlannerAgent
    from src.agents.teaching_team.course_planner import CoursePlannerAgent
    from src.utils.model_manager import get_model_manager
    
    # 1. 初始化Agent
    print("初始化CoursePlannerAgent...")
    planner = CoursePlannerAgent()
    
    # 2. 获取当前模型信息
    model_info = planner.get_current_model_info()
    print(f"当前使用模型: {json.dumps(model_info, ensure_ascii=False, indent=2)}")
    
    # 3. 确认使用的是qwen3_32b而非grok
    assert model_info["model_code"] == "qwen3_32b", f"预期使用qwen3_32b，实际使用{model_info['model_code']}"
    assert model_info["provider"] == "ollama", f"预期使用ollama提供商，实际使用{model_info['provider']}"
    
    print("测试通过：CoursePlannerAgent正确使用qwen3_32b模型")
    
    # 4. 简单功能测试 - 仅测试能否正常运行，不发起实际请求
    # 这里只测试是否能获取配置和记忆管理
    assert planner.memory_manager is not None, "记忆管理器初始化失败"
    assert planner.course_memory is not None, "课程记忆初始化失败"
    
    print("测试通过：CoursePlannerAgent基础功能正常")
    
    # 5. 检查模型管理器状态
    model_manager = get_model_manager()
    print("模型管理器状态:")
    print(f"配置文件已加载: {model_manager.config is not None}")
    print(f"可用提供商: {list(model_manager.config.get('model_providers', {}).keys())}")
    
    return True

if __name__ == "__main__":
    try:
        print("-" * 60)
        print("测试CoursePlannerAgent - 确认修复xAI (Grok) API问题")
        print("-" * 60)
        success = main()
        if success:
            print("\n✅ 所有测试均已通过")
        else:
            print("\n❌ 测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)
