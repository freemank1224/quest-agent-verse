from typing import Dict, Any, List, Optional
import logging
from fastapi import WebSocket
import json
from datetime import datetime

from src.agents.teaching_team.course_planner import course_planner
from src.agents.teaching_team.content_designer import content_designer
from src.agents.teaching_team.teacher_agent import teacher

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentService:
    """
    Agent服务类，负责协调不同Agent的工作，管理与前端的通信
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        logger.info("AgentService initialized")
    
    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """注册WebSocket连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str) -> None:
        """移除WebSocket连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]) -> None:
        """发送消息到特定客户端"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
            logger.debug(f"Message sent to client {client_id}")
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[str] = None) -> None:
        """广播消息到所有客户端，可选择排除特定客户端"""
        for client_id, websocket in self.active_connections.items():
            if exclude is None or client_id != exclude:
                await websocket.send_json(message)
        logger.debug(f"Message broadcasted to {len(self.active_connections) - (1 if exclude else 0)} clients")
    
    async def process_message(self, client_id: str, message_content: str) -> Dict[str, Any]:
        """
        处理从客户端接收到的消息
        这里将根据消息内容，决定调用哪个Agent来处理
        """
        # 调用Teacher Agent处理聊天消息
        response = await teacher.chat(client_id, message_content)
        
        # 添加消息ID和时间戳
        response["id"] = f"agent_{datetime.now().timestamp()}"
        if "timestamp" not in response:
            response["timestamp"] = datetime.now().isoformat()
            
        logger.info(f"Processed message from client {client_id}: {message_content[:50]}...")
        return response
    
    async def create_course_plan(self, topic: str, learning_goal: Optional[str] = None, 
                                 duration: Optional[str] = None, background_level: Optional[str] = None) -> Dict[str, Any]:
        """
        创建课程规划
        调用CoursePlanner Agent实现
        """
        logger.info(f"AgentService.create_course_plan called with topic: {topic}")
        
        # 调用CoursePlanner，使用正确的参数名
        result = await course_planner.create_course_plan(
            topic=topic, 
            learning_goal=learning_goal,
            target_audience=duration,  # 将duration作为target_audience
            knowledge_level=background_level
        )
        
        logger.info(f"CoursePlanner returned: {result}")
        
        # 检查结果结构并转换格式
        if isinstance(result, dict):
            # 如果有course_title和sections，转换为前端期望的格式
            if "course_title" in result and "sections" in result:
                formatted_result = {
                    "title": result["course_title"],
                    "chapters": []
                }
                
                # 转换sections为chapters格式
                for section in result["sections"]:
                    chapter = {
                        "id": section.get("id", ""),
                        "title": section.get("title", ""),
                        "description": section.get("description", ""),
                        "sections": []  # 前端期望的是嵌套的sections
                    }
                    
                    # 添加子节
                    if "subsections" in section:
                        for subsection in section["subsections"]:
                            chapter["sections"].append({
                                "id": subsection.get("id", ""),
                                "title": subsection.get("title", "")
                            })
                    else:
                        # 如果没有子节，创建一个默认子节
                        chapter["sections"].append({
                            "id": f"{section.get('id', '1')}.1",
                            "title": section.get("title", "内容") + " - 详细内容"
                        })
                    
                    formatted_result["chapters"].append(chapter)
                
                logger.info(f"Formatted result: {formatted_result}")
                return formatted_result
            
            # 如果已经是正确的格式
            elif "title" in result and "chapters" in result:
                logger.info("Result is already in correct format")
                return result
            
            # 如果是其他格式，尝试创建默认结构
            else:
                logger.warning(f"Unexpected result format, creating default structure. Keys: {result.keys()}")
                return {
                    "title": result.get("title", topic + " 课程大纲"),
                    "chapters": [
                        {
                            "id": "1",
                            "title": "第一章：基础介绍",
                            "description": f"介绍{topic}的基本概念",
                            "sections": [
                                {"id": "1.1", "title": "概念介绍"},
                                {"id": "1.2", "title": "基础知识"}
                            ]
                        },
                        {
                            "id": "2",
                            "title": "第二章：深入学习",
                            "description": f"深入学习{topic}的核心内容",
                            "sections": [
                                {"id": "2.1", "title": "核心原理"},
                                {"id": "2.2", "title": "实际应用"}
                            ]
                        }
                    ]
                }
        else:
            logger.error(f"CoursePlanner returned non-dict result: {type(result)}")
            # 创建默认响应
            return {
                "title": topic + " 课程大纲",
                "chapters": [
                    {
                        "id": "1",
                        "title": "第一章：基础介绍",
                        "description": f"介绍{topic}的基本概念",
                        "sections": [
                            {"id": "1.1", "title": "概念介绍"},
                            {"id": "1.2", "title": "基础知识"}
                        ]
                    }
                ]
            }
    
    async def get_course_content(self, section_id: str) -> Dict[str, Any]:
        """
        获取课程内容
        调用ContentDesigner Agent实现
        """
        logger.info(f"AgentService.get_course_content called with section_id: {section_id}")
        
        # 解析section_id来构建章节信息
        section_parts = section_id.split('-') if '-' in section_id else section_id.split('.')
        chapter_num = section_parts[0] if section_parts else "1"
        section_num = section_parts[1] if len(section_parts) > 1 else "1"
        
        # 构建section_info字典，这是ContentDesignerAgent.create_content()期望的格式
        section_info = {
            "id": section_id,
            "title": f"第{chapter_num}章 第{section_num}节",
            "description": f"关于{section_id}的详细内容",
            "learning_objectives": ["理解核心概念", "掌握实际应用"],
            "key_points": ["重点内容1", "重点内容2"]
        }
        
        logger.info(f"Calling ContentDesigner with section_info: {section_info}")
        
        try:
            result = await content_designer.create_content(section_info)
            logger.info(f"ContentDesigner returned: {result}")
            
            # 转换格式以匹配前端期望的CourseContentResponse
            if isinstance(result, dict):
                # 如果返回的是有效的内容格式
                if "content" in result:
                    # 提取内容并转换为前端期望的格式
                    main_content = ""
                    key_points = []
                    images = []
                    curriculum_alignment = []
                    
                    for item in result["content"]:
                        item_type = item.get("type", "")
                        if item_type == "introduction":
                            main_content += f"## 介绍\n{item.get('text', '')}\n\n"
                        elif item_type == "concept":
                            main_content += f"## {item.get('title', '概念')}\n{item.get('explanation', '')}\n\n"
                            if item.get("examples"):
                                main_content += f"**示例：**\n"
                                for example in item["examples"]:
                                    main_content += f"- {example}\n"
                                main_content += "\n"
                        elif item_type == "activity":
                            main_content += f"## {item.get('title', '活动')}\n{item.get('description', '')}\n\n"
                            if item.get("steps"):
                                main_content += f"**步骤：**\n"
                                for i, step in enumerate(item["steps"], 1):
                                    main_content += f"{i}. {step}\n"
                                main_content += "\n"
                        elif item_type == "media":
                            images.append({
                                "url": "https://via.placeholder.com/600x300?text=" + item.get("title", "示例图片"),
                                "caption": item.get("description", "示例图片")
                            })
                        elif item_type == "assessment":
                            for question in item.get("questions", []):
                                key_points.append(f"问题：{question.get('question', '')}")
                    
                    return {
                        "title": section_info["title"],
                        "mainContent": main_content or f"# {section_info['title']}\n\n这里是关于{section_info['title']}的详细内容。",
                        "keyPoints": key_points or ["核心概念理解", "实际应用掌握", "相关知识点整合"],
                        "images": images,
                        "curriculumAlignment": curriculum_alignment or ["符合课程标准要求", "对应学习目标", "适合目标年龄段"]
                    }
                else:
                    # 如果返回格式不符合预期，创建默认内容
                    logger.warning("ContentDesigner returned unexpected format, creating default content")
                    return {
                        "title": section_info["title"],
                        "mainContent": f"# {section_info['title']}\n\n这里是关于{section_info['title']}的详细内容。\n\n## 主要内容\n\n本节将介绍相关的核心概念和实际应用。",
                        "keyPoints": ["核心概念理解", "实际应用掌握", "相关知识点整合"],
                        "images": [],
                        "curriculumAlignment": ["符合课程标准要求", "对应学习目标", "适合目标年龄段"]
                    }
            else:
                logger.error(f"ContentDesigner returned non-dict result: {type(result)}")
                # 创建默认内容
                return {
                    "title": section_info["title"],
                    "mainContent": f"# {section_info['title']}\n\n这里是关于{section_info['title']}的详细内容。",
                    "keyPoints": ["核心概念理解", "实际应用掌握"],
                    "images": [],
                    "curriculumAlignment": ["符合课程标准要求"]
                }
                
        except Exception as e:
            logger.error(f"Error calling ContentDesigner: {e}")
            # 返回默认内容以防止API失败
            return {
                "title": section_info["title"],
                "mainContent": f"# {section_info['title']}\n\n抱歉，暂时无法获取详细内容。请稍后重试。",
                "keyPoints": ["内容加载中"],
                "images": [],
                "curriculumAlignment": ["课程标准对齐中"]
            }
    
    async def get_user_progress(self) -> Dict[str, Any]:
        """
        获取用户学习进度
        这将由LearningProfiler Agent实现
        """
        # 临时模拟返回数据，后续将实现实际的Agent调用
        progress = {
            "completedChapters": ["1", "2"],
            "achievements": [
                {"id": "1", "title": "学习初探", "description": "完成第一章学习"},
                {"id": "2", "title": "学习进阶", "description": "完成两个章节学习"}
            ],
            "progressPercentage": 60
        }
        logger.info("Retrieved user progress")
        return progress

# 创建一个全局的AgentService实例
agent_service = AgentService()
