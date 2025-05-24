from typing import Dict, Any, List, Optional
import logging
import json

from agno.agent import Agent, Message
from agno.models.ollama import Ollama
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2 import Memory

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentVerifierAgent:
    """
    ContentVerifier Agent负责验证和审核教学内容
    """
    
    def __init__(self):
        # 使用 xAI 作为主要模型
        self.agent = Agent(
            name="ContentVerifier",
            model=Ollama(id="qwen3:32b", host="http://localhost:11434"),
            memory=Memory(),
            tools=[
                ReasoningTools(),
                DuckDuckGoTools()
            ],
            description="""
            你是一个专业的教育内容审核专家，负责验证和改进教学内容质量。你的任务是：
            1. 检查教学内容的准确性和完整性
            2. 评估内容与学习目标的一致性
            3. 评估内容的教学有效性和吸引力
            4. 审核内容是否符合教育标准和规范
            5. 提供改进建议和修改意见
            
            你的评审应当客观、全面、建设性，确保内容符合高质量教学标准。
            """
        )
        logger.info("ContentVerifierAgent initialized")
    
    async def verify_content(self, content: Dict[str, Any], learning_objectives: List[str], 
                           user_background: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        验证教学内容
        
        Args:
            content: 要验证的教学内容
            learning_objectives: 学习目标列表
            user_background: 用户背景信息，包含年龄、学习目标、知识水平等（可选）
            
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        logger.info("Verifying content")
        
        # 将内容转换为字符串形式
        content_str = json.dumps(content, ensure_ascii=False, indent=2)
        
        # 构建用户背景信息部分
        background_content = ""
        if user_background:
            background_content = f"""
        
        用户背景信息（请在评审时充分考虑）:
        - 年龄/年级: {user_background.get('age', '未知')}
        - 学习目标: {user_background.get('learningGoal', '未知')}
        - 时间偏好: {user_background.get('timePreference', '未知')}
        - 知识水平: {user_background.get('knowledgeLevel', '未知')}
        - 目标受众: {user_background.get('targetAudience', '未知')}
        
        请特别评估：
        1. 内容难度是否适合目标年龄和知识水平
        2. 教学方法是否符合学习目标和时间偏好
        3. 内容是否有助于实现个人学习目标"""

        # 构建发送给Agent的消息
        prompt = f"""
        请评审以下教学内容的质量和有效性：
        
        学习目标:
        {self._format_list(learning_objectives)}
        
        教学内容:
        {content_str}
        
        {background_content}
        
        请从以下几个方面评审并给出分数（1-10分）和改进建议：
        1. 准确性：内容是否准确无误
        2. 完整性：内容是否完整覆盖了所有必要知识点
        3. 一致性：内容是否与学习目标一致
        4. 教学有效性：内容是否有助于学习者理解和掌握知识
        5. 吸引力：内容是否能够吸引学习者的兴趣
        
        请以JSON格式返回你的评审结果，结构如下：
        {
          "accuracy": {
            "score": 分数,
            "comments": "评语",
            "suggestions": ["建议1", "建议2"]
          },
          "completeness": {
            "score": 分数,
            "comments": "评语",
            "suggestions": ["建议1", "建议2"]
          },
          "alignment": {
            "score": 分数,
            "comments": "评语",
            "suggestions": ["建议1", "建议2"]
          },
          "effectiveness": {
            "score": 分数,
            "comments": "评语",
            "suggestions": ["建议1", "建议2"]
          },
          "engagement": {
            "score": 分数,
            "comments": "评语",
            "suggestions": ["建议1", "建议2"]
          },
          "overall": {
            "score": 总分,
            "comments": "总体评语",
            "major_strengths": ["优点1", "优点2"],
            "major_weaknesses": ["缺点1", "缺点2"]
          }
        }
        """
        
        # 创建消息
        message = Message(role="user", content=prompt)
        
        # 发送消息并获取回复
        response = await self.agent.arun(message)
        
        try:
            # 尝试解析JSON响应
            verification_result = json.loads(response.content)
            logger.info("Content verification completed")
            return verification_result
        except json.JSONDecodeError:
            # 如果不是有效的JSON，返回原始文本
            logger.warning("Failed to parse verification result as JSON, returning raw text")
            return {"raw_response": response.content}
    
    def _format_list(self, items: List[str]) -> str:
        """将列表格式化为带编号的文本"""
        if not items:
            return "无"
        
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

# 创建一个全局的ContentVerifierAgent实例
content_verifier = ContentVerifierAgent()
