from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from agno.agent import Agent, Message
from agno.models.ollama import Ollama
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2 import Memory

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TeacherAgent:
    """
    Teacher Agent负责与学习者互动，回答问题，提供指导
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
            你是一个专业的教师，负责与学习者进行互动和指导。你的任务是：
            1. 回答学习者关于课程内容的问题
            2. 提供额外的解释和示例
            3. 引导学习者进行深入思考
            4. 适时提供练习和挑战
            5. 给予积极的反馈和鼓励
            
            你的回应应当专业、耐心、友好，考虑学习者的知识水平和学习风格。
            """
        )
        self.conversation_history = {}  # 用于存储与不同用户的对话历史
        logger.info("TeacherAgent initialized")
    
    async def chat(self, client_id: str, message: str) -> Dict[str, Any]:
        """
        处理来自学习者的消息，生成响应
        
        Args:
            client_id: 客户端ID，用于区分不同的对话
            message: 学习者的消息内容
            
        Returns:
            Dict[str, Any]: 包含响应内容的字典
        """
        logger.info(f"Received message from client {client_id}: {message[:50]}...")
        
        # 获取或初始化会话历史
        if client_id not in self.conversation_history:
            self.conversation_history[client_id] = []
        
        # 添加用户消息到历史
        self.conversation_history[client_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 构建发送给Agent的消息，包含历史上下文
        history = []
        for item in self.conversation_history[client_id][-5:]:  # 只使用最近5条消息
            history.append(Message(role="user" if item["role"] == "user" else "assistant", 
                                 content=item["content"]))
        
        # 发送消息并获取回复
        if len(history) > 1:
            # 如果有历史消息，使用完整的消息列表
            response = await self.agent.arun(messages=history)
        else:
            # 如果没有历史，直接发送当前消息
            response = await self.agent.arun(message)
        
        # 添加助手回复到历史
        self.conversation_history[client_id].append({
            "role": "assistant",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 返回响应
        return {
            "response": response.content,
            "conversation_id": client_id
        }

# 创建一个全局的TeacherAgent实例
teacher = TeacherAgent()
