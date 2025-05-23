from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import os
import logging

from src.services.agent_service import agent_service

# 配置日志
logger = logging.getLogger(__name__)

# 路由器
router = APIRouter(prefix="/api", tags=["agents"])

# 定义数据模型
class CourseRequest(BaseModel):
    topic: str
    learning_goal: Optional[str] = None
    duration: Optional[str] = None
    background_level: Optional[str] = None

class MessageRequest(BaseModel):
    content: str
    sender: str

class CourseOutlineResponse(BaseModel):
    title: str
    chapters: List[Dict[str, Any]]

class CourseContentResponse(BaseModel):
    title: str
    mainContent: str
    keyPoints: List[str]
    images: List[Dict[str, str]]
    curriculumAlignment: List[str]

# WebSocket路由用于实时聊天
@router.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await agent_service.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理接收到的消息
            response = await agent_service.process_message(client_id, message["content"])
            
            # 发送响应
            await websocket.send_json(response)
    except WebSocketDisconnect:
        agent_service.disconnect(client_id)

# 课程规划相关路由
@router.post("/course/plan", response_model=CourseOutlineResponse)
async def create_course_plan(request: CourseRequest):
    """
    创建课程规划大纲
    这将由CoursePlanner Agent实现
    """
    return await agent_service.create_course_plan(
        request.topic, 
        request.learning_goal, 
        request.duration, 
        request.background_level
    )

@router.get("/course/exists/{topic}")
async def check_course_exists(topic: str):
    """
    检查指定主题的课程是否已存在
    """
    result = await agent_service.check_course_exists(topic)
    return JSONResponse(content=result)

@router.get("/course/content/{section_id}", response_model=CourseContentResponse)
async def get_course_content(section_id: str, topic: Optional[str] = None):
    """
    获取特定章节内容
    这将由ContentDesigner Agent实现
    """
    return await agent_service.get_course_content(section_id, topic)

@router.get("/course/list")
async def list_courses():
    """
    获取所有已存储的课程列表
    """
    courses_dir = agent_service.courses_dir
    course_files = []
    
    if os.path.exists(courses_dir):
        for filename in os.listdir(courses_dir):
            if filename.startswith("course_") and filename.endswith(".json"):
                filepath = os.path.join(courses_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        course_data = json.load(f)
                    course_files.append({
                        "filename": filename,
                        "topic": course_data.get("topic", "未知主题"),
                        "title": course_data.get("title", "未命名课程"),
                        "saved_at": course_data.get("saved_at", ""),
                        "chapters_count": len(course_data.get("chapters", []))
                    })
                except Exception as e:
                    logger.error(f"Error reading course file {filename}: {e}")
    
    return JSONResponse(content={"courses": course_files})

@router.get("/user/progress")
async def get_user_progress():
    """
    获取用户学习进度
    这将由LearningProfiler Agent实现
    """
    return await agent_service.get_user_progress()

@router.post("/teaching/set-context")
async def set_teaching_context(request: dict):
    """
    设置教学上下文，包括学习主题
    """
    client_id = request.get("client_id")
    topic = request.get("topic")
    session_id = request.get("session_id")
    
    if not client_id or not topic:
        raise HTTPException(status_code=400, detail="client_id and topic are required")
    
    context = {
        "topic": topic,
        "session_id": session_id or str(uuid.uuid4())
    }
    
    from src.agents.teaching_team.teacher_agent import teacher
    await teacher.set_teaching_context(client_id, context)
    
    return JSONResponse(content={"status": "success", "context": context})
