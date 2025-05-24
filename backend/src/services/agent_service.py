from typing import Dict, Any, List, Optional
import logging
from fastapi import WebSocket
import json
from datetime import datetime
import os
import hashlib

from src.agents.teaching_team.course_planner import course_planner
from src.agents.teaching_team.content_designer import content_designer
from src.agents.teaching_team.teacher_agent import teacher
from src.memory.course_memory import CourseMemory

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentService:
    """
    Agent服务类，负责协调不同Agent的工作，管理与前端的通信
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        # 初始化课程记忆管理器
        self.course_memory = CourseMemory()
        # 确保本地课程存储目录存在
        self.courses_dir = os.path.join(os.path.dirname(__file__), "../../courses")
        os.makedirs(self.courses_dir, exist_ok=True)
        logger.info("AgentService initialized with course memory")
    
    def _generate_topic_id(self, topic: str) -> str:
        """为主题生成唯一ID"""
        return hashlib.md5(topic.lower().encode()).hexdigest()[:12]
    
    def _save_course_to_file(self, topic: str, course_data: Dict[str, Any]) -> str:
        """将课程数据保存到本地文件"""
        topic_id = self._generate_topic_id(topic)
        filename = f"course_{topic_id}.json"
        filepath = os.path.join(self.courses_dir, filename)
        
        # 添加保存时间戳
        course_data["saved_at"] = datetime.now().isoformat()
        course_data["topic"] = topic
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Course saved to file: {filepath}")
        return filepath
    
    def _load_course_from_file(self, topic: str) -> Optional[Dict[str, Any]]:
        """从本地文件加载课程数据"""
        topic_id = self._generate_topic_id(topic)
        filename = f"course_{topic_id}.json"
        filepath = os.path.join(self.courses_dir, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    course_data = json.load(f)
                logger.info(f"Course loaded from file: {filepath}")
                return course_data
            except Exception as e:
                logger.error(f"Error loading course from file {filepath}: {e}")
        return None
    
    def _save_section_to_file(self, topic: str, section_id: str, content_data: Dict[str, Any]) -> str:
        """将章节内容保存到本地文件"""
        topic_id = self._generate_topic_id(topic)
        section_filename = f"section_{topic_id}_{section_id.replace('.', '_')}.json"
        section_filepath = os.path.join(self.courses_dir, section_filename)
        
        # 添加保存时间戳
        content_data["saved_at"] = datetime.now().isoformat()
        content_data["topic"] = topic
        content_data["section_id"] = section_id
        
        with open(section_filepath, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Section content saved to file: {section_filepath}")
        return section_filepath
    
    def _load_section_from_file(self, topic: str, section_id: str) -> Optional[Dict[str, Any]]:
        """从本地文件加载章节内容"""
        topic_id = self._generate_topic_id(topic)
        section_filename = f"section_{topic_id}_{section_id.replace('.', '_')}.json"
        section_filepath = os.path.join(self.courses_dir, section_filename)
        
        if os.path.exists(section_filepath):
            try:
                with open(section_filepath, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
                logger.info(f"Section content loaded from file: {section_filepath}")
                return content_data
            except Exception as e:
                logger.error(f"Error loading section from file {section_filepath}: {e}")
        return None

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
        这里将解析用户背景信息并根据消息内容，决定调用哪个Agent来处理
        """
        # 解析消息中的用户背景信息
        user_background = self._extract_user_background(message_content)
        
        # 检查是否是课程规划请求（包含用户背景信息的首次请求）
        if user_background and self._is_course_planning_request(message_content):
            logger.info(f"检测到课程规划请求，用户背景信息: {user_background}")
            
            # 提取原始学习主题
            original_topic = self._extract_original_topic(message_content)
            
            if original_topic:
                # 调用课程规划Agent，传入用户背景信息
                course_plan = await self.create_course_plan_with_background(
                    topic=original_topic,
                    user_background=user_background
                )
                
                # 返回课程规划结果
                response = {
                    "content": f"已为您生成《{original_topic}》的个性化课程大纲！\n\n根据您的背景信息（{user_background.get('age', '')}，学习目标：{user_background.get('learningGoal', '')}，时间偏好：{user_background.get('timePreference', '')}），我为您量身定制了以下学习计划。请在课程规划页面查看详细内容。",
                    "sender": "agent",
                    "course_data": course_plan,
                    "user_background": user_background
                }
            else:
                response = {
                    "content": "抱歉，我无法从您的消息中识别出具体的学习主题。请重新描述您想学习的内容。",
                    "sender": "agent"
                }
        else:
            # 普通聊天消息，调用Teacher Agent处理
            response = await teacher.chat(client_id, message_content, user_background)
        
        # 添加消息ID和时间戳
        response["id"] = f"agent_{datetime.now().timestamp()}"
        if "timestamp" not in response:
            response["timestamp"] = datetime.now().isoformat()
            
        logger.info(f"Processed message from client {client_id}: {message_content[:50]}...")
        return response
    
    async def check_course_exists(self, topic: str) -> Dict[str, Any]:
        """检查课程是否已存在"""
        # 先检查记忆管理器
        course_data = self.course_memory.get_course_by_topic(topic)
        if course_data:
            logger.info(f"Course found in memory for topic: {topic}")
            return {"exists": True, "source": "memory", "course_data": course_data}
        
        # 再检查本地文件
        course_data = self._load_course_from_file(topic)
        if course_data:
            logger.info(f"Course found in local file for topic: {topic}")
            return {"exists": True, "source": "file", "course_data": course_data}
        
        logger.info(f"No existing course found for topic: {topic}")
        return {"exists": False, "source": None, "course_data": None}

    async def create_course_plan(self, topic: str, learning_goal: Optional[str] = None, 
                                 duration: Optional[str] = None, background_level: Optional[str] = None) -> Dict[str, Any]:
        """
        创建课程规划
        调用CoursePlanner Agent实现，支持缓存检查
        """
        logger.info(f"AgentService.create_course_plan called with topic: {topic}")
        
        # 先检查是否已有课程内容
        existing_check = await self.check_course_exists(topic)
        if existing_check["exists"]:
            logger.info(f"返回已存在的课程内容，来源：{existing_check['source']}")
            return existing_check["course_data"]
        
        # 如果不存在，生成新的课程内容
        logger.info(f"生成新的课程内容：{topic}")
        result = await course_planner.create_course_plan(
            topic=topic, 
            learning_goal=learning_goal,
            target_audience=duration,  # 将duration作为target_audience
            knowledge_level=background_level
        )
        
        logger.info(f"CoursePlanner returned: {result}")
        
        # 格式化结果
        formatted_result = self._format_course_result(result, topic)
        
        # 存储到记忆管理器
        try:
            course_id = self.course_memory.store_course_outline(topic, formatted_result)
            logger.info(f"Course stored in memory with ID: {course_id}")
        except Exception as e:
            logger.error(f"Error storing course in memory: {e}")
        
        # 保存到本地文件
        try:
            self._save_course_to_file(topic, formatted_result)
        except Exception as e:
            logger.error(f"Error saving course to file: {e}")
        
        return formatted_result
    
    def _format_course_result(self, result: Any, topic: str) -> Dict[str, Any]:
        """格式化课程结果为前端期望的格式"""
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

    async def get_course_content(self, section_id: str, topic: Optional[str] = None, user_background: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取课程内容
        调用ContentDesigner Agent实现，支持缓存检查
        """
        logger.info(f"AgentService.get_course_content called with section_id: {section_id}")
        
        # 如果提供了主题，先检查本地文件缓存
        if topic:
            cached_content = self._load_section_from_file(topic, section_id)
            if cached_content:
                logger.info(f"返回缓存的章节内容：{section_id}")
                return cached_content
        
        # 尝试从记忆管理器获取
        memory_content = self.course_memory.get_section_content_by_id(section_id)
        if memory_content:
            logger.info(f"从记忆管理器获取章节内容：{section_id}")
            # 转换为前端期望的格式
            return self._format_section_content(memory_content, section_id)
        
        # 如果缓存中没有，生成新内容
        logger.info(f"生成新的章节内容：{section_id}")
        
        # 解析section_id来构建章节信息
        section_parts = section_id.split('-') if '-' in section_id else section_id.split('.')
        chapter_num = section_parts[0] if section_parts else "1"
        section_num = section_parts[1] if len(section_parts) > 1 else "1"
        
        # 构建section_info字典
        section_info = {
            "id": section_id,
            "title": f"第{chapter_num}章 第{section_num}节",
            "description": f"关于{section_id}的详细内容",
            "learning_objectives": ["理解核心概念", "掌握实际应用"],
            "key_points": ["重点内容1", "重点内容2"]
        }
        
        try:
            result = await content_designer.create_content(
                section_info, 
                course_topic=topic, 
                user_background=user_background
            )
            logger.info(f"ContentDesigner returned: {result}")
            
            # 格式化内容
            formatted_content = self._format_content_result(result, section_info)
            
            # 存储到记忆管理器（如果有课程ID的话）
            try:
                # 这里需要课程ID，暂时跳过记忆存储
                # content_id = self.course_memory.store_section_content(course_id, section_info, formatted_content)
                pass
            except Exception as e:
                logger.error(f"Error storing section content in memory: {e}")
            
            # 保存到本地文件（如果有主题的话）
            if topic:
                try:
                    self._save_section_to_file(topic, section_id, formatted_content)
                except Exception as e:
                    logger.error(f"Error saving section content to file: {e}")
            
            return formatted_content
                
        except Exception as e:
            logger.error(f"Error calling ContentDesigner: {e}")
            # 返回默认内容以防止API失败
            return self._get_default_section_content(section_info)
    
    def _format_section_content(self, memory_content: Dict[str, Any], section_id: str) -> Dict[str, Any]:
        """将记忆管理器中的内容格式化为前端期望的格式"""
        # 这里需要根据记忆管理器的实际存储格式来转换
        return {
            "title": memory_content.get("title", f"章节 {section_id}"),
            "mainContent": memory_content.get("content", ""),
            "keyPoints": memory_content.get("key_points", []),
            "images": memory_content.get("images", []),
            "curriculumAlignment": memory_content.get("curriculum_alignment", [])
        }
    
    def _format_content_result(self, result: Any, section_info: Dict[str, Any]) -> Dict[str, Any]:
        """格式化章节内容结果"""
        if isinstance(result, dict) and "content" in result:
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
            return self._get_default_section_content(section_info)
    
    def _get_default_section_content(self, section_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取默认的章节内容"""
        return {
            "title": section_info["title"],
            "mainContent": f"# {section_info['title']}\n\n这里是关于{section_info['title']}的详细内容。\n\n## 主要内容\n\n本节将介绍相关的核心概念和实际应用。",
            "keyPoints": ["核心概念理解", "实际应用掌握", "相关知识点整合"],
            "images": [],
            "curriculumAlignment": ["符合课程标准要求", "对应学习目标", "适合目标年龄段"]
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

    def _extract_user_background(self, message_content: str) -> Optional[Dict[str, Any]]:
        """
        从消息内容中提取用户背景信息
        """
        try:
            # 查找用户背景信息标记
            if "## 用户背景信息" in message_content:
                lines = message_content.split('\n')
                background_info = {}
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("年龄/年级:"):
                        background_info["age"] = line.split(":", 1)[1].strip()
                    elif line.startswith("学习目标:"):
                        background_info["learningGoal"] = line.split(":", 1)[1].strip()
                    elif line.startswith("时间偏好:"):
                        background_info["timePreference"] = line.split(":", 1)[1].strip()
                    elif line.startswith("知识水平:"):
                        background_info["knowledgeLevel"] = line.split(":", 1)[1].strip()
                    elif line.startswith("目标受众:"):
                        background_info["targetAudience"] = line.split(":", 1)[1].strip()
                
                return background_info if background_info else None
                
        except Exception as e:
            logger.error(f"Error extracting user background: {e}")
        
        return None
    
    def _is_course_planning_request(self, message_content: str) -> bool:
        """
        判断是否是课程规划请求
        """
        # 检查是否包含课程规划相关的标识
        planning_indicators = [
            "## Agent处理指令",
            "CoursePlanner",
            "ContentGenerator", 
            "Monitor",
            "Verifier"
        ]
        
        for indicator in planning_indicators:
            if indicator in message_content:
                return True
        
        return False
    
    def _extract_original_topic(self, message_content: str) -> Optional[str]:
        """
        从格式化消息中提取原始学习主题
        """
        try:
            # 消息内容的第一行通常是原始主题
            lines = message_content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("年龄") and not line.startswith("学习目标"):
                    return line
        except Exception as e:
            logger.error(f"Error extracting original topic: {e}")
        
        return None
    
    async def create_course_plan_with_background(self, topic: str, user_background: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用用户背景信息创建个性化课程规划
        """
        logger.info(f"Creating personalized course plan for topic: {topic} with background: {user_background}")
        
        # 调用CoursePlanner Agent，传入用户背景信息作为独立参数
        result = await course_planner.create_course_plan(
            topic=topic,
            learning_goal=user_background.get("learningGoal"),
            target_audience=user_background.get("age"),  # 使用年龄作为目标受众
            knowledge_level=user_background.get("knowledgeLevel"),
            store_to_memory=True
        )
        
        # 存储用户背景信息到结果中，以便后续Agent使用
        if isinstance(result, dict):
            result["user_background"] = user_background
            result["personalization_applied"] = True
        
        # 格式化结果
        formatted_result = self._format_course_result(result, topic)
        
        # 保存包含用户背景信息的课程到本地文件
        try:
            formatted_result["user_background"] = user_background
            self._save_course_to_file(topic, formatted_result)
        except Exception as e:
            logger.error(f"Error saving personalized course to file: {e}")
        
        return formatted_result

# 创建一个全局的AgentService实例
agent_service = AgentService()
