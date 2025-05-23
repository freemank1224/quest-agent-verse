import logging
from typing import Dict, Any, Optional
import json
from datetime import datetime
import re

from agno.agent import Agent, Message
from agno.models.ollama import Ollama
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2 import Memory

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
    """
    
    def __init__(self):
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
            """
        )
        
        # 存储客户端会话信息
        self.client_sessions = {}
        logger.info("TeacherAgent initialized")
    
    async def chat(self, client_id: str, message_content: str) -> Dict[str, Any]:
        """
        处理来自客户端的聊天消息
        
        Args:
            client_id: 客户端标识
            message_content: 消息内容
            
        Returns:
            包含响应信息的字典
        """
        # 确保客户端会话存在
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = {
                "history": [],
                "current_topic": None,
                "learning_progress": {}
            }
            logger.info(f"New session created for client {client_id}")
        
        # 准备发送给Agent的消息
        user_message = Message(
            role="user",
            content=message_content
        )
        
        # 记录用户消息到会话历史
        self.client_sessions[client_id]["history"].append({
            "role": "user",
            "content": message_content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 如果有上下文消息，构建带上下文的提示
        final_message = user_message
        if "context_message" in self.client_sessions[client_id]:
            context = self.client_sessions[client_id]["context_message"].content
            final_message = Message(
                role="user",
                content=f"[上下文: {context}]\n\n用户问题: {message_content}"
            )
        
        # 调用Agent处理消息
        response = await self.agent.arun(final_message)
        
        # 处理Agent的响应 - 从RunResponse对象中提取content属性
        agent_response = response.content
        
        # 记录Agent响应到会话历史
        self.client_sessions[client_id]["history"].append({
            "role": "agent",
            "content": agent_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 更新学习进度信息
        self._update_learning_progress(client_id, message_content, agent_response)
        
        # 返回响应给前端
        return {
            "content": agent_response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat()
        }
    
    async def set_teaching_context(self, client_id: str, context: Dict[str, Any]) -> None:
        """
        设置教学上下文，包括当前主题、课程内容等
        
        Args:
            client_id: 客户端标识
            context: 上下文信息
        """
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = {
                "history": [],
                "current_topic": None,
                "learning_progress": {}
            }
        
        # 更新上下文信息
        self.client_sessions[client_id].update(context)
        
        # 告知Agent关于当前主题的上下文
        if "topic" in context:
            context_message = Message(
                role="system",
                content=f"当前学习主题是: {context['topic']}。请基于此主题回答学习者的问题。"
            )
            
            # 将上下文消息存储在会话中，在后续请求中使用
            self.client_sessions[client_id]["context_message"] = context_message
            
            logger.info(f"Teaching context set for client {client_id}: {context['topic']}")
    
    async def provide_teaching_material(self, client_id: str, material: Dict[str, Any]) -> Dict[str, Any]:
        """
        提供教学材料，例如由ContentDesigner生成的内容
        
        Args:
            client_id: 客户端标识
            material: 教学材料
            
        Returns:
            处理后的响应
        """
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = {
                "history": [],
                "current_topic": None,
                "learning_progress": {}
            }
        
        # 将教学材料信息添加到会话中
        self.client_sessions[client_id]["teaching_material"] = material
        
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
        
        logger.info(f"Teaching material provided for client {client_id}: {material.get('title', 'Untitled')}")
        
        # 返回响应给前端
        return {
            "content": response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_practice_questions(self, client_id: str, topic: Optional[str] = None, 
                                        difficulty: Optional[str] = None, 
                                        count: int = 3) -> Dict[str, Any]:
        """
        生成练习题
        
        Args:
            client_id: 客户端标识
            topic: 题目主题，如果为None则使用当前会话主题
            difficulty: 难度 ('easy', 'medium', 'hard')
            count: 生成题目的数量
            
        Returns:
            包含题目的响应
        """
        # 确保会话存在
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = {
                "history": [],
                "current_topic": None,
                "learning_progress": {}
            }
        
        # 使用当前主题如果没有指定
        if topic is None:
            topic = self.client_sessions[client_id].get("current_topic", "一般知识")
        
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
        
        # 创建生成练习题的提示
        prompt = f"""
        请针对"{topic}"主题，设计{count}道{difficulty_desc}练习题，帮助学习者巩固知识。
        
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
        
        logger.info(f"Generated {count} practice questions on {topic} for client {client_id}")
        
        # 返回响应给前端
        return {
            "content": response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat()
        }
    
    async def evaluate_answer(self, client_id: str, question: str, 
                            user_answer: str) -> Dict[str, Any]:
        """
        评估用户对问题的回答
        
        Args:
            client_id: 客户端标识
            question: 问题内容
            user_answer: 用户回答
            
        Returns:
            包含评估结果的响应
        """
        # 创建评估提示
        prompt = f"""
        请评估以下问题的回答:
        
        问题:
        {question}
        
        学习者的回答:
        {user_answer}
        
        请提供:
        1. 该回答是否正确
        2. 如果有误，指出错误之处
        3. 详细的解释和正确答案
        4. 建设性的反馈和鼓励
        """
        
        # 调用Agent进行评估
        eval_message = Message(
            role="user",
            content=prompt
        )
        
        response = await self.agent.arun(eval_message)
        response = response.content
        
        logger.info(f"Evaluated answer for client {client_id}")
        
        # 返回响应给前端
        return {
            "content": response,
            "sender": "agent",
            "timestamp": datetime.now().isoformat()
        }
    
    def _update_learning_progress(self, client_id: str, user_message: str, 
                                agent_response: str) -> None:
        """
        更新学习进度信息
        
        Args:
            client_id: 客户端标识
            user_message: 用户消息
            agent_response: 智能体响应
        """
        # 获取当前会话
        session = self.client_sessions.get(client_id, {})
        learning_progress = session.get("learning_progress", {})
        
        # 简单分析交互来更新学习进度
        # 这里使用简单的关键词匹配，实际系统可能需要更复杂的分析
        
        # 检测理解程度
        if re.search(r'我明白了|我懂了|我理解了|清楚了', user_message, re.IGNORECASE):
            learning_progress["comprehension"] = learning_progress.get("comprehension", 0) + 1
        
        # 检测疑惑
        if re.search(r'不明白|不懂|困惑|怎么理解|为什么', user_message, re.IGNORECASE):
            learning_progress["confusion"] = learning_progress.get("confusion", 0) + 1
        
        # 检测提问
        if re.search(r'\?|？|什么是|如何|能否解释', user_message, re.IGNORECASE):
            learning_progress["questions"] = learning_progress.get("questions", 0) + 1
        
        # 更新交互次数
        learning_progress["interactions"] = learning_progress.get("interactions", 0) + 1
        
        # 更新会话中的学习进度
        self.client_sessions[client_id]["learning_progress"] = learning_progress


# 单例实例，用于服务调用
teacher = TeacherAgent()