from typing import Dict, Any, List, Optional
import logging
import json
import re

from agno.agent import Agent, Message
from agno.models.ollama import Ollama
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2 import Memory


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentDesignerAgent:
    """
    ContentDesigner Agent负责根据课程大纲设计章节的详细内容
    """
    
    def __init__(self):
        # 使用 xAI 作为主要模型
        self.agent = Agent(
            name="ContentDesigner",
            model=Ollama(id="qwen3:32b", host="http://localhost:11434"),  # 使用xAI的默认模型
            memory=Memory(),
            tools=[
                ReasoningTools(),
                DuckDuckGoTools()
            ],
            description="""
            你是一个专业的教育内容设计专家，负责设计高质量的教学内容。你的任务是：
            1. 根据课程大纲中的章节要求，设计详细的教学内容
            2. 创建结构清晰、易于理解的教学材料
            3. 确定核心知识点和学习要点
            4. 建议合适的教学媒体（图像、视频等）
            5. 确保内容与课标要求保持一致
            
            教学内容应当符合教育理论，使用适当的教学方法和策略。
            """
        )
        logger.info("ContentDesignerAgent initialized")
    
    async def create_content(self, section_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        为特定章节创建内容
        
        Args:
            section_info: 包含章节信息的字典，应当包含id, title, description等字段
            
        Returns:
            Dict[str, Any]: 包含章节内容的字典
        """
        logger.info(f"Creating content for section: {section_info.get('title', 'Unknown')}")
        
        # 构建发送给Agent的消息
        # 首先准备JSON模板字符串（避免f-string中的大括号冲突）
        json_template = '''{
  "content": [
    {
      "type": "introduction",
      "text": "内容介绍"
    },
    {
      "type": "concept",
      "title": "概念标题",
      "explanation": "概念解释",
      "examples": ["示例1", "示例2"]
    },
    {
      "type": "activity",
      "title": "活动标题",
      "description": "活动描述",
      "steps": ["步骤1", "步骤2"]
    },
    {
      "type": "media",
      "title": "媒体标题",
      "description": "媒体描述",
      "media_type": "image/video/audio",
      "suggestion": "媒体建议"
    },
    {
      "type": "assessment",
      "questions": [
        {
          "question": "问题描述",
          "type": "multiple_choice/short_answer/etc",
          "options": ["选项1", "选项2"],
          "answer": "正确答案",
          "explanation": "答案解释"
        }
      ]
    }
  ]
}'''
        
        content = f"""请根据以下章节信息，设计详细的教学内容：

章节ID: {section_info.get('id', 'Unknown')}
章节标题: {section_info.get('title', 'Unknown')}
章节描述: {section_info.get('description', 'No description provided')}

学习目标:
{self._format_list(section_info.get('learning_objectives', []))}

关键要点:
{self._format_list(section_info.get('key_points', []))}

请提供以下内容：
1. 详细的教学内容，包括概念解释、示例和应用
2. 推荐的教学活动和练习
3. 建议的教学媒体和资源
4. 评估方法和问题

请以JSON格式返回你的回答，结构如下：
{json_template}
"""
        
        # 创建消息
        message = Message(role="user", content=content)
        
        # 发送消息并获取回复
        logger.info("Sending message to ContentDesigner agno agent...")
        response = await self.agent.arun(message)
        logger.info(f"Raw response from ContentDesigner: {response.content}")
        
        # 清理响应内容，移除thinking标签和其他非JSON内容
        cleaned_content = response.content
        
        # 移除<think>标签及其内容
        cleaned_content = re.sub(r'<think>.*?</think>', '', cleaned_content, flags=re.DOTALL)
        
        # 移除其他可能的标签
        cleaned_content = re.sub(r'<.*?>', '', cleaned_content)
        
        # 移除多余的空白行
        cleaned_content = '\n'.join(line.strip() for line in cleaned_content.split('\n') if line.strip())
        
        logger.info(f"Cleaned response: {cleaned_content}")
        
        try:
            # 首先尝试直接解析JSON
            section_content = json.loads(cleaned_content)
            logger.info("Successfully parsed ContentDesigner response as JSON")
            return section_content
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse ContentDesigner response as direct JSON: {e}")
            
            # 尝试从markdown代码块中提取JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', cleaned_content, re.DOTALL)
            if json_match:
                try:
                    section_content = json.loads(json_match.group(1))
                    logger.info("Successfully extracted JSON from markdown code block")
                    return section_content
                except json.JSONDecodeError as e2:
                    logger.warning(f"Failed to parse extracted JSON: {e2}")
            
            # 尝试寻找任何JSON对象
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, cleaned_content, re.DOTALL)
            for match in json_matches:
                try:
                    section_content = json.loads(match)
                    logger.info("Successfully found and parsed JSON object in response")
                    return section_content
                except json.JSONDecodeError:
                    continue
            
            # 如果所有解析都失败，创建一个默认格式的响应
            logger.warning("All JSON parsing attempts failed, creating default content structure")
            return {
                "content": [
                    {
                        "type": "introduction",
                        "text": f"欢迎学习{section_info.get('title', '本章节')}。本节将深入介绍相关的核心概念和实际应用。"
                    },
                    {
                        "type": "concept",
                        "title": "核心概念",
                        "explanation": f"在{section_info.get('title', '本章节')}中，我们将学习重要的概念和原理。",
                        "examples": ["概念示例1", "概念示例2"]
                    },
                    {
                        "type": "activity",
                        "title": "实践活动",
                        "description": "通过实践活动来加深对概念的理解",
                        "steps": ["观察和思考", "动手实践", "总结反思"]
                    },
                    {
                        "type": "media",
                        "title": "辅助材料",
                        "description": "相关的图片或视频资源",
                        "media_type": "image",
                        "suggestion": "建议查看相关图表和示意图"
                    },
                    {
                        "type": "assessment",
                        "questions": [
                            {
                                "question": f"请描述{section_info.get('title', '本章节')}的主要内容",
                                "type": "short_answer",
                                "options": [],
                                "answer": "学生应该能够清楚地解释核心概念",
                                "explanation": "这个问题帮助检验学生对核心概念的理解"
                            }
                        ]
                    }
                ]
            }
    
    def _format_list(self, items: List[str]) -> str:
        """将列表格式化为带编号的文本"""
        if not items:
            return "无"
        
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

# 创建一个全局的ContentDesignerAgent实例
content_designer = ContentDesignerAgent()
