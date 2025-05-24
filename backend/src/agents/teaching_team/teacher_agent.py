import logging
from typing import Dict, Any, Optional
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
            model=Ollama(id="qwen3:32b", host="http://localhost:11434"),
            memory=Memory(),
            tools=[
                ReasoningTools(),
                DuckDuckGoTools()
            ],
            description="""
            你是一个专业的教师AI助手，负责执行教学内容并与学习者进行互动。你的任务是：
            1. 讲解课程内容和知识点，确保学习者理解
            2. 回答学习者提出的问题，给予详细且准确的解释
            3. 根据学习者反馈调整教学方式，以提高理解和参与度
            4. 提供例题和练习，帮助学习者巩固所学知识
            5. 识别学习者的困惑点，提供针对性的解释和补充材料
            6. 跟踪学习者的学习进度和理解程度
            7. 保持学习主题的连贯性，适时引导偏离的话题回到正轨
            
            你应当表现出教师的专业性，同时保持亲切友好的态度，鼓励学习者积极思考和提问。
            你的语言应当清晰、简洁，避免过于学术化的表达，使内容易于理解。
            当需要解释复杂概念时，应当使用类比、示例和可视化描述来帮助理解。
            
            你的回应应当结构清晰，包括:
            - 直接回答问题或解释概念
            - 相关的例子或应用场景
            - 适当的延伸思考或知识链接
            - 鼓励继续探索的提示
            
            在与学习者互动时，你应当：
            - 积极肯定学习者的正确理解和进步
            - 耐心纠正错误概念，不使用负面或批评性语言
            - 尊重学习者的不同学习节奏和风格
            - 鼓励批判性思维和创造性问题解决
            - 基于学习历史提供个性化的学习建议
            """
        )
        
        # 初始化记忆管理器
        self.memory_manager = MemoryManager(memory_db_path)
        
        # 存储客户端会话信息
        self.client_sessions = {}
        logger.info(f"TeacherAgent initialized with memory manager: {memory_db_path}")
    
    async def chat(self, client_id: str, message_content: str, user_background: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理来自客户端的聊天消息，集成记忆管理功能
        
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
        
        # 计算主题相关性
        topic_relevance = self.memory_manager.calculate_topic_relevance(
            current_topic, message_content
        )
        
        # 检查是否偏离主题
        is_off_topic = self.memory_manager.check_topic_deviation(
            client_id, session_id, threshold=0.3
        )
        
        # 准备发送给Agent的消息
        user_message = Message(
            role="user",
            content=message_content
        )
        
        # 获取学习历史和进度信息
        learning_history = self.memory_manager.get_teaching_history(
            client_id, session_id, limit=5
        )
        memory_summary = self.memory_manager.get_memory_summary(client_id)
        
        # 构建包含上下文的提示
        context_info = []
        
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
                context_info.append("用户背景信息：\n" + "\n".join(background_context))
                context_info.append("请根据用户背景调整回答的难度、语言风格和教学方法")
        
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
        
        # 如果有上下文信息，添加到消息中
        if context_info:
            enhanced_content = f"[教学上下文]\n{chr(10).join(context_info)}\n\n[学习者问题]\n{message_content}"
            final_message = Message(
                role="user",
                content=enhanced_content
            )
        else:
            final_message = user_message
        
        # 记录用户消息到会话历史
        self.client_sessions[client_id]["history"].append({
            "role": "user",
            "content": message_content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 调用Agent处理消息
        response = await self.agent.arun(final_message)
        
        # 处理Agent的响应
        agent_response = response.content
        
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
        
        # 返回响应给前端
        return {
            "content": agent_response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "topic_relevance": topic_relevance,
            "is_off_topic": is_off_topic
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