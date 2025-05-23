#!/usr/bin/env python3
"""
TeacherAgent迁移示例

展示如何将现有的TeacherAgent从原始memory系统迁移到agno memory系统
"""

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

# 新的导入方式 - 使用工厂函数
from memory import create_memory_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernTeacherAgent:
    """
    现代化的Teacher Agent - 使用agno内置memory系统
    
    这个版本展示了如何使用新的agno memory架构，同时保持所有原有功能
    """
    
    def __init__(self, memory_db_path: str = "memory/teaching_memory.db", use_agno: bool = True):
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
            你是一个专业的教师AI助手，负责执行教学内容并与学习者进行互动。
            [原有的description保持不变...]
            """
        )
        
        # 使用新的工厂函数创建memory管理器
        self.memory_manager = create_memory_manager(memory_db_path, use_agno=use_agno)
        
        # 存储客户端会话信息
        self.client_sessions = {}
        
        memory_type = "Agno Memory v2" if use_agno else "SQLite Memory"
        logger.info(f"ModernTeacherAgent initialized with {memory_type}: {memory_db_path}")
    
    async def chat(self, client_id: str, message_content: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理来自客户端的聊天消息 - 使用新的memory系统
        
        这个方法的逻辑完全保持不变，但底层使用了agno memory架构
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
        
        # 计算主题相关性 - API保持完全一致
        topic_relevance = self.memory_manager.calculate_topic_relevance(
            current_topic, message_content
        )
        
        # 检查是否偏离主题 - API保持完全一致
        is_off_topic = self.memory_manager.check_topic_deviation(
            client_id, session_id, threshold=0.3
        )
        
        # 准备发送给Agent的消息
        user_message = Message(
            role="user",
            content=message_content
        )
        
        # 获取学习历史和进度信息 - API保持完全一致
        learning_history = self.memory_manager.get_teaching_history(
            client_id, session_id, limit=5
        )
        memory_summary = self.memory_manager.get_memory_summary(client_id)
        
        # 构建包含上下文的提示
        context_info = []
        
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
        
        # 记录教学交互到记忆管理器 - API保持完全一致
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
        设置教学上下文 - 使用新的memory系统
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
        
        # 如果设置了新主题，更新主题跟踪 - API保持完全一致
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
        提供教学材料 - 使用新的memory系统存储
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
        
        # 如果材料包含课程信息，存储到记忆管理器 - API保持完全一致
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
        
        # 记录教学交互到记忆管理器 - API保持完全一致
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
    
    def _update_learning_progress_with_memory(self, client_id: str, session_id: str, 
                                             current_topic: str, user_message: str, 
                                             agent_response: str) -> None:
        """
        更新学习进度 - 使用新的memory系统
        """
        try:
            # 简单的理解度评估（实际应用中可以使用更复杂的算法）
            comprehension_score = self._estimate_comprehension(user_message, agent_response)
            
            # 构建进度数据
            progress_data = {
                'user_message': user_message,
                'agent_response': agent_response,
                'comprehension_score': comprehension_score,
                'topic': current_topic,
                'timestamp': datetime.now().isoformat()
            }
            
            # 使用memory manager更新进度 - API保持完全一致
            self.memory_manager.update_learning_progress(
                client_id=client_id,
                course_id=1,  # 简化的课程ID
                section_id=current_topic,
                progress_data=progress_data
            )
            
        except Exception as e:
            logger.error(f"Error updating learning progress: {e}")
    
    def _estimate_comprehension(self, user_message: str, agent_response: str) -> float:
        """
        估算理解度评分
        """
        # 简化的理解度评估逻辑
        question_indicators = ['什么', '如何', '为什么', '怎么', '?', '？']
        has_question = any(indicator in user_message for indicator in question_indicators)
        
        if has_question:
            # 如果是问题，理解度稍低
            return 0.6
        else:
            # 如果是陈述或回答，理解度较高
            return 0.8


# 使用示例
async def main():
    """
    使用示例 - 展示如何使用新的ModernTeacherAgent
    """
    print("🚀 ModernTeacherAgent 使用示例")
    
    # 创建使用agno memory的teacher agent
    teacher = ModernTeacherAgent(use_agno=True)
    
    # 设置教学上下文
    await teacher.set_teaching_context("student_123", {
        "topic": "Python编程基础",
        "session_id": "session_001"
    })
    
    # 提供教学材料
    material = {
        "title": "Python变量",
        "course_title": "Python编程基础",
        "mainContent": "Python变量是用来存储数据的容器",
        "keyPoints": ["变量命名规则", "数据类型", "变量赋值"],
        "sections": [
            {"id": "var_basics", "title": "变量基础"},
            {"id": "var_types", "title": "变量类型"}
        ]
    }
    
    response = await teacher.provide_teaching_material("student_123", material)
    print(f"教学材料响应: {response['content'][:100]}...")
    
    # 模拟学生提问
    chat_response = await teacher.chat("student_123", "什么是Python变量？")
    print(f"聊天响应: {chat_response['content'][:100]}...")
    
    print("✅ 示例完成！新的agno memory系统运行正常。")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 