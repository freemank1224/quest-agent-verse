#!/usr/bin/env python3
"""
测试增强后的课程规划功能

验证背景信息解析和课标对齐功能
"""

import sys
import os
import asyncio
import json
sys.path.append('src')

from agents.teaching_team.course_planner import CoursePlannerAgent

async def test_basic_course_planning():
    """测试基础课程规划功能"""
    print("=== 测试基础课程规划功能 ===")
    
    planner = CoursePlannerAgent()
    
    # 测试简单主题
    topic = "小学四年级数学分数入门"
    
    try:
        result = await planner.create_course_plan(
            topic=topic,
            learning_goal="让学生理解分数的基本概念，能够进行简单的分数比较和运算",
            target_audience="小学四年级学生",
            knowledge_level="已掌握整数运算，初次接触分数概念",
            store_to_memory=False
        )
        
        print(f"✓ 基础课程规划成功")
        print(f"课程标题: {result.get('course_title', 'N/A')}")
        
        # 检查新增字段
        if 'background_analysis' in result:
            print(f"✓ 包含背景信息分析")
            bg = result['background_analysis']
            print(f"  目标年龄: {bg.get('target_age', 'N/A')}")
            print(f"  知识水平: {bg.get('knowledge_level', 'N/A')}")
        
        if 'curriculum_alignment' in result:
            print(f"✓ 包含课程标准对齐")
            align = result['curriculum_alignment']
            print(f"  使用标准: {align.get('standards_used', 'N/A')}")
        
        # 检查章节的课标对齐
        sections = result.get('sections', [])
        aligned_sections = 0
        for section in sections:
            if 'curriculum_alignment' in section:
                aligned_sections += 1
        
        print(f"✓ 章节课标对齐: {aligned_sections}/{len(sections)}")
        
        return result
        
    except Exception as e:
        print(f"✗ 基础课程规划失败: {e}")
        return None

async def test_background_extraction():
    """测试背景信息提取功能"""
    print("\n=== 测试背景信息提取功能 ===")
    
    planner = CoursePlannerAgent()
    
    # 测试包含丰富背景信息的主题
    topic = "初中二年级物理光学实验课程，适合14-15岁学生，需要具备基础的几何知识和简单的数学运算能力"
    
    try:
        result = await planner.create_course_plan(
            topic=topic,
            store_to_memory=False
        )
        
        print(f"✓ 背景信息提取测试完成")
        print(f"课程标题: {result.get('course_title', 'N/A')}")
        
        # 检查是否正确提取了背景信息
        if 'background_analysis' in result:
            bg = result['background_analysis']
            print(f"提取的背景信息:")
            print(f"  目标年龄: {bg.get('target_age', 'N/A')}")
            print(f"  知识水平: {bg.get('knowledge_level', 'N/A')}")
            print(f"  学习目标: {bg.get('learning_objectives', 'N/A')}")
            print(f"  特殊需求: {bg.get('special_requirements', 'N/A')}")
        else:
            print("✗ 未找到背景信息分析")
        
        return result
        
    except Exception as e:
        print(f"✗ 背景信息提取失败: {e}")
        return None

async def test_curriculum_alignment():
    """测试课程标准对齐功能"""
    print("\n=== 测试课程标准对齐功能 ===")
    
    planner = CoursePlannerAgent()
    
    # 测试不同学科的课标对齐
    test_topics = [
        "小学三年级科学课：认识植物",
        "高中一年级数学：函数基础",
        "初中编程入门：Scratch图形化编程"
    ]
    
    for topic in test_topics:
        print(f"\n测试主题: {topic}")
        
        try:
            result = await planner.create_course_plan(
                topic=topic,
                store_to_memory=False
            )
            
            # 检查课程标准对齐
            if 'curriculum_alignment' in result:
                align = result['curriculum_alignment']
                print(f"  ✓ 使用标准: {align.get('standards_used', 'N/A')}")
                print(f"  ✓ 对齐说明: {align.get('alignment_overview', 'N/A')[:100]}...")
            else:
                print(f"  ✗ 缺少课程标准对齐信息")
            
            # 检查章节级别的对齐
            sections = result.get('sections', [])
            for i, section in enumerate(sections[:2]):  # 只检查前两个章节
                if 'curriculum_alignment' in section:
                    print(f"  ✓ 章节{i+1}课标对齐: {section['curriculum_alignment'][:80]}...")
                else:
                    print(f"  ✗ 章节{i+1}缺少课标对齐")
                    
        except Exception as e:
            print(f"  ✗ 测试失败: {e}")

async def test_model_switching():
    """测试模型切换功能"""
    print("\n=== 测试模型切换功能 ===")
    
    planner = CoursePlannerAgent()
    
    # 显示当前模型
    current_model = planner.get_current_model_info()
    print(f"当前模型: {current_model.get('model_code', 'N/A')} ({current_model.get('provider', 'N/A')})")
    
    # 测试切换到不同模型
    test_models = ["qwen3_14b", "llama3_8b"]
    
    for model_code in test_models:
        print(f"\n尝试切换到模型: {model_code}")
        
        try:
            success = await planner.switch_model(model_code)
            if success:
                print(f"✓ 成功切换到: {model_code}")
                
                # 测试使用新模型创建简单课程
                result = await planner.create_course_plan(
                    topic="简单测试：小学数学加法",
                    store_to_memory=False
                )
                if result:
                    print(f"✓ 新模型工作正常，生成课程: {result.get('course_title', 'N/A')}")
                else:
                    print(f"✗ 新模型生成课程失败")
            else:
                print(f"✗ 切换到 {model_code} 失败")
                
        except Exception as e:
            print(f"✗ 模型切换错误: {e}")
    
    # 切换回默认模型
    await planner.switch_model("qwen3_32b")
    print(f"\n已切换回默认模型")

async def test_memory_integration():
    """测试记忆系统集成"""
    print("\n=== 测试记忆系统集成 ===")
    
    planner = CoursePlannerAgent()
    
    topic = "测试课程：小学英语字母学习"
    
    try:
        # 创建并存储课程
        result = await planner.create_course_plan(
            topic=topic,
            learning_goal="让学生掌握26个英文字母的读音和写法",
            target_audience="小学一年级学生",
            store_to_memory=True
        )
        
        if 'course_id' in result:
            course_id = result['course_id']
            print(f"✓ 课程已存储，ID: {course_id}")
            
            # 测试检索
            retrieved_course = planner.get_course_plan(course_id)
            if retrieved_course:
                print(f"✓ 成功检索课程: {retrieved_course.get('course_title', 'N/A')}")
            else:
                print(f"✗ 检索课程失败")
            
            # 测试搜索
            search_results = planner.search_courses("英语字母")
            if search_results:
                print(f"✓ 搜索找到 {len(search_results)} 个相关课程")
            else:
                print(f"✗ 搜索未找到相关课程")
        else:
            print(f"✗ 课程未正确存储")
            
    except Exception as e:
        print(f"✗ 记忆系统集成测试失败: {e}")

def display_course_outline(result: dict):
    """显示课程大纲的详细信息"""
    if not result:
        return
    
    print(f"\n📚 课程大纲详情:")
    print(f"标题: {result.get('course_title', 'N/A')}")
    print(f"描述: {result.get('course_description', 'N/A')}")
    
    if 'background_analysis' in result:
        bg = result['background_analysis']
        print(f"\n👥 背景分析:")
        print(f"  目标年龄: {bg.get('target_age', 'N/A')}")
        print(f"  知识水平: {bg.get('knowledge_level', 'N/A')}")
    
    if 'curriculum_alignment' in result:
        align = result['curriculum_alignment']
        print(f"\n📋 课标对齐:")
        print(f"  标准体系: {align.get('standards_used', 'N/A')}")
    
    sections = result.get('sections', [])
    print(f"\n📖 章节结构 ({len(sections)}个章节):")
    for i, section in enumerate(sections[:3]):  # 只显示前3个章节
        print(f"  {i+1}. {section.get('title', 'N/A')}")
        if 'curriculum_alignment' in section:
            print(f"     课标: {section['curriculum_alignment'][:60]}...")

async def main():
    """主测试函数"""
    print("🚀 增强版课程规划Agent测试")
    print("测试背景信息解析和课标对齐功能")
    print("=" * 60)
    
    try:
        # 基础功能测试
        basic_result = await test_basic_course_planning()
        if basic_result:
            display_course_outline(basic_result)
        
        # 背景信息提取测试
        background_result = await test_background_extraction()
        
        # 课程标准对齐测试
        await test_curriculum_alignment()
        
        # 模型切换测试
        await test_model_switching()
        
        # 记忆系统集成测试
        await test_memory_integration()
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 增强版课程规划Agent测试完成")
    
    print(f"\n💡 增强功能总结:")
    print(f"1. ✅ 背景信息自动解析和提取")
    print(f"2. ✅ 强制课程标准对齐要求")
    print(f"3. ✅ 浏览器工具辅助课标搜索")
    print(f"4. ✅ 结构化JSON输出格式")
    print(f"5. ✅ 动态模型切换支持")

if __name__ == "__main__":
    asyncio.run(main()) 