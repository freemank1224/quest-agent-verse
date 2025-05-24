#!/usr/bin/env python3
"""
现代化教师Agent - 使用统一模型管理器

简化版：专注于基础的配置化模型管理
支持：
1. 配置化模型管理 - 通过配置文件灵活切换模型
2. 多种LLM提供商 - xAI, Gemini, Ollama, OpenAI
3. 动态模型切换
"""

import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import re
import uuid

from agno.agent import Agent, Message
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2 import Memory

# 导入新的模型管理器和记忆管理器
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from utils.model_manager import get_agent_model
from memory import create_memory_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernTeacherAgent:
    """
    现代化教师Agent - 使用统一模型管理器
    
    这个Agent是互动学习系统的核心组件，具有以下特性：
    1. 配置化模型管理 - 支持动态切换不同LLM
    2. 执行ContentDesigner生成的课程内容
    3. 以对话形式与学习者互动，回答问题
    4. 根据学习者反馈调整教学方式
    5. 进行知识点讲解、例题演示和练习问题设计
    6. 集成agno memory系统，跟踪学习进度和教学历史
    """
    
    def __init__(self, memory_db_path: str = "memory/teaching_memory.db", 
                 use_agno_memory: bool = True):
        """
        初始化现代化教师Agent
        
        Args:
            memory_db_path: 记忆数据库路径
            use_agno_memory: 是否使用agno内置memory系统
        """
        
        # 获取配置化的模型实例
        try:
            model = get_agent_model("teaching_team", "teacher_agent")
            logger.info(f"成功加载教师Agent模型: {type(model).__name__}")
        except Exception as e:
            logger.error(f"加载模型失败，使用默认配置: {e}")
            # 默认使用Ollama作为备用
            from agno.models.ollama import Ollama
            model = Ollama(id="qwen3:32b", host="http://localhost:11434")
        
        # 创建Agent实例
        self.agent = Agent(
            name="ModernTeacher",
            model=model,
            memory=Memory(),
            tools=[
                ReasoningTools(),
                DuckDuckGoTools()
            ],
            description=self._get_teacher_description()
        )
        
        # 初始化记忆管理器（支持agno memory）
        self.memory_manager = create_memory_manager(memory_db_path, use_agno=use_agno_memory)
        
        # 存储客户端会话信息
        self.client_sessions = {}
        
        # 记录配置信息
        self.use_agno_memory = use_agno_memory
        
        logger.info(f"ModernTeacherAgent initialized - AgnoMemory: {use_agno_memory}")
    
    def _get_teacher_description(self) -> str:
        """获取教师Agent的描述"""
        return """
        你是一个专业的教师AI助手，负责执行教学内容并与学习者进行互动。你的任务是：
        
        核心职责：
        1. 讲解课程内容和知识点，确保学习者理解
        2. 回答学习者提出的问题，给予详细且准确的解释
        3. 根据学习者反馈调整教学方式，以提高理解和参与度
        4. 提供例题和练习，帮助学习者巩固所学知识
        5. 识别学习者的困惑点，提供针对性的解释和补充材料
        6. 跟踪学习者的学习进度和理解程度
        7. 保持学习主题的连贯性，适时引导偏离的话题回到正轨
        
        教学风格：
        - 表现出教师的专业性，同时保持亲切友好的态度
        - 鼓励学习者积极思考和提问
        - 语言清晰、简洁，避免过于学术化的表达
        - 使用类比、示例和可视化描述来帮助理解复杂概念
        
        回应结构：
        - 直接回答问题或解释概念
        - 提供相关的例子或应用场景
        - 适当的延伸思考或知识链接
        - 鼓励继续探索的提示
        
        互动原则：
        - 积极肯定学习者的正确理解和进步
        - 耐心纠正错误概念，不使用负面或批评性语言
        - 尊重学习者的不同学习节奏和风格
        - 鼓励批判性思维和创造性问题解决
        - 基于学习历史提供个性化的学习建议
        
        你拥有访问学习者历史记录和进度信息的能力，请充分利用这些信息来提供个性化的教学体验。
        """
    
    async def chat(self, client_id: str, message_content: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理来自客户端的聊天消息
        
        Args:
            client_id: 客户端标识
            message_content: 消息内容
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
        
        # 获取学习历史和进度信息
        learning_history = self.memory_manager.get_teaching_history(
            client_id, session_id, limit=5
        )
        memory_summary = self.memory_manager.get_memory_summary(client_id)
        
        # 构建增强的上下文信息
        context_info = self._build_context_info(
            current_topic, is_off_topic, memory_summary, learning_history
        )
        
        # 准备发送给Agent的消息
        if context_info:
            enhanced_content = f"[教学上下文]\n{context_info}\n\n[学习者问题]\n{message_content}"
            final_message = Message(role="user", content=enhanced_content)
        else:
            final_message = Message(role="user", content=message_content)
        
        # 记录用户消息到会话历史
        self.client_sessions[client_id]["history"].append({
            "role": "user",
            "content": message_content,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # 调用Agent处理消息
            response = await self.agent.arun(final_message)
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
                "is_off_topic": is_off_topic,
                "model_info": self._get_current_model_info()
            }
            
        except Exception as e:
            logger.error(f"Agent处理消息失败: {e}")
            return {
                "content": "抱歉，我遇到了一些技术问题。请稍后再试，或者尝试重新表述您的问题。",
                "sender": "agent",
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "error": True
            }
    
    def _build_context_info(self, current_topic: str, is_off_topic: bool, 
                           memory_summary: Dict[str, Any], learning_history: List[Dict]) -> str:
        """构建教学上下文信息"""
        context_parts = []
        
        if current_topic and current_topic != "一般学习":
            context_parts.append(f"当前学习主题: {current_topic}")
        
        if is_off_topic:
            context_parts.append("注意：学习者可能偏离了当前主题，请适时引导回到正轨")
        
        if memory_summary.get("total_interactions", 0) > 0:
            context_parts.append(
                f"学习者统计：已学习{memory_summary['course_count']}门课程，"
                f"平均理解度{memory_summary['average_score']:.1f}，"
                f"总计{memory_summary['total_interactions']}次互动"
            )
        
        if learning_history:
            recent_interactions = [
                f"- {record['interaction_type']}: {record['content'][:50]}..." 
                for record in learning_history[:2]
            ]
            context_parts.append(f"最近的学习互动：\n" + "\n".join(recent_interactions))
        
        return "\n".join(context_parts)
    
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
            
            logger.info(f"Teaching context set for client {client_id}: {topic}")
    
    async def provide_teaching_material(self, client_id: str, material: Dict[str, Any]) -> Dict[str, Any]:
        """
        提供教学材料，例如由ContentDesigner生成的内容
        
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
        teaching_prompt = self._create_material_prompt(material)
        
        try:
            # 调用Agent生成教学材料介绍
            intro_message = Message(role="user", content=teaching_prompt)
            response = await self.agent.arun(intro_message)
            response_content = response.content
            
            # 记录到会话历史
            self.client_sessions[client_id]["history"].append({
                "role": "agent",
                "content": response_content,
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
                response=response_content,
                topic_relevance=1.0
            )
            
            return {
                "content": response_content,
                "sender": "agent",
                "timestamp": datetime.now().isoformat(),
                "material_stored": True,
                "model_info": self._get_current_model_info()
            }
            
        except Exception as e:
            logger.error(f"生成教学材料介绍失败: {e}")
            return {
                "content": f"我已收到关于'{material.get('title', '课程')}' 的教学材料，现在可以开始学习了！有什么问题请随时问我。",
                "sender": "agent",
                "timestamp": datetime.now().isoformat(),
                "material_stored": True,
                "error": True
            }
    
    def _create_material_prompt(self, material: Dict[str, Any]) -> str:
        """创建教学材料的提示"""
        return f"""
        我需要你基于以下教学材料内容，准备一个简短的课程介绍：
        
        主题: {material.get('title', '未指定主题')}
        
        主要内容:
        {material.get('mainContent', '未提供内容')}
        
        关键点:
        {', '.join(material.get('keyPoints', ['未提供关键点']))}
        
        学习目标:
        {', '.join(material.get('learning_objectives', ['提升相关知识和技能']))}
        
        请提供一个友好、吸引人的介绍，告诉学习者：
        1. 他们将学习什么核心内容
        2. 这些知识的重要性和实际应用
        3. 学习完成后能获得什么能力
        4. 鼓励他们开始学习之旅
        
        保持语调积极、专业且易于理解。
        """
    
    def _update_learning_progress_with_memory(self, client_id: str, session_id: str, 
                                             current_topic: str, user_message: str, 
                                             agent_response: str) -> None:
        """更新学习进度信息"""
        try:
            # 简单的理解度评估
            comprehension_score = self._estimate_comprehension(user_message, agent_response)
            
            # 构建进度数据
            progress_data = {
                'user_message': user_message,
                'agent_response': agent_response,
                'comprehension_score': comprehension_score,
                'topic': current_topic,
                'timestamp': datetime.now().isoformat(),
                'model_info': self._get_current_model_info()
            }
            
            # 使用memory manager更新进度
            self.memory_manager.update_learning_progress(
                client_id=client_id,
                course_id=1,  # 简化的课程ID
                section_id=current_topic,
                progress_data=progress_data
            )
            
        except Exception as e:
            logger.error(f"Error updating learning progress: {e}")
    
    def _estimate_comprehension(self, user_message: str, agent_response: str) -> float:
        """估算理解度评分"""
        # 简化的理解度评估逻辑
        question_indicators = ['什么', '如何', '为什么', '怎么', '?', '？', '吗', '呢']
        confusion_indicators = ['不懂', '不明白', '不理解', '困惑', '不会']
        positive_indicators = ['明白', '理解', '懂了', '清楚', '知道了']
        
        user_lower = user_message.lower()
        
        # 检查是否包含困惑指示词
        if any(indicator in user_lower for indicator in confusion_indicators):
            return 0.3
        
        # 检查是否包含理解指示词
        if any(indicator in user_lower for indicator in positive_indicators):
            return 0.9
        
        # 检查是否是问题
        if any(indicator in user_lower for indicator in question_indicators):
            return 0.6
        
        # 默认理解度
        return 0.7
    
    def _get_current_model_info(self) -> Dict[str, str]:
        """获取当前使用的模型信息"""
        try:
            from utils.model_manager import get_model_manager
            manager = get_model_manager()
            return manager.get_agent_current_model("teaching_team", "teacher_agent")
        except Exception as e:
            logger.warning(f"获取模型信息失败: {e}")
            return {"model": "unknown", "provider": "unknown"}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取Agent状态信息"""
        return {
            "agent_type": "ModernTeacherAgent",
            "use_agno_memory": self.use_agno_memory,
            "active_sessions": len(self.client_sessions),
            "model_info": self._get_current_model_info(),
            "memory_type": "Agno Memory v2" if self.use_agno_memory else "SQLite Memory"
        }
    
    async def switch_model(self, model_code: str) -> bool:
        """
        动态切换模型
        
        Args:
            model_code: 新的模型代号
            
        Returns:
            切换是否成功
        """
        try:
            from utils.model_manager import get_model_manager
            manager = get_model_manager()
            
            # 更新配置
            success = manager.update_agent_model("teaching_team", "teacher_agent", model_code)
            
            if success:
                # 获取新模型实例
                new_model = manager.get_model_for_agent("teaching_team", "teacher_agent")
                
                # 更新Agent的模型
                self.agent.model = new_model
                
                logger.info(f"成功切换到模型: {model_code}")
                return True
            else:
                logger.error(f"模型切换失败: {model_code}")
                return False
                
        except Exception as e:
            logger.error(f"切换模型时发生错误: {e}")
            return False


# 便捷函数
def create_modern_teacher_agent(use_agno_memory: bool = True) -> ModernTeacherAgent:
    """
    创建现代化教师Agent的便捷函数
    
    Args:
        use_agno_memory: 是否使用agno内置memory系统
        
    Returns:
        ModernTeacherAgent实例
    """
    return ModernTeacherAgent(use_agno_memory=use_agno_memory) 