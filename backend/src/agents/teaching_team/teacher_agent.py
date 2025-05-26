import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import re
import uuid

from agno.agent import Agent, Message
from agno.models.ollama import Ollama
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2 import Memory

# 导入记忆管理器 - 使用绝对导入
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from memory.memory_manager import MemoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TeacherAgent:
    """
    Teacher Agent负责执行课程内容，通过对话形式与学习者互动
    这个Agent是互动学习系统的核心组件，负责：
    1. 执行ContentDesigner生成的课程内容
    2. 以对话形式与学习者互动，回答问题
    3. 根据学习者反馈调整教学方式
    4. 进行知识点讲解、例题演示和练习问题设计
    5. 集成记忆管理功能，跟踪学习进度和教学历史
    """
    
    def __init__(self, memory_db_path: str = "memory/teaching_memory.db"):
        # 使用 Ollama 作为主要模型
        self.agent = Agent(
            name="Teacher",
            model=xAI(id="grok-3-mini-beta", api_key=os.environ.get('XAI_API_KEY')),
            # model=Ollama(id="qwen3:32b", host="http://localhost:11434"),
            memory=Memory(),
            tools=[
                ReasoningTools(),
                DuckDuckGoTools()
            ],
            description="""
            你是一个专业的AI教师，严格遵循以下6个核心行为准则：

            ## 准则1：共享ContentDesigner的记忆，遵循课程内容设计
            - 必须充分利用CoursePlanner制定的完整课程大纲和ContentDesigner设计的课程内容
            - 严格按照课程的整体学习目标、章节结构、布鲁姆分类层级目标进行教学
            - 理解当前教学内容在整个课程中的位置和作用，确保内容的连贯性和逻辑性
            - 根据课程的curriculum_alignment信息，确保教学符合相应的课程标准要求

            ## 准则2：提供与用户问题和课程进度紧密相关的专注回应
            - 回应必须紧密围绕用户的具体问题和当前的课程学习进度
            - 避免偏离主题的冗长解释，保持内容的针对性和相关性
            - 根据学习者的理解水平和背景信息调整回应的深度和复杂度
            - 如果用户偏离主题，温和地引导回到当前课程内容

            ## 准则3：以苏格拉底式反思问题结尾
            - 每次回应的结尾必须包含一个或多个启发性的反思问题
            - 问题应该引导学习者深入思考概念的应用、关联和意义
            - 问题类型包括：概念应用、类比思考、实际联系、深层理解、批判性分析
            - 问题应该基于刚刚讲解的内容，帮助学习者巩固和拓展理解

            ## 准则4：当用户表示理解时推进内容
            - 识别用户的理解信号："我明白了"、"我懂了"、"I understand"、"continue"、"继续"等
            - 当检测到理解信号时，主动推进到课程的下一个知识点或更深层次的内容
            - 推进时要建立与前面内容的联系，确保知识的连贯性
            - 如果当前章节内容已完成，提示可以进入下一章节的学习

            ## 准则5：使用类比、故事和游戏化方法
            - 积极使用生动的类比来解释抽象概念，让学习更容易理解
            - 融入相关的故事和案例，增加学习的趣味性和记忆性
            - 采用游戏化元素：设置学习挑战、使用积分思维、创造问题情境等
            - 根据学习者的年龄和背景选择合适的类比和故事
            - 鼓励学习者参与互动，而不仅仅是被动接受信息

            ## 准则6：内容段落完成时生成3-5个评估问题
            - 当一个重要概念或内容段落教学完成时，自动生成3-5个评估问题
            - 评估问题应该覆盖不同的认知层次：记忆、理解、应用、分析
            - 问题难度应该与学习者的背景和课程进度相匹配
            - 提供多种题型：选择题、简答题、应用题等
            - 评估应该帮助学习者检验理解程度并巩固学习成果

            ## 教学风格要求
            - 保持亲切友好且专业的态度，营造积极的学习氛围
            - 使用清晰简洁的语言，避免过于学术化的表达
            - 积极肯定学习者的进步，耐心引导困惑点的解决
            - 根据学习者的个性化需求调整教学方法和节奏
            - 始终以学习者的理解和成长为中心目标
            """
        )
        
        # 初始化记忆管理器
        self.memory_manager = MemoryManager(memory_db_path)
        
        # 存储客户端会话信息
        self.client_sessions = {}
        logger.info(f"TeacherAgent initialized with memory manager: {memory_db_path}")
    
    def get_full_course_context(self, client_id: str, current_topic: str) -> str:
        """
        获取完整的课程上下文信息，包括CoursePlanner的记忆
        
        Args:
            client_id: 客户端标识
            current_topic: 当前学习主题
            
        Returns:
            格式化的课程上下文字符串
        """
        context_parts = []
        
        try:
            # 搜索相关课程
            courses = self.memory_manager.search_courses_by_topic(current_topic)
            
            if courses:
                # 获取最相关的课程
                course = courses[0]
                course_outline = self.memory_manager.get_course_outline(course['id'])
                
                if course_outline:
                    # 添加课程基本信息
                    if 'course_title' in course_outline:
                        context_parts.append(f"课程标题: {course_outline['course_title']}")
                    if 'course_description' in course_outline:
                        context_parts.append(f"课程描述: {course_outline['course_description']}")
                    
                    # 添加学习目标
                    if 'learning_objectives' in course_outline:
                        objectives = course_outline['learning_objectives']
                        if isinstance(objectives, list) and objectives:
                            context_parts.append(f"课程学习目标: {'; '.join(objectives)}")
                    
                    # 添加布鲁姆分类层级目标
                    if 'bloom_taxonomy_objectives' in course_outline:
                        bloom_obj = course_outline['bloom_taxonomy_objectives']
                        if isinstance(bloom_obj, dict):
                            bloom_info = []
                            for level, objectives in bloom_obj.items():
                                if objectives and len(objectives) > 0:
                                    bloom_info.append(f"{level}: {'; '.join(objectives)}")
                            if bloom_info:
                                context_parts.append(f"布鲁姆分类层级目标:\n" + '\n'.join(bloom_info))
                    
                    # 添加课标对齐信息
                    if 'curriculum_alignment' in course_outline:
                        ca = course_outline['curriculum_alignment']
                        if isinstance(ca, dict):
                            context_parts.append(f"课程标准: {ca.get('standards_used', '未指定')}")
                            context_parts.append(f"课标对齐: {ca.get('alignment_overview', '未指定')}")
                        elif isinstance(ca, str):
                            context_parts.append(f"课标对齐: {ca}")
                    
                    # 添加章节结构信息
                    if 'chapters' in course_outline:
                        chapters_info = []
                        for i, chapter in enumerate(course_outline['chapters'], 1):
                            chapter_title = chapter.get('title', f'第{i}章')
                            chapters_info.append(f"第{i}章: {chapter_title}")
                        if chapters_info:
                            context_parts.append(f"课程结构:\n" + '\n'.join(chapters_info))
            
            # 如果没有找到课程上下文，提供基本信息
            if not context_parts:
                context_parts.append(f"当前学习主题: {current_topic}")
                context_parts.append("注意：未找到详细的课程设计信息，请基于主题进行教学")
        
        except Exception as e:
            logger.warning(f"Failed to get course context: {e}")
            context_parts.append(f"当前学习主题: {current_topic}")
        
        return "\n".join(context_parts)
    
    def _detect_user_intent(self, message_content: str) -> Dict[str, Any]:
        """
        检测用户意图
        
        Args:
            message_content: 用户消息内容
            
        Returns:
            包含意图类型和信心度的字典
        """
        message_lower = message_content.lower()
        
        # 检测理解/继续信号
        understanding_keywords = [
            '我明白了', '我懂了', '我理解了', '明白了', '懂了', '理解了',
            'i understand', 'i get it', 'got it', 'understand',
            'continue', '继续', '下一个', '下一步', '继续学习',
            '可以继续', '请继续', '下面讲什么'
        ]
        
        confusion_keywords = [
            '不明白', '不懂', '不理解', '困惑', '迷惑',
            '为什么', '怎么理解', '怎么回事', '搞不懂',
            "don't understand", "don't get it", "confused", "why"
        ]
        
        more_info_keywords = [
            '再讲讲', '详细说明', '举个例子', '能再解释', '更详细',
            '具体怎么', '比如说', '例如', '举例',
            'more details', 'explain more', 'give example', 'for example'
        ]
        
        question_keywords = [
            '什么是', '如何', '怎样', '能否解释', '可以说说',
            'what is', 'how to', 'can you explain', 'what does'
        ]
        
        # 检测各种意图
        intent_scores = {
            'understanding': 0,
            'confusion': 0,
            'more_info': 0,
            'question': 0
        }
        
        # 计算匹配分数
        for keyword in understanding_keywords:
            if keyword in message_lower:
                intent_scores['understanding'] += 1
        
        for keyword in confusion_keywords:
            if keyword in message_lower:
                intent_scores['confusion'] += 1
        
        for keyword in more_info_keywords:
            if keyword in message_lower:
                intent_scores['more_info'] += 1
        
        for keyword in question_keywords:
            if keyword in message_lower:
                intent_scores['question'] += 1
        
        # 检测问号
        if '?' in message_content or '？' in message_content:
            intent_scores['question'] += 1
        
        # 确定主要意图
        main_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        return {
            'primary_intent': main_intent[0] if main_intent[1] > 0 else 'general',
            'confidence': main_intent[1],
            'all_scores': intent_scores
        }
    
    def _clean_agent_response(self, response: str) -> str:
        """
        清理Agent响应内容，移除不需要的标记和格式
        
        Args:
            response: 原始响应内容
            
        Returns:
            清理后的响应内容
        """
        if not response:
            return response
            
        # 移除<think>标签及其内容
        import re
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # 移除其他可能的XML标记
        response = re.sub(r'<[^>]+>', '', response)
        
        # 清理多余的空行
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
        
        # 去除开头和结尾的空白
        response = response.strip()
        
        return response

    def _generate_socratic_question(self, topic: str, content_level: str = "basic") -> str:
        """
        生成苏格拉底式反思问题
        
        Args:
            topic: 当前话题
            content_level: 内容难度级别
            
        Returns:
            苏格拉底式问题
        """
        question_templates = {
            'basic': [
                f"你能想到{topic}在日常生活中的应用例子吗？",
                f"如果你要向朋友解释{topic}，你会怎么说？",
                f"学习{topic}对你来说意味着什么？",
                f"你觉得{topic}最有趣的地方是什么？"
            ],
            'intermediate': [
                f"你能比较一下{topic}与之前学过的概念有什么相同和不同吗？",
                f"如果{topic}的某个条件发生变化，结果会怎样？",
                f"你认为{topic}背后的原理是什么？",
                f"在什么情况下{topic}可能不适用？"
            ],
            'advanced': [
                f"你能批判性地评价{topic}的优缺点吗？",
                f"如果你要改进{topic}，你会怎么做？",
                f"你能预测{topic}在未来的发展趋势吗？",
                f"{topic}对社会/科学/技术发展有什么影响？"
            ]
        }
        
        import random
        questions = question_templates.get(content_level, question_templates['basic'])
        return random.choice(questions)
    
    def _should_generate_assessment(self, client_id: str, session_history: List[Dict]) -> bool:
        """
        判断是否应该生成评估问题
        
        Args:
            client_id: 客户端标识
            session_history: 会话历史
            
        Returns:
            是否应该生成评估
        """
        # 检查最近的交互次数
        if len(session_history) < 3:
            return False
        
        # 检查是否刚刚生成过评估
        recent_messages = session_history[-3:]
        for msg in recent_messages:
            if msg.get('role') == 'agent' and '评估问题' in msg.get('content', ''):
                return False
        
        # 检查是否有足够的内容交流
        content_exchanges = sum(1 for msg in session_history[-5:] 
                              if msg.get('role') == 'agent' and len(msg.get('content', '')) > 100)
        
        return content_exchanges >= 2
    
    async def _auto_generate_assessment(self, client_id: str, topic: str, 
                                      user_background: Optional[Dict[str, Any]] = None) -> str:
        """
        自动生成评估问题
        
        Args:
            client_id: 客户端标识
            topic: 当前主题
            user_background: 用户背景信息
            
        Returns:
            评估问题内容
        """
        # 获取学习历史来调整难度
        memory_summary = self.memory_manager.get_memory_summary(client_id)
        avg_score = memory_summary.get("average_score", 0.5)
        
        # 根据历史表现调整难度
        if avg_score < 0.5:
            difficulty = "基础"
            complexity = "简单直接"
        elif avg_score < 0.7:
            difficulty = "中等"
            complexity = "需要一定思考"
        else:
            difficulty = "进阶"
            complexity = "具有挑战性"
        
        # 构建背景信息
        background_context = ""
        if user_background:
            if user_background.get("age"):
                background_context += f"学习者年龄/年级: {user_background['age']}\n"
            if user_background.get("knowledgeLevel"):
                background_context += f"知识水平: {user_background['knowledgeLevel']}\n"
        
        assessment_prompt = f"""
        基于刚才的教学内容，为"{topic}"主题生成3-5个{difficulty}难度的评估问题。
        
        {background_context}
        学习者历史平均理解度: {avg_score:.1f}
        
        评估问题要求：
        1. 问题应该{complexity}，适合当前学习者水平
        2. 涵盖不同认知层次：记忆、理解、应用
        3. 包含多种题型：选择题、简答题、应用题
        4. 每题提供简要的答案要点
        5. 问题应该帮助巩固刚才学习的核心概念
        
        请以清晰的格式呈现这些评估问题，让学习者能够轻松理解和回答。
        """
        
        assessment_message = Message(
            role="user",
            content=assessment_prompt
        )
        
        response = await self.agent.arun(assessment_message)
        return response.content

    async def chat(self, client_id: str, message_content: str, user_background: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理来自客户端的聊天消息，集成记忆管理功能，遵循6个行为准则
        
        Args:
            client_id: 客户端标识
            message_content: 消息内容
            user_background: 用户背景信息（年龄、学习目标、时间偏好等）
            session_id: 会话ID，如果为None则自动生成
            
        Returns:
            包含响应信息的字典
        """
        # 确保会话存在
        if client_id not in self.client_sessions:
            session_id = session_id or str(uuid.uuid4())
            self.client_sessions[client_id] = {
                "session_id": session_id,
                "history": [],
                "current_topic": None,
                "learning_progress": {}
            }
            logger.info(f"New session created for client {client_id}")
        
        # 获取当前学习主题，确保不为None
        current_topic = self.client_sessions[client_id].get("current_topic")
        if not current_topic:
            current_topic = "一般学习"  # 设置默认主题
            self.client_sessions[client_id]["current_topic"] = current_topic
            logger.info(f"Set default topic for client {client_id}: {current_topic}")
        
        # 【准则1】获取完整的课程上下文信息
        course_context = self.get_full_course_context(client_id, current_topic)
        
        # 【准则4】检测用户意图
        user_intent = self._detect_user_intent(message_content)
        
        # 计算主题相关性
        topic_relevance = self.memory_manager.calculate_topic_relevance(
            current_topic, message_content
        )
        
        # 检查是否偏离主题
        is_off_topic = self.memory_manager.check_topic_deviation(
            client_id, session_id, threshold=0.3
        )
        
        # 获取学习历史和进度信息
        learning_history = self.memory_manager.get_teaching_history(
            client_id, session_id, limit=5
        )
        memory_summary = self.memory_manager.get_memory_summary(client_id)
        
        # 构建包含上下文的提示
        context_info = []
        
        # 【准则1】添加课程上下文信息
        if course_context:
            context_info.append("=== 课程设计指导 ===")
            context_info.append(course_context)
            context_info.append("请严格遵循以上课程设计进行教学，确保内容与整体课程目标一致。")
        
        # 添加用户背景信息到上下文
        if user_background:
            background_context = []
            if user_background.get("age"):
                background_context.append(f"学习者年龄/年级: {user_background['age']}")
            if user_background.get("learningGoal"):
                background_context.append(f"学习目标: {user_background['learningGoal']}")
            if user_background.get("timePreference"):
                background_context.append(f"时间偏好: {user_background['timePreference']}")
            if user_background.get("knowledgeLevel"):
                background_context.append(f"知识水平: {user_background['knowledgeLevel']}")
            if user_background.get("targetAudience"):
                background_context.append(f"目标受众: {user_background['targetAudience']}")
            
            if background_context:
                context_info.append("=== 学习者背景 ===")
                context_info.append("\n".join(background_context))
                context_info.append("请根据学习者背景调整教学方法、语言风格和内容难度。")
        
        # 【准则4】添加用户意图信息
        if user_intent['primary_intent'] != 'general':
            intent_guidance = {
                'understanding': "学习者表示理解，请确认理解程度并适当推进到下一个知识点。",
                'confusion': "学习者感到困惑，请用更简单的方式重新解释，多用类比和例子。",
                'more_info': "学习者需要更多信息，请提供详细说明和具体例子。",
                'question': "学习者提出问题，请针对性回答并确保解答透彻。"
            }
            context_info.append(f"=== 用户意图指导 ===")
            context_info.append(intent_guidance.get(user_intent['primary_intent'], ''))
        
        # 添加学习进度信息
        if current_topic and current_topic != "一般学习":
            context_info.append(f"当前学习主题: {current_topic}")
        
        if is_off_topic:
            context_info.append("注意：学习者可能偏离了当前主题，请适时引导回到正轨")
        
        if memory_summary["total_interactions"] > 0:
            context_info.append(f"学习者统计：已学习{memory_summary['course_count']}门课程，平均理解度{memory_summary['average_score']:.1f}")
        
        if learning_history:
            recent_interactions = [f"- {record['interaction_type']}: {record['content'][:50]}..." 
                                 for record in learning_history[:2]]
            context_info.append(f"最近的学习互动：\n" + "\n".join(recent_interactions))
        
        # 【准则2&3&5】构建教学行为指导
        teaching_guidance = [
            "=== 教学行为要求 ===",
            "1. 【专注回应】回应必须紧密围绕用户问题和当前课程进度",
            "2. 【苏格拉底式结尾】每次回应必须以启发性反思问题结尾",
            "3. 【教学方法】积极使用类比、故事和游戏化元素",
            "4. 【内容推进】如用户表示理解，引导至下一知识点",
            "5. 【评估时机】重要概念讲完后考虑生成评估问题"
        ]
        context_info.extend(teaching_guidance)
        
        # 构建最终消息
        if context_info:
            enhanced_content = f"[教学上下文与指导]\n{chr(10).join(context_info)}\n\n[学习者问题]\n{message_content}"
            final_message = Message(
                role="user",
                content=enhanced_content
            )
        else:
            final_message = Message(
                role="user",
                content=message_content
            )
        
        # 记录用户消息到会话历史
        self.client_sessions[client_id]["history"].append({
            "role": "user",
            "content": message_content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 调用Agent处理消息
        response = await self.agent.arun(final_message)
        agent_response = response.content
        
        # 清理响应内容，移除<think>标签和其他不需要的标记
        agent_response = self._clean_agent_response(agent_response)
        
        # 【准则3】确保苏格拉底式问题结尾（如果Agent没有包含）
        if not any(question_word in agent_response for question_word in ['？', '?', '你认为', '你觉得', '你能']):
            socratic_question = self._generate_socratic_question(current_topic)
            agent_response += f"\n\n🤔 {socratic_question}"
        
        # 记录Agent响应到会话历史
        self.client_sessions[client_id]["history"].append({
            "role": "agent",
            "content": agent_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 记录教学交互到记忆管理器
        self.memory_manager.record_teaching_interaction(
            client_id=client_id,
            session_id=session_id,
            topic=current_topic,
            interaction_type="question_answer",
            content=message_content,
            response=agent_response,
            topic_relevance=topic_relevance
        )
        
        # 更新学习进度信息
        self._update_learning_progress_with_memory(
            client_id, session_id, current_topic, message_content, agent_response
        )
        
        # 【准则6】检查是否需要生成评估问题
        session_history = self.client_sessions[client_id]["history"]
        should_assess = self._should_generate_assessment(client_id, session_history)
        assessment_content = ""
        
        if should_assess:
            try:
                assessment_content = await self._auto_generate_assessment(
                    client_id, current_topic, user_background
                )
                if assessment_content:
                    agent_response += f"\n\n📝 **学习评估**\n{assessment_content}"
                    
                    # 记录评估生成
                    self.memory_manager.record_teaching_interaction(
                        client_id=client_id,
                        session_id=session_id,
                        topic=current_topic,
                        interaction_type="assessment",
                        content="自动生成评估问题",
                        response=assessment_content,
                        topic_relevance=1.0
                    )
            except Exception as e:
                logger.warning(f"Failed to generate assessment: {e}")
        
        # 返回响应给前端
        return {
            "content": agent_response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "topic_relevance": topic_relevance,
            "is_off_topic": is_off_topic,
            "user_intent": user_intent['primary_intent'],
            "has_assessment": bool(assessment_content)
        }
    
    async def set_teaching_context(self, client_id: str, context: Dict[str, Any]) -> None:
        """
        设置教学上下文，包括当前主题、课程内容等
        
        Args:
            client_id: 客户端标识
            context: 上下文信息
        """
        session_id = context.get("session_id", str(uuid.uuid4()))
        
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = {
                "session_id": session_id,
                "history": [],
                "current_topic": None,
                "learning_progress": {}
            }
        
        # 更新上下文信息
        self.client_sessions[client_id].update(context)
        
        # 如果设置了新主题，更新主题跟踪
        if "topic" in context:
            topic = context["topic"]
            self.client_sessions[client_id]["current_topic"] = topic
            
            # 更新记忆管理器中的主题跟踪
            self.memory_manager.update_topic_tracking(
                client_id, session_id, topic
            )
            
            # 告知Agent关于当前主题的上下文
            context_message = Message(
                role="system",
                content=f"当前学习主题是: {topic}。请基于此主题回答学习者的问题。"
            )
            
            # 将上下文消息存储在会话中
            self.client_sessions[client_id]["context_message"] = context_message
            
            logger.info(f"Teaching context set for client {client_id}: {topic}")
    
    async def provide_teaching_material(self, client_id: str, material: Dict[str, Any]) -> Dict[str, Any]:
        """
        提供教学材料，例如由ContentDesigner生成的内容，并存储到记忆管理器中
        
        Args:
            client_id: 客户端标识
            material: 教学材料
            
        Returns:
            处理后的响应
        """
        session_id = self.client_sessions.get(client_id, {}).get("session_id", str(uuid.uuid4()))
        
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = {
                "session_id": session_id,
                "history": [],
                "current_topic": None,
                "learning_progress": {}
            }
        
        # 将教学材料信息添加到会话中
        self.client_sessions[client_id]["teaching_material"] = material
        
        # 如果材料包含课程信息，存储到记忆管理器
        if material.get('course_title') and material.get('sections'):
            try:
                course_id = self.memory_manager.store_course_outline(
                    topic=material.get('title', material.get('course_title', '')),
                    outline_data=material
                )
                
                # 存储章节内容
                for section in material.get('sections', []):
                    if isinstance(section, dict) and 'title' in section:
                        section_id = section.get('id', f"section_{len(material.get('sections', []))}")
                        self.memory_manager.store_section_content(
                            course_id=course_id,
                            section_id=section_id,
                            title=section['title'],
                            content_data=section
                        )
                
                logger.info(f"Course material stored with ID: {course_id}")
            except Exception as e:
                logger.warning(f"Failed to store course material: {e}")
        
        # 创建用于教学的提示
        teaching_prompt = f"""
        我需要你基于以下教学材料内容，准备一个简短的课程介绍：
        
        主题: {material.get('title', '未指定主题')}
        
        主要内容:
        {material.get('mainContent', '未提供内容')}
        
        关键点:
        {', '.join(material.get('keyPoints', ['未提供关键点']))}
        
        请提供一个友好的介绍，告诉学习者他们将学习什么，以及这些知识的重要性和应用。
        """
        
        # 调用Agent生成教学材料介绍
        intro_message = Message(
            role="user",
            content=teaching_prompt
        )
        
        response = await self.agent.arun(intro_message)
        response = response.content
        
        # 记录到会话历史
        self.client_sessions[client_id]["history"].append({
            "role": "agent",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 记录教学交互到记忆管理器
        current_topic = material.get('title', '课程介绍')
        self.memory_manager.record_teaching_interaction(
            client_id=client_id,
            session_id=session_id,
            topic=current_topic,
            interaction_type="explanation",
            content=f"提供课程材料: {current_topic}",
            response=response,
            topic_relevance=1.0
        )
        
        logger.info(f"Teaching material provided for client {client_id}: {material.get('title', 'Untitled')}")
        
        # 返回响应给前端
        return {
            "content": response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat(),
            "material_stored": True
        }
    
    async def generate_practice_questions(self, client_id: str, topic: Optional[str] = None, 
                                        difficulty: Optional[str] = None, 
                                        count: int = 3) -> Dict[str, Any]:
        """
        生成练习题，并记录到记忆管理器
        
        Args:
            client_id: 客户端标识
            topic: 题目主题，如果为None则使用当前会话主题
            difficulty: 难度 ('easy', 'medium', 'hard')
            count: 生成题目的数量
            
        Returns:
            包含题目的响应
        """
        # 确保会话存在
        session_id = self.client_sessions.get(client_id, {}).get("session_id", str(uuid.uuid4()))
        
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = {
                "session_id": session_id,
                "history": [],
                "current_topic": None,
                "learning_progress": {}
            }
        
        # 使用当前主题如果没有指定
        if topic is None:
            topic = self.client_sessions[client_id].get("current_topic", "一般知识")
        
        # 获取学习者的历史进度，调整题目难度
        memory_summary = self.memory_manager.get_memory_summary(client_id)
        avg_score = memory_summary.get("average_score", 0)
        
        # 基于历史表现调整难度
        if difficulty is None:
            if avg_score < 0.5:
                difficulty = "easy"
            elif avg_score < 0.7:
                difficulty = "medium"
            else:
                difficulty = "hard"
        
        # 调整难度描述
        difficulty_desc = ""
        if difficulty == "easy":
            difficulty_desc = "简单的，基础的"
        elif difficulty == "medium":
            difficulty_desc = "中等难度的"
        elif difficulty == "hard":
            difficulty_desc = "有挑战性的，进阶的"
        else:
            difficulty_desc = "适合学习者当前水平的"
        
        # 获取相关课程内容
        course_content = ""
        courses = self.memory_manager.search_courses_by_topic(topic)
        if courses:
            recent_course = courses[0]
            course_outline = self.memory_manager.get_course_outline(recent_course['id'])
            if course_outline:
                course_content = f"\n参考课程内容：{course_outline.get('description', '')}"
        
        # 创建生成练习题的提示
        prompt = f"""
        请针对"{topic}"主题，设计{count}道{difficulty_desc}练习题，帮助学习者巩固知识。
        
        学习者当前水平：平均理解度 {avg_score:.1f}
        {course_content}
        
        每道题目应包括：
        1. 清晰的问题陈述
        2. 如果是选择题，提供选项
        3. 正确答案
        4. 简短的解释或解题思路
        
        请以一种有组织的方式呈现这些问题，使学习者能够清晰理解并学习。
        """
        
        # 调用Agent生成练习题
        question_message = Message(
            role="user",
            content=prompt
        )
        
        response = await self.agent.arun(question_message)
        response = response.content
        
        # 记录教学交互到记忆管理器
        self.memory_manager.record_teaching_interaction(
            client_id=client_id,
            session_id=session_id,
            topic=topic,
            interaction_type="practice",
            content=f"生成{count}道{difficulty}练习题",
            response=response,
            topic_relevance=1.0
        )
        
        logger.info(f"Generated {count} practice questions on {topic} for client {client_id}")
        
        # 返回响应给前端
        return {
            "content": response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat(),
            "difficulty": difficulty,
            "topic": topic
        }
    
    async def evaluate_answer(self, client_id: str, question: str, 
                            user_answer: str) -> Dict[str, Any]:
        """
        评估用户对问题的回答，并更新学习进度
        
        Args:
            client_id: 客户端标识
            question: 问题内容
            user_answer: 用户回答
            
        Returns:
            包含评估结果的响应
        """
        session_id = self.client_sessions.get(client_id, {}).get("session_id", str(uuid.uuid4()))
        current_topic = self.client_sessions.get(client_id, {}).get("current_topic", "练习评估")
        
        # 创建评估提示
        prompt = f"""
        请评估以下问题的回答:
        
        问题:
        {question}
        
        学习者的回答:
        {user_answer}
        
        请提供:
        1. 该回答是否正确（请给出数字评分0-1）
        2. 如果有误，指出错误之处
        3. 详细的解释和正确答案
        4. 建设性的反馈和鼓励
        
        请在回答开头明确标注评分，格式：[评分: 0.X]
        """
        
        # 调用Agent进行评估
        eval_message = Message(
            role="user",
            content=prompt
        )
        
        response = await self.agent.arun(eval_message)
        response = response.content
        
        # 尝试从响应中提取评分
        score_match = re.search(r'\[评分:\s*([\d.]+)\]', response)
        comprehension_score = float(score_match.group(1)) if score_match else 0.5
        
        # 记录教学交互到记忆管理器
        self.memory_manager.record_teaching_interaction(
            client_id=client_id,
            session_id=session_id,
            topic=current_topic,
            interaction_type="answer",
            content=f"问题：{question}\n回答：{user_answer}",
            response=response,
            topic_relevance=1.0
        )
        
        # 更新学习进度
        progress_data = {
            "comprehension_score": comprehension_score,
            "question": question,
            "answer": user_answer,
            "evaluation": response
        }
        
        self.memory_manager.update_learning_progress(
            client_id=client_id,
            course_id=1,  # 默认课程ID，实际应用中应该使用真实的课程ID
            section_id=current_topic,
            progress_data=progress_data
        )
        
        logger.info(f"Evaluated answer for client {client_id}, score: {comprehension_score}")
        
        # 返回响应给前端
        return {
            "content": response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat(),
            "comprehension_score": comprehension_score
        }
    
    def _update_learning_progress_with_memory(self, client_id: str, session_id: str, 
                                             current_topic: str, user_message: str, 
                                             agent_response: str) -> None:
        """
        更新学习进度信息，包括记忆管理器中的学习进度
        
        Args:
            client_id: 客户端标识
            session_id: 会话ID
            current_topic: 当前学习主题
            user_message: 用户消息
            agent_response: 智能体响应
        """
        # 获取当前会话
        session = self.client_sessions.get(client_id, {})
        learning_progress = session.get("learning_progress", {})
        
        # 简单分析交互来更新学习进度
        # 这里使用简单的关键词匹配，实际系统可能需要更复杂的分析
        
        # 检测理解程度
        comprehension_score = 0.5  # 默认评分
        if re.search(r'我明白了|我懂了|我理解了|清楚了', user_message, re.IGNORECASE):
            learning_progress["comprehension"] = learning_progress.get("comprehension", 0) + 1
            comprehension_score = 0.8
        
        # 检测疑惑
        if re.search(r'不明白|不懂|困惑|怎么理解|为什么', user_message, re.IGNORECASE):
            learning_progress["confusion"] = learning_progress.get("confusion", 0) + 1
            comprehension_score = 0.3
        
        # 检测提问
        if re.search(r'\?|？|什么是|如何|能否解释', user_message, re.IGNORECASE):
            learning_progress["questions"] = learning_progress.get("questions", 0) + 1
            comprehension_score = 0.6
        
        # 更新交互次数
        learning_progress["interactions"] = learning_progress.get("interactions", 0) + 1
        learning_progress["comprehension_score"] = comprehension_score
        
        # 更新会话中的学习进度
        self.client_sessions[client_id]["learning_progress"] = learning_progress
        
        # 记录学习进度到记忆管理器
        # 尝试获取或创建课程ID
        try:
            courses = self.memory_manager.search_courses_by_topic(current_topic)
            course_id = courses[0]['id'] if courses else 1  # 使用找到的课程ID或默认为1
        except:
            course_id = 1  # 默认课程ID
            
        self.memory_manager.update_learning_progress(
            client_id=client_id,
            course_id=course_id,
            section_id=current_topic,
            progress_data=learning_progress
        )

    # 新增记忆管理相关方法
    
    async def get_learning_summary(self, client_id: str) -> Dict[str, Any]:
        """
        获取学习者的学习总结
        
        Args:
            client_id: 客户端标识
            
        Returns:
            学习总结信息
        """
        # 获取记忆摘要
        memory_summary = self.memory_manager.get_memory_summary(client_id)
        
        # 获取复习建议
        review_suggestions = self.memory_manager.suggest_review_content(client_id)
        
        # 获取最近的学习历史
        recent_history = self.memory_manager.get_teaching_history(client_id, limit=10)
        
        # 生成个性化的学习总结
        summary_prompt = f"""
        基于以下学习数据，为学习者生成一个个性化的学习总结：
        
        学习统计：
        - 学习课程数：{memory_summary['course_count']}
        - 完成章节数：{memory_summary['section_count']}
        - 平均理解度：{memory_summary['average_score']:.1f}
        - 总交互次数：{memory_summary['total_interactions']}
        
        最近学习的主题：
        {', '.join(memory_summary['recent_topics'])}
        
        需要复习的内容：
        {[item['title'] for item in review_suggestions]}
        
        请提供一个鼓励性的学习总结，包括：
        1. 学习成就的肯定
        2. 进步的领域
        3. 需要加强的方面
        4. 具体的学习建议
        """
        
        summary_message = Message(
            role="user",
            content=summary_prompt
        )
        
        response = await self.agent.arun(summary_message)
        
        return {
            "summary": response.content,
            "statistics": memory_summary,
            "review_suggestions": review_suggestions,
            "recent_history": recent_history[:5]  # 只返回最近5条记录
        }
    
    async def get_course_content(self, client_id: str, topic: str) -> Optional[Dict[str, Any]]:
        """
        根据主题获取课程内容
        
        Args:
            client_id: 客户端标识
            topic: 课程主题
            
        Returns:
            课程内容信息
        """
        # 搜索相关课程
        courses = self.memory_manager.search_courses_by_topic(topic)
        
        if not courses:
            return None
        
        # 获取最相关的课程
        course = courses[0]
        course_outline = self.memory_manager.get_course_outline(course['id'])
        
        if course_outline:
            # 获取章节内容
            sections_content = []
            for section in course_outline.get('sections', []):
                if isinstance(section, dict) and 'id' in section:
                    section_content = self.memory_manager.get_section_content(section['id'])
                    if section_content:
                        sections_content.append(section_content)
            
            return {
                "course_outline": course_outline,
                "sections_content": sections_content
            }
        
        return None
    
    def get_topic_deviation_status(self, client_id: str) -> Dict[str, Any]:
        """
        获取主题偏离状态
        
        Args:
            client_id: 客户端标识
            
        Returns:
            主题偏离状态信息
        """
        session_id = self.client_sessions.get(client_id, {}).get("session_id")
        if not session_id:
            return {"is_off_topic": False, "message": "暂无会话数据"}
        
        is_off_topic = self.memory_manager.check_topic_deviation(client_id, session_id)
        current_topic = self.client_sessions.get(client_id, {}).get("current_topic", "无")
        
        return {
            "is_off_topic": is_off_topic,
            "current_topic": current_topic,
            "message": "学习偏离当前主题，建议回到正轨" if is_off_topic else "学习进展正常"
        }


# 单例实例，用于服务调用
teacher = TeacherAgent()