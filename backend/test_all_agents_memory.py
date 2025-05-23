#!/usr/bin/env python3
"""
测试所有Agent的记忆管理器集成功能

验证TeacherAgent、ContentDesignerAgent和CoursePlannerAgent的记忆管理功能
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.teaching_team.teacher_agent import TeacherAgent
from agents.teaching_team.content_designer import ContentDesignerAgent
from agents.teaching_team.course_planner import CoursePlannerAgent
from memory.memory_manager import MemoryManager
from memory.course_memory import CourseMemory

async def test_course_planner_memory():
    """测试CoursePlannerAgent的记忆管理器集成"""
    print("🔍 测试CoursePlannerAgent记忆管理器集成...")
    
    try:
        # 初始化CoursePlannerAgent
        planner = CoursePlannerAgent(memory_db_path="test_planner_memory.db")
        print("✅ CoursePlannerAgent初始化成功")
        
        # 创建课程计划
        course_plan = await planner.create_course_plan(
            topic="机器学习基础",
            learning_goal="掌握机器学习的基本概念和算法",
            target_audience="初学者",
            knowledge_level="入门级",
            store_to_memory=True
        )
        
        course_id = course_plan.get('course_id')
        if course_id:
            print(f"✅ 课程计划创建并存储成功，ID: {course_id}")
        else:
            print("❌ 课程计划存储失败")
            return False
        
        # 检索课程计划
        retrieved_plan = planner.get_course_plan(course_id)
        if retrieved_plan:
            print("✅ 课程计划检索成功")
        else:
            print("❌ 课程计划检索失败")
            return False
        
        # 搜索相关课程
        search_results = planner.search_courses("机器学习")
        if search_results:
            print(f"✅ 课程搜索成功，找到{len(search_results)}个相关课程")
        else:
            print("❌ 课程搜索失败")
        
        # 清理
        os.remove("test_planner_memory.db")
        print("🗑️ 测试数据库已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ CoursePlannerAgent测试失败: {e}")
        return False

async def test_content_designer_memory():
    """测试ContentDesignerAgent的记忆管理器集成"""
    print("\n🔍 测试ContentDesignerAgent记忆管理器集成...")
    
    try:
        # 初始化ContentDesignerAgent
        designer = ContentDesignerAgent(memory_db_path="test_designer_memory.db")
        print("✅ ContentDesignerAgent初始化成功")
        
        # 首先创建一个课程大纲
        planner = CoursePlannerAgent(memory_db_path="test_designer_memory.db")
        course_plan = await planner.create_course_plan(
            topic="Python编程",
            store_to_memory=True
        )
        course_id = course_plan.get('course_id')
        
        if not course_id:
            print("❌ 无法创建课程大纲")
            return False
        
        # 创建章节内容
        section_info = {
            "id": "section_1",
            "title": "Python基础语法",
            "description": "学习Python的基础语法和概念",
            "learning_objectives": ["掌握变量和数据类型", "理解控制结构"],
            "key_points": ["变量", "数据类型", "条件语句", "循环"]
        }
        
        section_content = await designer.create_content(
            section_info=section_info,
            course_id=course_id,
            course_topic="Python编程"
        )
        
        if section_content and 'content' in section_content:
            print("✅ 章节内容创建成功")
        else:
            print("❌ 章节内容创建失败")
            return False
        
        # 检索章节内容
        retrieved_content = designer.get_section_content("section_1")
        if retrieved_content:
            print("✅ 章节内容检索成功")
        else:
            print("❌ 章节内容检索失败")
        
        # 搜索相关内容
        related_content = designer.search_related_content("Python")
        if related_content:
            print(f"✅ 相关内容搜索成功，找到{len(related_content)}个相关内容")
        else:
            print("❌ 相关内容搜索失败")
        
        # 清理
        os.remove("test_designer_memory.db")
        print("🗑️ 测试数据库已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ ContentDesignerAgent测试失败: {e}")
        return False

async def test_teacher_agent_memory():
    """测试TeacherAgent的记忆管理器集成"""
    print("\n🔍 测试TeacherAgent记忆管理器集成...")
    
    try:
        # 初始化TeacherAgent
        teacher = TeacherAgent(memory_db_path="test_teacher_memory.db")
        print("✅ TeacherAgent初始化成功")
        
        # 设置教学上下文
        await teacher.set_teaching_context("test_student", {
            "topic": "数据结构",
            "session_id": "session_001"
        })
        print("✅ 教学上下文设置成功")
        
        # 提供教学材料
        test_material = {
            "title": "数据结构基础",
            "course_title": "数据结构基础",
            "course_description": "学习基本的数据结构",
            "mainContent": "数据结构是计算机科学的基础...",
            "keyPoints": ["数组", "链表", "栈", "队列"],
            "sections": [
                {"id": "ds_1", "title": "数组和链表", "content": "数组和链表的基本概念..."},
                {"id": "ds_2", "title": "栈和队列", "content": "栈和队列的实现..."}
            ]
        }
        
        material_response = await teacher.provide_teaching_material("test_student", test_material)
        if material_response.get('material_stored'):
            print("✅ 教学材料存储成功")
        else:
            print("❌ 教学材料存储失败")
        
        # 进行聊天交互
        chat_response = await teacher.chat(
            "test_student",
            "什么是数组？",
            "session_001"
        )
        
        if chat_response.get('content'):
            print("✅ 聊天交互成功")
            print(f"   话题相关性: {chat_response.get('topic_relevance', 0)}")
        else:
            print("❌ 聊天交互失败")
        
        # 生成练习题
        practice_response = await teacher.generate_practice_questions(
            "test_student",
            topic="数据结构",
            difficulty="easy",
            count=2
        )
        
        if practice_response.get('content'):
            print("✅ 练习题生成成功")
        else:
            print("❌ 练习题生成失败")
        
        # 获取学习总结
        summary = await teacher.get_learning_summary("test_student")
        if summary.get('summary'):
            print("✅ 学习总结生成成功")
            print(f"   学习统计: {summary['statistics']}")
        else:
            print("❌ 学习总结生成失败")
        
        # 检查主题偏离状态
        deviation_status = teacher.get_topic_deviation_status("test_student")
        print(f"✅ 主题偏离检测: {deviation_status['message']}")
        
        # 清理
        os.remove("test_teacher_memory.db")
        print("🗑️ 测试数据库已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ TeacherAgent测试失败: {e}")
        return False

async def test_integrated_workflow():
    """测试完整的集成工作流程"""
    print("\n🔍 测试完整的集成工作流程...")
    
    try:
        # 使用同一个数据库进行集成测试
        db_path = "test_integrated_memory.db"
        
        # 1. 使用CoursePlannerAgent创建课程大纲
        planner = CoursePlannerAgent(memory_db_path=db_path)
        course_plan = await planner.create_course_plan(
            topic="Web开发基础",
            learning_goal="掌握Web开发的基础技能",
            store_to_memory=True
        )
        course_id = course_plan.get('course_id')
        print(f"✅ 步骤1: 课程大纲创建成功，ID: {course_id}")
        
        # 2. 使用ContentDesignerAgent为第一个章节创建内容
        designer = ContentDesignerAgent(memory_db_path=db_path)
        first_section = course_plan['sections'][0]
        section_content = await designer.create_content(
            section_info=first_section,
            course_id=course_id,
            course_topic="Web开发基础"
        )
        print("✅ 步骤2: 章节内容创建成功")
        
        # 3. 使用TeacherAgent进行教学
        teacher = TeacherAgent(memory_db_path=db_path)
        
        # 设置教学上下文
        await teacher.set_teaching_context("integrated_student", {
            "topic": "Web开发基础",
            "session_id": "integrated_session"
        })
        
        # 提供教学材料
        teaching_material = {
            "title": course_plan['course_title'],
            "course_title": course_plan['course_title'],
            "course_description": course_plan['course_description'],
            "mainContent": "Web开发是创建网站和Web应用的过程...",
            "keyPoints": ["HTML", "CSS", "JavaScript"],
            "sections": course_plan['sections']
        }
        
        await teacher.provide_teaching_material("integrated_student", teaching_material)
        print("✅ 步骤3: 教学材料提供成功")
        
        # 进行教学互动
        chat_response = await teacher.chat(
            "integrated_student",
            "Web开发需要学习哪些技术？",
            "integrated_session"
        )
        print("✅ 步骤4: 教学互动成功")
        
        # 4. 验证数据一致性
        # 检查课程是否正确存储
        stored_course = planner.get_course_plan(course_id)
        if stored_course and stored_course['course_title'] == course_plan['course_title']:
            print("✅ 步骤5: 数据一致性验证成功")
        else:
            print("❌ 步骤5: 数据一致性验证失败")
            return False
        
        # 检查学习记录
        summary = await teacher.get_learning_summary("integrated_student")
        if summary['statistics']['course_count'] > 0:
            print("✅ 步骤6: 学习记录验证成功")
        else:
            print("❌ 步骤6: 学习记录验证失败")
            return False
        
        # 清理
        os.remove(db_path)
        print("🗑️ 测试数据库已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成工作流程测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 70)
    print("🧠 所有Agent记忆管理器集成测试")
    print("=" * 70)
    
    test_results = []
    
    # 测试各个Agent的记忆管理器集成
    test_results.append(await test_course_planner_memory())
    test_results.append(await test_content_designer_memory())
    test_results.append(await test_teacher_agent_memory())
    test_results.append(await test_integrated_workflow())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 70)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！记忆管理器集成功能正常。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 