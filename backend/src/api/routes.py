from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime

from src.services.agent_service import agent_service

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

@router.get("/course/content/{section_id}", response_model=CourseContentResponse)
async def get_course_content(section_id: str):
    """
    获取特定章节内容
    这将由ContentDesigner Agent实现
    """
    return await agent_service.get_course_content(section_id)

@router.get("/user/progress")
async def get_user_progress():
    """
    获取用户学习进度
    这将由LearningProfiler Agent实现
    """
    return await agent_service.get_user_progress()
