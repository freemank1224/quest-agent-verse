#!/usr/bin/env python3
"""
测试脚本 - 验证CoursePlannerAgent能够正常工作
并确认使用qwen3_32b而非grok模型
"""

import os
import sys
import logging
import json

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# 导入CoursePlannerAgent
from agents.teaching_team.course_planner import CoursePlannerAgent
from utils.model_manager import get_model_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """测试CoursePlannerAgent的基本功能"""
    # 1. 初始化Agent
    logger.info("初始化CoursePlannerAgent...")
    planner = CoursePlannerAgent()
    
    # 2. 获取当前模型信息
    model_info = planner.get_current_model_info()
    logger.info(f"当前使用模型: {model_info}")
    
    # 3. 确认使用的是qwen3_32b而非grok
    assert model_info['model_code'] == 'qwen3_32b', f"预期使用qwen3_32b，实际使用{model_info['model_code']}"
    assert model_info['provider'] == 'ollama', f"预期使用ollama提供商，实际使用{model_info['provider']}"
    
    logger.info("测试通过：CoursePlannerAgent正确使用qwen3_32b模型")
    
    # 4. 简单功能测试 - 仅测试能否正常运行，不发起实际请求
    # 这里只测试是否能获取配置和记忆管理
    assert planner.memory_manager is not None, "记忆管理器初始化失败"
    assert planner.course_memory is not None, "课程记忆初始化失败"
    
    logger.info("测试通过：CoursePlannerAgent基础功能正常")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            logger.info("✅ 所有测试均已通过")
        else:
            logger.error("❌ 测试失败")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ 测试过程中发生错误: {e}")
        sys.exit(1)
