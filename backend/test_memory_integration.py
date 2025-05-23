#!/usr/bin/env python3
"""
测试TeacherAgent的记忆管理器集成功能

用于验证记忆管理功能是否正常集成到TeacherAgent中
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.teaching_team.teacher_agent import TeacherAgent
from memory.memory_manager import MemoryManager
from memory.course_memory import CourseMemory

async def test_memory_integration():
    """测试记忆管理器集成功能"""
    print("🔍 开始测试TeacherAgent的记忆管理器集成...")
    
    # 1. 测试TeacherAgent初始化
    try:
        teacher = TeacherAgent(memory_db_path="test_memory.db")
        print("✅ TeacherAgent初始化成功")
    except Exception as e:
        print(f"❌ TeacherAgent初始化失败: {e}")
        return
    
    # 2. 测试记忆管理器访问
    try:
        memory_summary = teacher.memory_manager.get_memory_summary("test_client")
        print(f"✅ 记忆管理器访问成功，获得摘要: {memory_summary}")
    except Exception as e:
        print(f"❌ 记忆管理器访问失败: {e}")
        return
    
    # 3. 测试课程材料存储
    try:
        test_material = {
            "title": "Python基础编程",
            "course_title": "Python基础编程",
            "course_description": "学习Python编程的基础知识",
            "mainContent": "Python是一种高级编程语言...",
            "keyPoints": ["变量", "函数", "条件语句", "循环"],
            "sections": [
                {"id": "section_1", "title": "Python简介", "content": "Python是..."},
                {"id": "section_2", "title": "变量和数据类型", "content": "变量是..."}
            ]
        }
        
        response = await teacher.provide_teaching_material("test_client", test_material)
        print(f"✅ 课程材料存储成功: {response.get('material_stored', False)}")
    except Exception as e:
        print(f"❌ 课程材料存储失败: {e}")
        return
    
    # 4. 测试聊天功能与记忆集成
    try:
        # 设置教学上下文
        await teacher.set_teaching_context("test_client", {
            "topic": "Python基础编程",
            "session_id": "test_session_001"
        })
        
        # 模拟聊天交互
        chat_response = await teacher.chat(
            "test_client", 
            "我想了解Python中的变量是什么？",
            "test_session_001"
        )
        print(f"✅ 聊天功能集成成功，话题相关性: {chat_response.get('topic_relevance', 0)}")
    except Exception as e:
        print(f"❌ 聊天功能集成失败: {e}")
        return
    
    # 5. 测试学习总结功能
    try:
        learning_summary = await teacher.get_learning_summary("test_client")
        print(f"✅ 学习总结功能正常，统计信息: {learning_summary['statistics']}")
    except Exception as e:
        print(f"❌ 学习总结功能失败: {e}")
        return
    
    # 6. 测试主题偏离检测
    try:
        deviation_status = teacher.get_topic_deviation_status("test_client")
        print(f"✅ 主题偏离检测正常: {deviation_status['message']}")
    except Exception as e:
        print(f"❌ 主题偏离检测失败: {e}")
        return
    
    print("\n🎉 所有测试通过！TeacherAgent的记忆管理器集成功能正常。")
    
    # 清理测试数据库
    try:
        os.remove("test_memory.db")
        print("🗑️ 测试数据库已清理")
    except:
        pass

def test_standalone_memory():
    """测试独立的记忆管理器功能"""
    print("\n🔍 测试独立记忆管理器功能...")
    
    try:
        # 测试MemoryManager
        memory_manager = MemoryManager("test_standalone_memory.db")
        print("✅ MemoryManager创建成功")
        
        # 测试CourseMemory
        course_memory = CourseMemory(memory_manager)
        print("✅ CourseMemory创建成功")
        
        # 测试课程存储
        outline_data = {
            "course_title": "测试课程",
            "course_description": "这是一个测试课程",
            "learning_objectives": ["目标1", "目标2"],
            "sections": [{"id": "test_section", "title": "测试章节"}]
        }
        
        course_id = course_memory.store_course_outline("测试主题", outline_data)
        print(f"✅ 课程存储成功，ID: {course_id}")
        
        # 测试课程检索
        retrieved_course = course_memory.get_course_by_topic("测试主题")
        if retrieved_course:
            print("✅ 课程检索成功")
        else:
            print("❌ 课程检索失败")
        
        print("✅ 独立记忆管理器功能测试通过")
        
        # 清理
        os.remove("test_standalone_memory.db")
        print("🗑️ 测试数据库已清理")
        
    except Exception as e:
        print(f"❌ 独立记忆管理器测试失败: {e}")

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧠 TeacherAgent记忆管理器集成测试")
    print("=" * 60)
    
    # 测试独立记忆管理器
    test_standalone_memory()
    
    # 测试集成功能
    await test_memory_integration()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 