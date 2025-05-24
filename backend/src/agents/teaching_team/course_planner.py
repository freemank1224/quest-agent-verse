from typing import Dict, Any, List, Optional
import logging
import json
import re
import sys
import os

from agno.agent import Agent, Message
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2 import Memory

# 导入记忆管理器和模型管理器
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from memory.memory_manager import MemoryManager
from memory.course_memory import CourseMemory
from utils.model_manager import get_agent_model

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoursePlannerAgent:
    """
    CoursePlanner Agent负责根据用户提供的主题，规划并生成一个总体课程大纲
    集成记忆管理功能，能够存储和检索课程大纲
    现在使用统一模型管理器，支持配置化模型切换
    """
    
    def __init__(self, memory_db_path: str = "memory/teaching_memory.db"):
        # 使用统一模型管理器获取配置化的模型
        try:
            # 使用 ollama 的 qwen3_32b 模型替代 grok (xAI API已被封禁)
            model = get_agent_model("teaching_team", "course_planner")
            logger.info(f"成功加载课程规划Agent模型: {type(model).__name__}")
        except Exception as e:
            logger.error(f"加载模型失败，使用默认配置: {e}")
            # 备用：如果模型管理器失败，使用默认Ollama，设置长超时时间
            from agno.models.ollama import Ollama
            model = Ollama(
                id="qwen3:32b", 
                host="http://localhost:11434",
                timeout=600,  # 10分钟超时，适应本地大模型推理时间
                keep_alive="10m"
            )
        
        self.agent = Agent(
            name="CoursePlanner",
            model=model,
            memory=Memory(),
            tools=[
                ReasoningTools()
                # DuckDuckGoTools()
            ],
            description="""
            你是一个专业的 K-12 课程规划专家，擅长根据用户提供的主题来设计课程大纲。你的核心任务包括：

            ## 主题解析
            1. 仔细解析用户输入的学习主题
            2. 如果有背景信息，请提取出学习者的年龄、年级、知识水平、学习目标等关键信息
            3. 根据提取的背景信息来调整课程大纲的内容难易度和教学方法
            4. 如果背景信息不完整，请根据主题特点合理推断适合的年龄段和知识水平

            ## 课程大纲设计
            5. 根据用户提供的学习主题和背景信息（包括学习目标、年龄、知识水平等），设计一个结构完整的课程大纲
            6. 将课程内容分解为合理的章节和子主题
            7. 充分考虑「游戏化学习」和「个性化学习」的理念，为每个章节设定明确的学习目标
            8. 利用已有的课程记忆来避免重复设计和保持一致性，只根据背景信息来调整大纲的内容难易度

            ## 课程标准对齐（必须项）
            9. **与课标对齐是提纲中必须的一项**，请务必调用浏览器工具来确定生成的大纲与相应课标对齐情况
            10. 通过搜索网络，确定与主题对应的体系的课程标准对齐情况：
                - 科学类主题：对齐到最新的「义务教育科学课程标准」中的相应知识点和美国「下一代科学标准」NGSS中的相应知识点
                - 计算机类主题：对齐到「CSTA」中的相应知识点
                - 数学类主题：对齐到「CCSS」中的相应知识点
                - 语文类主题：对齐到「义务教育语文课程标准」中的相应知识点
                - 英语类主题：对齐到「义务教育英语课程标准」中的相应知识点
            11. 为每个章节明确标注对应的课标知识点和能力要求

            ## 教育理论遵循
            课程大纲应当符合教育理论，遵循布鲁姆的认知分层理论，逐步展开。
            
            ## 工作流程
            1. 首先使用浏览器工具搜索相关课程标准
            2. 分析用户输入，提取背景信息
            3. 基于课标要求和背景信息设计课程结构
            4. 确保每个章节都与课标明确对齐
            """
        )
        
        # 初始化记忆管理器
        self.memory_manager = MemoryManager(memory_db_path)
        self.course_memory = CourseMemory(self.memory_manager)
        
        logger.info(f"CoursePlannerAgent initialized with memory manager: {memory_db_path}")
    
    def get_current_model_info(self) -> Dict[str, str]:
        """获取当前使用的模型信息"""
        try:
            from utils.model_manager import get_model_manager
            manager = get_model_manager()
            return manager.get_agent_current_model("teaching_team", "course_planner")
        except Exception as e:
            logger.warning(f"获取模型信息失败: {e}")
            return {"model": "unknown", "provider": "unknown"}
    
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
            success = manager.update_agent_model("teaching_team", "course_planner", model_code)
            
            if success:
                # 获取新模型实例
                new_model = manager.get_model_for_agent("teaching_team", "course_planner")
                
                # 更新Agent的模型
                self.agent.model = new_model
                
                logger.info(f"课程规划Agent成功切换到模型: {model_code}")
                return True
            else:
                logger.error(f"模型切换失败: {model_code}")
                return False
                
        except Exception as e:
            logger.error(f"切换模型时发生错误: {e}")
            return False

    async def create_course_plan(self, topic: str, learning_goal: Optional[str] = None, 
                                target_audience: Optional[str] = None, 
                                knowledge_level: Optional[str] = None,
                                store_to_memory: bool = True) -> Dict[str, Any]:
        """
        根据给定的主题和条件创建课程计划，并可选择存储到记忆管理器
        
        Args:
            topic: 课程主题
            learning_goal: 学习目标
            target_audience: 目标受众，严格遵循用户输入的背景信息中相关的内容
            knowledge_level: 知识水平，严格遵循用户输入的背景信息中相关的内容
            store_to_memory: 是否存储到记忆管理器
            
        Returns:
            Dict[str, Any]: 包含课程计划的字典，包括course_id（如果存储）
        """
        logger.info(f"Creating course plan for topic: {topic}")
        
        # 检查是否已有相似的课程
        existing_courses = self.memory_manager.search_courses_by_topic(topic)
        context_info = []
        
        if existing_courses:
            context_info.append(f"已有相关课程: {existing_courses[0]['title']}")
            # 获取已有课程的详细信息作为参考
            existing_course = self.memory_manager.get_course_outline(existing_courses[0]['id'])
            if existing_course:
                context_info.append(f"参考学习目标: {', '.join(existing_course.get('learning_objectives', []))}")
        
        # 构建发送给Agent的消息
        # 首先准备JSON模板字符串（避免f-string中的大括号冲突）
        json_template = '''{
            "course_title": "课程标题",
            "course_description": "课程概述和介绍",
            "background_analysis": {
                "target_age": "目标年龄/年级",
                "knowledge_level": "知识水平评估",
                "learning_context": "学习背景和环境分析"
            },
            "bloom_taxonomy_objectives": {
                "remember": ["记忆层面的学习目标（如：记住关键概念、术语等）"],
                "understand": ["理解层面的学习目标（如：解释概念、描述原理等）"],
                "apply": ["应用层面的学习目标（如：运用知识解决问题等）"],
                "analyze": ["分析层面的学习目标（如：分析结构、比较差异等）"],
                "evaluate": ["评估层面的学习目标（如：评判价值、批判性思考等）"],
                "create": ["创造层面的学习目标（如：设计方案、创新应用等）"]
            },
            "curriculum_alignment": {
                "standards_used": "使用的课程标准体系（如：义务教育科学课程标准、NGSS等）",
                "alignment_overview": "整体对齐情况说明"
            },
            "chapters": [
                {
                    "id": "章节ID（如：chapter-1）",
                    "title": "章节标题",
                    "description": "章节详细描述",
                    "estimated_duration": "预计学习时间（如：2-3小时）",
                    "bloom_focus": ["本章节重点的布鲁姆层级（如：understand, apply）"],
                    "learning_objectives": ["章节具体学习目标1", "章节具体学习目标2"],
                    "key_concepts": ["核心概念1", "核心概念2", "核心概念3"],
                    "teaching_resources": {
                        "interactive_activities": ["互动活动类型（如：实验、游戏、讨论等）"],
                        "media_types": ["推荐媒体类型（如：视频、图片、动画等）"],
                        "assessment_methods": ["评估方法（如：问答、测试、项目等）"]
                    },
                    "content_design_guidance": {
                        "content_structure": "内容结构建议（如：概念介绍→示例展示→练习应用）",
                        "difficulty_level": "难度等级（如：初级、中级、高级）",
                        "examples_needed": "需要的示例类型（如：生活实例、科学案例等）",
                        "practice_activities": "练习活动建议（如：动手实验、思考题等）"
                    },
                    "curriculum_alignment": "具体课标对齐情况和知识点",
                    "sections": [
                        {
                            "id": "小节ID（如：1.1, 1.2）",
                            "title": "小节标题",
                            "content_type": "内容类型（如：概念讲解、实践活动、评估测试）",
                            "activity_suggestion": "活动建议（如：观察实验、角色扮演等）"
                        }
                    ]
                }
            ]
        }'''
        
        content = f"""请根据以下信息设计一个完整的课程大纲：

课程主题: {topic}"""
        
        if learning_goal:
            content += f"\n学习目标: {learning_goal}"
        if target_audience:
            content += f"\n目标受众: {target_audience}"
        if knowledge_level:
            content += f"\n知识水平: {knowledge_level}"
        
        if context_info:
            content += f"\n\n参考信息:\n{chr(10).join(context_info)}"
            
        content += f"""

## 任务要求：

### 第一步：背景信息分析
请仔细分析上述输入的学习主题和相关信息，提取以下关键背景信息：
- 学习者年龄/年级（如果未明确提供，请根据主题推断）
- 知识水平和先修要求
- 学习目标和预期成果
- 学习背景和环境分析

### 第二步：布鲁姆认知分层目标设计（核心任务）
**重要：必须根据布鲁姆认知分层理论设计学习目标**
- 记忆层面（Remember）：学习者需要记住的关键概念、术语、事实
- 理解层面（Understand）：学习者需要理解的原理、关系、含义
- 应用层面（Apply）：学习者需要能够运用知识解决的问题
- 分析层面（Analyze）：学习者需要能够分析的结构、关系、模式
- 评估层面（Evaluate）：学习者需要能够评判的标准、价值、质量
- 创造层面（Create）：学习者需要能够创造的新想法、方案、产品

**注意：不需要全部覆盖六个层级，但要根据主题特点和学习者水平合理分配**

### 第三步：课程标准对齐（必须完成）
**重要：与课标对齐是必须项，请务必使用浏览器工具搜索相关课程标准**
- 首先搜索并确定该主题对应的课程标准体系
- 找到具体的知识点和能力要求
- 为课程大纲的每个章节明确标注课标对齐情况

### 第四步：章节结构设计
设计合理的章节结构，每个章节必须包含：
1. **基本信息**：标题、描述、预计时间
2. **学习目标**：与布鲁姆分层对应的具体目标
3. **核心概念**：本章节要掌握的关键概念
4. **教学资源规划**：
   - 互动活动类型（实验、游戏、讨论、角色扮演等）
   - 推荐媒体类型（视频、图片、动画、模拟器等）
   - 评估方法（问答、测试、项目、作品集等）

### 第五步：ContentDesigner指导方案设计（关键任务）
**这是最重要的部分，必须为每个章节提供详细的内容设计指导**
为每个章节生成 content_design_guidance，包括：
1. **内容结构建议**：如"概念介绍→原理讲解→示例展示→练习应用→总结巩固"
2. **难度等级**：根据背景分析确定适合的难度
3. **示例需求**：需要什么类型的示例（生活实例、科学案例、历史事件等）
4. **练习活动建议**：具体的实践活动设计（动手实验、思考题、项目制作等）

### 第六步：小节活动设计
为每个小节提供：
- **内容类型**：概念讲解、实践活动、评估测试、综合应用等
- **活动建议**：具体的教学活动（观察实验、小组讨论、创意制作等）

## 格式要求：
请严格按照以下JSON格式返回你的回答，**必须完全遵循模板结构，不得遗漏任何字段**：
{json_template}

**关键要求：**
1. ✅ 必须使用浏览器工具搜索相关课程标准
2. ✅ 必须完整填写所有JSON字段，不得省略
3. ✅ bloom_taxonomy_objectives 必须根据主题特点合理分配
4. ✅ content_design_guidance 必须详细具体，能够指导ContentDesigner
5. ✅ teaching_resources 必须包含具体的活动和媒体建议
6. ✅ 根据背景信息调整内容难度和教学方法
7. ✅ 体现游戏化学习和个性化学习理念
8. ✅ 确保JSON格式完全正确，可以被程序解析

**返回格式检查清单：**
- [ ] JSON格式完整无误
- [ ] 所有必需字段都已填写
- [ ] content_design_guidance 详细具体
- [ ] teaching_resources 包含具体建议
- [ ] bloom_taxonomy_objectives 合理分配
- [ ] curriculum_alignment 明确具体"""
        
        # 创建消息
        message = Message(role="user", content=content)
        
        # 发送消息并获取回复
        logger.info("Sending message to agno agent...")
        response = await self.agent.arun(message)
        logger.info(f"Raw response from agno: {response.content}")
        
        # 清理响应内容，移除thinking标签和其他非JSON内容
        cleaned_content = response.content
        
        # 移除<think>标签及其内容
        cleaned_content = re.sub(r'<think>.*?</think>', '', cleaned_content, flags=re.DOTALL)
        
        # 移除其他可能的标签
        cleaned_content = re.sub(r'<.*?>', '', cleaned_content)
        
        # 移除多余的空白行
        cleaned_content = '\n'.join(line.strip() for line in cleaned_content.split('\n') if line.strip())
        
        logger.info(f"Cleaned response: {cleaned_content}")
        
        course_plan = None
        
        try:
            # 首先尝试直接解析JSON
            course_plan = json.loads(cleaned_content)
            logger.info("Successfully parsed response as JSON")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse response as direct JSON: {e}")
            
            # 尝试从markdown代码块中提取JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', cleaned_content, re.DOTALL)
            if json_match:
                try:
                    course_plan = json.loads(json_match.group(1))
                    logger.info("Successfully extracted JSON from markdown code block")
                except json.JSONDecodeError as e2:
                    logger.warning(f"Failed to parse extracted JSON: {e2}")
            
            if not course_plan:
                # 尝试寻找任何JSON对象
                json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                json_matches = re.findall(json_pattern, cleaned_content, re.DOTALL)
                for match in json_matches:
                    try:
                        course_plan = json.loads(match)
                        logger.info("Successfully found and parsed JSON object in response")
                        break
                    except json.JSONDecodeError:
                        continue
            
            # 如果所有解析都失败，创建一个默认格式的响应
            if not course_plan:
                logger.warning("All JSON parsing attempts failed, creating default response")
                course_plan = {
                    "course_title": f"{topic} 课程大纲",
                    "course_description": f"关于{topic}的综合学习课程",
                    "learning_objectives": ["掌握基础概念", "理解核心原理", "能够实际应用"],
                    "sections": [
                        {
                            "id": "1",
                            "title": f"{topic} 基础介绍",
                            "description": f"介绍{topic}的基本概念和原理",
                            "learning_objectives": ["了解基本概念", "掌握基础知识"],
                            "key_points": ["基础概念", "核心原理"],
                            "subsections": [
                                {"id": "1.1", "title": "概念介绍"},
                                {"id": "1.2", "title": "基础原理"}
                            ]
                        },
                        {
                            "id": "2", 
                            "title": f"{topic} 深入学习",
                            "description": f"深入学习{topic}的高级内容",
                            "learning_objectives": ["深入理解", "熟练应用"],
                            "key_points": ["高级概念", "实际应用"],
                            "subsections": [
                                {"id": "2.1", "title": "高级概念"},
                                {"id": "2.2", "title": "实际应用"}
                            ]
                        }
                    ]
                }
        
        # 存储课程大纲到记忆管理器
        if store_to_memory and course_plan:
            try:
                creator_info = {
                    "agent": "CoursePlannerAgent",
                    "model_info": self.get_current_model_info(),
                    "learning_goal": learning_goal,
                    "target_audience": target_audience,
                    "knowledge_level": knowledge_level
                }
                
                course_id = self.course_memory.store_course_outline(
                    topic, course_plan, creator_info
                )
                course_plan['course_id'] = course_id
                logger.info(f"Course plan stored to memory with ID: {course_id}")
            except Exception as e:
                logger.warning(f"Failed to store course plan to memory: {e}")
        
        return course_plan
    
    def get_course_plan(self, course_id: int) -> Optional[Dict[str, Any]]:
        """
        从记忆管理器中获取课程大纲
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程大纲或None
        """
        return self.memory_manager.get_course_outline(course_id)
    
    def search_courses(self, topic_keywords: str) -> List[Dict[str, Any]]:
        """
        搜索相关的课程大纲
        
        Args:
            topic_keywords: 搜索关键词
            
        Returns:
            相关课程列表
        """
        return self.memory_manager.search_courses_by_topic(topic_keywords)
    
    def get_course_structure(self, course_id: int) -> Dict[str, Any]:
        """
        获取课程的完整结构信息
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程结构信息
        """
        return self.course_memory.get_course_structure(course_id)

# 创建一个全局的CoursePlannerAgent实例
course_planner = CoursePlannerAgent()
