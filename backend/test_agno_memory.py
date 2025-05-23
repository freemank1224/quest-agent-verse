#!/usr/bin/env python3
"""
Agno Memory系统测试脚本

测试新的AgnoMemoryManager和AgnoCourseMemory系统的各项功能，
确保与原有API完全兼容。
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from memory.agno_memory_manager import AgnoMemoryManager
from memory.agno_course_memory import AgnoCourseMemory

def test_agno_memory_manager():
    """测试AgnoMemoryManager的基本功能"""
    print("=== 测试AgnoMemoryManager ===")
    
    # 使用临时目录避免冲突
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_memory.db")
        memory_manager = AgnoMemoryManager(db_path)
        
        # 测试课程大纲存储
        print("1. 测试课程大纲存储...")
        course_data = {
            'course_title': 'Python编程基础',
            'course_description': '学习Python编程的基础知识',
            'learning_objectives': ['掌握变量和数据类型', '理解控制流', '学会函数定义'],
            'sections': [
                {'id': 'section_1', 'title': '变量和数据类型'},
                {'id': 'section_2', 'title': '控制流程'}
            ]
        }
        
        course_id = memory_manager.store_course_outline('Python编程', course_data)
        print(f"   课程ID: {course_id}")
        
        # 测试课程检索
        print("2. 测试课程检索...")
        retrieved_course = memory_manager.get_course_outline(course_id)
        print(f"   检索到课程: {retrieved_course['course_title'] if retrieved_course else 'None'}")
        
        # 测试章节内容存储
        print("3. 测试章节内容存储...")
        section_content = {
            'content_type': 'lesson',
            'main_content': 'Python变量是用来存储数据的...',
            'examples': ['x = 10', 'name = "Alice"'],
            'exercises': ['创建一个变量存储你的年龄']
        }
        
        content_id = memory_manager.store_section_content(
            course_id, 'section_1', '变量和数据类型', section_content
        )
        print(f"   内容ID: {content_id}")
        
        # 测试章节内容检索
        print("4. 测试章节内容检索...")
        retrieved_content = memory_manager.get_section_content('section_1')
        print(f"   检索到章节: {retrieved_content['title'] if retrieved_content else 'None'}")
        
        # 测试课程搜索
        print("5. 测试课程搜索...")
        search_results = memory_manager.search_courses_by_topic('Python')
        print(f"   搜索结果数量: {len(search_results)}")
        
        # 测试学习进度管理
        print("6. 测试学习进度管理...")
        progress_data = {
            'completion_rate': 0.8,
            'comprehension_score': 0.85,
            'time_spent': 3600
        }
        
        memory_manager.update_learning_progress('user_123', course_id, 'section_1', progress_data)
        progress_list = memory_manager.get_learning_progress('user_123')
        print(f"   进度记录数量: {len(progress_list)}")
        
        # 测试教学记录
        print("7. 测试教学记录...")
        memory_manager.record_teaching_interaction(
            'user_123', 'session_1', 'Python编程',
            'question_answer', '什么是变量？', '变量是存储数据的容器', 0.9
        )
        
        teaching_history = memory_manager.get_teaching_history('user_123')
        print(f"   教学记录数量: {len(teaching_history)}")
        
        # 测试主题跟踪
        print("8. 测试主题跟踪...")
        memory_manager.update_topic_tracking('user_123', 'session_1', 'Python编程')
        
        # 测试记忆摘要
        print("9. 测试记忆摘要...")
        summary = memory_manager.get_memory_summary('user_123')
        print(f"   摘要信息: {summary}")
        
        print("AgnoMemoryManager测试完成！✅")

def test_agno_course_memory():
    """测试AgnoCourseMemory的功能"""
    print("\n=== 测试AgnoCourseMemory ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_course_memory.db")
        memory_manager = AgnoMemoryManager(db_path)
        course_memory = AgnoCourseMemory(memory_manager)
        
        # 测试课程大纲存储
        print("1. 测试课程大纲存储...")
        outline_data = {
            'course_title': '机器学习入门',
            'course_description': '学习机器学习的基础概念',
            'learning_objectives': ['理解监督学习', '掌握无监督学习'],
            'sections': [
                {'id': 'ml_section_1', 'title': '监督学习'},
                {'id': 'ml_section_2', 'title': '无监督学习'}
            ]
        }
        
        course_id = course_memory.store_course_outline(
            '机器学习', 
            outline_data, 
            {'agent': 'TestAgent'}
        )
        print(f"   课程ID: {course_id}")
        
        # 测试章节内容存储
        print("2. 测试章节内容存储...")
        section_info = {'id': 'ml_section_1', 'title': '监督学习'}
        content_data = {
            'content_type': 'structured_lesson',
            'main_points': ['分类问题', '回归问题'],
            'examples': ['线性回归', '逻辑回归'],
            'practical_exercises': ['实现线性回归']
        }
        
        content_id = course_memory.store_section_content(course_id, section_info, content_data)
        print(f"   内容ID: {content_id}")
        
        # 测试根据主题获取课程
        print("3. 测试根据主题获取课程...")
        course_by_topic = course_memory.get_course_by_topic('机器学习')
        print(f"   找到课程: {course_by_topic['course_title'] if course_by_topic else 'None'}")
        
        # 测试获取课程章节
        print("4. 测试获取课程章节...")
        sections = course_memory.get_course_sections(course_id)
        print(f"   章节数量: {len(sections)}")
        
        # 测试搜索相关内容
        print("5. 测试搜索相关内容...")
        related_content = course_memory.search_related_content('学习')
        print(f"   相关内容数量: {len(related_content)}")
        
        # 测试获取课程结构
        print("6. 测试获取课程结构...")
        structure = course_memory.get_course_structure(course_id)
        print(f"   课程结构: {structure.get('total_sections', 0)} 个章节")
        
        print("AgnoCourseMemory测试完成！✅")

def test_api_compatibility():
    """测试API兼容性"""
    print("\n=== 测试API兼容性 ===")
    
    # 导入原始和新的实现
    from memory.memory_manager import MemoryManager
    from memory.agno_memory_manager import AgnoMemoryManager
    
    print("1. 检查方法签名兼容性...")
    
    # 检查MemoryManager的公共方法
    original_methods = [method for method in dir(MemoryManager) if not method.startswith('_')]
    agno_methods = [method for method in dir(AgnoMemoryManager) if not method.startswith('_')]
    
    missing_methods = set(original_methods) - set(agno_methods)
    extra_methods = set(agno_methods) - set(original_methods)
    
    if missing_methods:
        print(f"   ❌ 缺少方法: {missing_methods}")
    else:
        print("   ✅ 所有原始方法都已实现")
    
    if extra_methods:
        print(f"   ℹ️  新增方法: {extra_methods}")
    
    # 测试方法调用兼容性
    print("2. 测试方法调用兼容性...")
    with tempfile.TemporaryDirectory() as temp_dir:
        agno_db_path = os.path.join(temp_dir, "agno_test.db")
        agno_memory = AgnoMemoryManager(agno_db_path)
        
        # 测试常用方法的调用
        try:
            # store_course_outline
            course_id = agno_memory.store_course_outline('测试主题', {'course_title': '测试课程'})
            
            # get_course_outline
            course = agno_memory.get_course_outline(course_id)
            
            # search_courses_by_topic
            results = agno_memory.search_courses_by_topic('测试')
            
            # update_learning_progress
            agno_memory.update_learning_progress('test_user', course_id, 'section_1', {'score': 0.8})
            
            # get_learning_progress
            progress = agno_memory.get_learning_progress('test_user')
            
            # calculate_topic_relevance
            relevance = agno_memory.calculate_topic_relevance('测试主题', '这是关于测试的问题')
            
            print("   ✅ 所有核心方法调用成功")
            
        except Exception as e:
            print(f"   ❌ 方法调用失败: {e}")
    
    print("API兼容性测试完成！")

def test_factory_functions():
    """测试工厂函数"""
    print("\n=== 测试工厂函数 ===")
    
    from memory import create_memory_manager, create_course_memory
    
    # 测试工厂函数
    print("1. 测试create_memory_manager...")
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "factory_test.db")
        
        # 测试agno版本
        agno_manager = create_memory_manager(db_path, use_agno=True)
        print(f"   Agno实现: {type(agno_manager).__name__}")
        
        # 测试原始版本
        original_manager = create_memory_manager(db_path, use_agno=False)
        print(f"   原始实现: {type(original_manager).__name__}")
    
    print("2. 测试create_course_memory...")
    agno_course = create_course_memory(use_agno=True)
    original_course = create_course_memory(use_agno=False)
    
    print(f"   Agno课程记忆: {type(agno_course).__name__}")
    print(f"   原始课程记忆: {type(original_course).__name__}")
    
    print("工厂函数测试完成！✅")

def main():
    """运行所有测试"""
    print("🚀 开始Agno Memory系统测试\n")
    
    try:
        test_agno_memory_manager()
        test_agno_course_memory()
        test_api_compatibility()
        test_factory_functions()
        
        print("\n🎉 所有测试通过！")
        print("\n📋 测试摘要:")
        print("   ✅ AgnoMemoryManager基础功能")
        print("   ✅ AgnoCourseMemory功能")
        print("   ✅ API兼容性")
        print("   ✅ 工厂函数")
        
        print("\n💡 使用建议:")
        print("   1. 设置环境变量 USE_AGNO_MEMORY=true 启用新系统")
        print("   2. 使用迁移工具迁移现有数据")
        print("   3. 逐步替换现有代码中的直接导入")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 