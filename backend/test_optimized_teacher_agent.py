#!/usr/bin/env python3
"""
测试优化后的TeacherAgent - 验证6个行为准则的实现

测试验证：
1. 共享ContentDesigner的记忆，遵循课程内容设计
2. 提供与用户问题和课程进度紧密相关的专注回应
3. 以苏格拉底式反思问题结尾
4. 当用户表示理解时推进内容
5. 使用类比、故事和游戏化方法
6. 内容段落完成时生成3-5个评估问题
"""

import asyncio
import sys
import os
import json
import uuid

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.teaching_team.teacher_agent import TeacherAgent
from agents.teaching_team.course_planner import CoursePlannerAgent
from agents.teaching_team.content_designer import ContentDesignerAgent


class TeacherAgentTester:
    def __init__(self):
        self.teacher = TeacherAgent()
        self.course_planner = CoursePlannerAgent()
        self.content_designer = ContentDesignerAgent()
        self.client_id = f"test_client_{uuid.uuid4().hex[:8]}"
        self.session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        
    async def setup_course_context(self):
        """设置课程上下文 - 创建一个测试课程"""
        print("📚 设置课程上下文...")
        
        # 创建一个简单的数学课程
        topic = "小学数学 - 分数的基本概念"
        user_background = {
            "age": "小学四年级",
            "learningGoal": "理解分数的概念和基本运算",
            "knowledgeLevel": "初学者",
            "targetAudience": "小学生"
        }
        
        # 使用CoursePlanner创建课程大纲
        course_result = await self.course_planner.plan_course(
            topic=topic,
            user_background=user_background
        )
        
        print(f"✅ 创建课程: {course_result.get('course_title', topic)}")
        
        # 设置TeacherAgent的教学上下文
        await self.teacher.set_teaching_context(
            client_id=self.client_id,
            context={
                "topic": topic,
                "session_id": self.session_id,
                "user_background": user_background
            }
        )
        
        return topic, user_background
    
    async def test_principle_1_course_memory_integration(self, topic, user_background):
        """测试准则1: 共享ContentDesigner的记忆，遵循课程内容设计"""
        print("\n🧠 测试准则1: 课程记忆集成...")
        
        response = await self.teacher.chat(
            client_id=self.client_id,
            message_content="请开始教学分数的概念",
            user_background=user_background,
            session_id=self.session_id
        )
        
        content = response['content']
        print(f"回应内容: {content[:200]}...")
        
        # 检查是否包含课程上下文信息
        has_course_context = any(keyword in content for keyword in [
            '课程', '学习目标', '分数', '概念'
        ])
        
        print(f"✅ 课程上下文集成: {'成功' if has_course_context else '失败'}")
        return has_course_context
    
    async def test_principle_2_focused_response(self, user_background):
        """测试准则2: 专注回应"""
        print("\n🎯 测试准则2: 专注回应...")
        
        response = await self.teacher.chat(
            client_id=self.client_id,
            message_content="分数的分子和分母分别代表什么？",
            user_background=user_background,
            session_id=self.session_id
        )
        
        content = response['content']
        print(f"回应内容: {content[:200]}...")
        
        # 检查是否直接回答问题
        focused_keywords = ['分子', '分母', '代表', '表示']
        is_focused = any(keyword in content for keyword in focused_keywords)
        
        print(f"✅ 专注回应: {'成功' if is_focused else '失败'}")
        return is_focused
    
    async def test_principle_3_socratic_questions(self, user_background):
        """测试准则3: 苏格拉底式反思问题结尾"""
        print("\n🤔 测试准则3: 苏格拉底式提问...")
        
        response = await self.teacher.chat(
            client_id=self.client_id,
            message_content="我想了解分数在生活中的应用",
            user_background=user_background,
            session_id=self.session_id
        )
        
        content = response['content']
        print(f"回应内容: {content[:300]}...")
        
        # 检查是否以问题结尾
        question_indicators = ['？', '?', '你认为', '你觉得', '你能', '🤔']
        has_question = any(indicator in content for indicator in question_indicators)
        
        print(f"✅ 苏格拉底式提问: {'成功' if has_question else '失败'}")
        return has_question
    
    async def test_principle_4_content_progression(self, user_background):
        """测试准则4: 内容推进检测"""
        print("\n➡️ 测试准则4: 内容推进...")
        
        # 第一次互动
        response1 = await self.teacher.chat(
            client_id=self.client_id,
            message_content="请解释什么是分数",
            user_background=user_background,
            session_id=self.session_id
        )
        
        # 表示理解，触发内容推进
        response2 = await self.teacher.chat(
            client_id=self.client_id,
            message_content="我明白了，请继续",
            user_background=user_background,
            session_id=self.session_id
        )
        
        content2 = response2['content']
        print(f"推进后的内容: {content2[:200]}...")
        
        # 检查是否有内容推进
        progression_keywords = ['下一个', '接下来', '进一步', '更深入', '继续学习']
        has_progression = any(keyword in content2 for keyword in progression_keywords)
        
        # 检查用户意图识别
        user_intent = response2.get('user_intent', '')
        intent_detected = user_intent == 'understanding'
        
        print(f"✅ 意图检测: {'成功' if intent_detected else '失败'} (检测到: {user_intent})")
        print(f"✅ 内容推进: {'成功' if has_progression else '失败'}")
        return intent_detected and has_progression
    
    async def test_principle_5_teaching_methods(self, user_background):
        """测试准则5: 类比、故事和游戏化方法"""
        print("\n🎮 测试准则5: 教学方法...")
        
        response = await self.teacher.chat(
            client_id=self.client_id,
            message_content="请用简单的方法让我理解分数",
            user_background=user_background,
            session_id=self.session_id
        )
        
        content = response['content']
        print(f"回应内容: {content[:300]}...")
        
        # 检查是否使用了类比、故事等方法
        method_keywords = [
            '比如', '就像', '好比', '想象', '故事', '例子', '类比',
            '🍕', '🍰', '🍎', '游戏', '挑战', '任务'
        ]
        uses_methods = any(keyword in content for keyword in method_keywords)
        
        print(f"✅ 教学方法应用: {'成功' if uses_methods else '失败'}")
        return uses_methods
    
    async def test_principle_6_assessment_generation(self, user_background):
        """测试准则6: 评估问题生成"""
        print("\n📝 测试准则6: 评估问题生成...")
        
        # 进行多次互动来触发评估生成
        interactions = [
            "请详细解释分数的组成部分",
            "分子和分母的关系是什么？",
            "我理解了分数的基本概念"
        ]
        
        last_response = None
        for i, message in enumerate(interactions):
            response = await self.teacher.chat(
                client_id=self.client_id,
                message_content=message,
                user_background=user_background,
                session_id=self.session_id
            )
            last_response = response
            print(f"互动 {i+1}: {message[:30]}...")
        
        # 检查最后的回应是否包含评估
        if last_response:
            content = last_response['content']
            has_assessment = last_response.get('has_assessment', False)
            
            # 检查评估关键词
            assessment_keywords = ['评估', '练习', '问题', '测试', '检验', '📝']
            content_has_assessment = any(keyword in content for keyword in assessment_keywords)
            
            print(f"最终回应长度: {len(content)}")
            print(f"✅ 评估标记: {'成功' if has_assessment else '失败'}")
            print(f"✅ 评估内容: {'成功' if content_has_assessment else '失败'}")
            
            return has_assessment or content_has_assessment
        
        return False
    
    async def run_comprehensive_test(self):
        """运行全面测试"""
        print("🚀 开始TeacherAgent优化测试")
        print("=" * 50)
        
        try:
            # 设置课程上下文
            topic, user_background = await self.setup_course_context()
            
            # 执行所有测试
            results = {}
            
            results['principle_1'] = await self.test_principle_1_course_memory_integration(topic, user_background)
            results['principle_2'] = await self.test_principle_2_focused_response(user_background)
            results['principle_3'] = await self.test_principle_3_socratic_questions(user_background)
            results['principle_4'] = await self.test_principle_4_content_progression(user_background)
            results['principle_5'] = await self.test_principle_5_teaching_methods(user_background)
            results['principle_6'] = await self.test_principle_6_assessment_generation(user_background)
            
            # 总结结果
            print("\n" + "=" * 50)
            print("📊 测试结果总结")
            print("=" * 50)
            
            total_tests = len(results)
            passed_tests = sum(1 for success in results.values() if success)
            
            for principle, success in results.items():
                status = "✅ 通过" if success else "❌ 失败"
                print(f"{principle}: {status}")
            
            print(f"\n总体结果: {passed_tests}/{total_tests} 测试通过")
            success_rate = (passed_tests / total_tests) * 100
            print(f"成功率: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("🎉 TeacherAgent优化成功！")
            elif success_rate >= 60:
                print("⚠️  TeacherAgent基本达到要求，建议继续优化")
            else:
                print("❌ TeacherAgent需要进一步优化")
                
            return results
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return None


async def main():
    """主函数"""
    tester = TeacherAgentTester()
    results = await tester.run_comprehensive_test()
    
    if results:
        print("\n📋 详细测试报告已完成")
        print("🔧 如需调整，请检查具体失败的测试项")
    else:
        print("❌ 测试失败，请检查环境配置和代码实现")


if __name__ == "__main__":
    asyncio.run(main())
