from typing import Dict, Any, List, Optional
import logging
import json
import re
import sys
import os

from agno.agent import Agent, Message
from agno.models.ollama import Ollama
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2 import Memory

# 导入记忆管理器
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from memory.memory_manager import MemoryManager
from memory.course_memory import CourseMemory

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentDesignerAgent:
    """
    ContentDesigner Agent负责根据课程大纲设计章节的详细内容
    集成记忆管理功能，能够存储和检索课程内容
    """
    
    def __init__(self, memory_db_path: str = "memory/teaching_memory.db"):
        # 使用 xAI 作为主要模型
        self.agent = Agent(
            name="ContentDesigner",
            model=Ollama(id="qwen3:32b", host="http://localhost:11434"),  # 使用Ollama的Qwen模型
            # model=xAI(id="grok-3-beta", api_key=os.environ.get('XAI_API_KEY')),  # 使用xAI的Grok模型
            memory=Memory(),
            tools=[
                ReasoningTools()
                # DuckDuckGoTools()
            ],
            description="""
            你是一个专业的教育专家，负责设计高质量的教学内容。你的核心任务是：

            ## 内容设计基础
            1. 严格遵循课程规划团队(CoursePlanner)制定的整体课程大纲和框架
            2. 创建结构清晰、易于理解的教学材料，保持课程内容的一致性和连贯性
            3. 确保每个章节内容与整体课程目标和课标要求完全对齐
            4. 必须理解当前章节在整个课程中的位置和作用，不能仅凭章节标题孤立地创建内容

            ## 记忆与连贯性利用
            5. 充分利用CoursePlanner的课程记忆，包括课程标题、描述、布鲁姆分类目标、课标对齐等
            6. 明确考虑当前章节与前后章节的关系，确保内容的逻辑流程和知识构建是连贯的
            7. 根据章节在课程中的位置和作用调整内容深度和广度，前置章节应打好基础，后续章节应建立在前置知识上

            ## 用户背景适应
            8. 严格根据提供的用户背景信息（如年龄、知识水平、学习目标）定制内容难度和教学方法
            9. 如果用户背景信息不完整，参考课程设计中的默认受众信息

            ## 内容质量要求
            10. 确定核心知识点和学习要点，确保与布鲁姆分类目标对应
            11. 建议合适的教学媒体（图像、视频等）和互动活动，符合章节设计指南
            12. 根据章节的内容设计指导(content_design_guidance)调整内容结构、难度等级等
            
            教学内容必须符合教育理论，使用适当的教学方法和策略。你的设计应该确保学习者能够按照课程的整体规划，在理解前置知识的基础上，平稳地过渡到当前章节的学习内容。
            """
        )
        
        # 初始化记忆管理器
        self.memory_manager = MemoryManager(memory_db_path)
        self.course_memory = CourseMemory(self.memory_manager)
        
        logger.info(f"ContentDesignerAgent initialized with memory manager: {memory_db_path}")
    
    async def create_content(self, section_info: Dict[str, Any], 
                           course_id: Optional[int] = None,
                           course_topic: Optional[str] = None,
                           user_background: Optional[Dict[str, Any]] = None,
                           chapter_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        为特定章节创建内容，并存储到记忆管理器中
        
        Args:
            section_info: 包含章节信息的字典，应当包含id, title, description等字段
            course_id: 课程ID（可选）
            course_topic: 课程主题（可选，用于搜索相关内容）
            user_background: 用户背景信息，包含年龄、学习目标、知识水平等（可选）
            chapter_info: 增强的章节信息，包含content_design_guidance等字段（可选）
            
        Returns:
            Dict[str, Any]: 包含章节内容的字典
        """
        logger.info(f"Creating content for section: {section_info.get('title', 'Unknown')}")
        
        # 获取相关的课程内容作为上下文
        context_info = []
        course_outline = None
        
        # 首先尝试通过课程ID获取完整的课程大纲
        if course_id:
            course_outline = self.memory_manager.get_course_outline(course_id)
            if course_outline:
                # 添加课程基本信息
                context_info.append(f"课程标题: {course_outline.get('course_title', course_outline.get('title', '未知'))}")
                if 'course_description' in course_outline:
                    context_info.append(f"课程描述: {course_outline['course_description']}")
                
                # 添加课程学习目标
                if 'learning_objectives' in course_outline:
                    context_info.append(f"课程整体学习目标: {', '.join(course_outline['learning_objectives'])}")
                
                # 添加课程的布鲁姆分类层级目标
                if 'bloom_taxonomy_objectives' in course_outline and isinstance(course_outline['bloom_taxonomy_objectives'], dict):
                    bloom_info = []
                    for level, objectives in course_outline['bloom_taxonomy_objectives'].items():
                        if objectives and len(objectives) > 0:
                            bloom_info.append(f"{level}: {'; '.join(objectives)}")
                    if bloom_info:
                        context_info.append(f"课程布鲁姆分类层级目标:\n" + '\n'.join(bloom_info))
                
                # 添加课标对齐信息
                if 'curriculum_alignment' in course_outline:
                    if isinstance(course_outline['curriculum_alignment'], dict):
                        ca = course_outline['curriculum_alignment']
                        context_info.append(f"课程标准: {ca.get('standards_used', '未指定')}")
                        context_info.append(f"课标对齐概述: {ca.get('alignment_overview', '未指定')}")
                    elif isinstance(course_outline['curriculum_alignment'], str):
                        context_info.append(f"课标对齐: {course_outline['curriculum_alignment']}")
                
                # 提取当前章节所在的完整章节信息及其在课程中的位置
                if 'chapters' in course_outline and section_info and 'id' in section_info:
                    section_id = section_info['id']
                    current_chapter = None
                    for chapter in course_outline['chapters']:
                        if 'sections' in chapter:
                            for section in chapter['sections']:
                                if section.get('id') == section_id:
                                    current_chapter = chapter
                                    break
                            if current_chapter:
                                break
                    
                    if current_chapter:
                        # 添加当前章节所在的章的总体信息
                        context_info.append(f"所属章节: {current_chapter.get('title', '未知')}")
                        if 'description' in current_chapter:
                            context_info.append(f"章节描述: {current_chapter['description']}")
                        if 'learning_objectives' in current_chapter:
                            context_info.append(f"章节学习目标: {', '.join(current_chapter['learning_objectives'])}")
                        if 'key_concepts' in current_chapter:
                            context_info.append(f"章节核心概念: {', '.join(current_chapter['key_concepts'])}")
                        
                        # 添加章节在课程中的位置关系
                        chapter_index = course_outline['chapters'].index(current_chapter)
                        context_info.append(f"章节编号: 第{chapter_index + 1}章，共{len(course_outline['chapters'])}章")
                        
                        # 添加前后章节的信息以建立连贯性
                        if chapter_index > 0:
                            prev_chapter = course_outline['chapters'][chapter_index - 1]
                            context_info.append(f"前置章节: {prev_chapter.get('title', '未知')}")
                        
                        if chapter_index < len(course_outline['chapters']) - 1:
                            next_chapter = course_outline['chapters'][chapter_index + 1]
                            context_info.append(f"后续章节: {next_chapter.get('title', '未知')}")
                        
                        # 添加当前章节中其他小节的信息，建立小节之间的关系
                        if 'sections' in current_chapter:
                            section_index = -1
                            for i, sec in enumerate(current_chapter['sections']):
                                if sec.get('id') == section_id:
                                    section_index = i
                                    break
                            
                            if section_index != -1:
                                context_info.append(f"小节编号: 第{section_index + 1}节，共{len(current_chapter['sections'])}节")
                                
                                # 添加相邻小节信息
                                if section_index > 0:
                                    prev_section = current_chapter['sections'][section_index - 1]
                                    context_info.append(f"前置小节: {prev_section.get('title', '未知')}")
                                
                                if section_index < len(current_chapter['sections']) - 1:
                                    next_section = current_chapter['sections'][section_index + 1]
                                    context_info.append(f"后续小节: {next_section.get('title', '未知')}")
        
        # 如果没有通过课程ID获取到信息，尝试通过课程主题搜索相关课程
        if course_topic and not course_outline:
            related_courses = self.memory_manager.search_courses_by_topic(course_topic)
            if related_courses:
                context_info.append(f"相关课程: {related_courses[0]['title']}")
                
                # 尝试获取相关课程的详细信息
                related_outline = self.memory_manager.get_course_outline(related_courses[0]['id'])
                if related_outline:
                    context_info.append(f"相关课程描述: {related_outline.get('course_description', '未知')}")
                    if 'learning_objectives' in related_outline:
                        context_info.append(f"相关课程学习目标: {', '.join(related_outline.get('learning_objectives', []))}")
        
        # 构建发送给Agent的消息
        # 首先准备JSON模板字符串（避免f-string中的大括号冲突）
        json_template = '''{
  "title": "章节标题",
  "mainContent": "主要内容（使用Markdown格式）",
  "keyPoints": ["关键知识点1", "关键知识点2", "关键知识点3"],
  "images": [
    {
      "url": "/placeholder.svg",
      "caption": "图片说明"
    }
  ],
  "curriculumAlignment": ["课标对齐点1", "课标对齐点2"],
  "activities": [
    {
      "type": "interactive",
      "title": "活动标题",
      "description": "活动描述",
      "instructions": ["步骤1", "步骤2", "步骤3"],
      "materials": ["所需材料1", "所需材料2"]
    }
  ],
  "assessments": [
    {
      "type": "quiz",
      "questions": [
        {
          "question": "问题描述",
          "type": "multiple_choice",
          "options": ["选项A", "选项B", "选项C", "选项D"],
          "correct_answer": "A",
          "explanation": "答案解释"
        }
      ]
    }
  ]
}'''
        
        # 构建内容设计指导信息
        design_guidance_content = ""
        if chapter_info and chapter_info.get('content_design_guidance'):
            guidance = chapter_info['content_design_guidance']
            design_guidance_content = f"""

## 内容设计指导（重要：必须严格遵循）
- 内容结构: {guidance.get('content_structure', '未指定')}
- 难度等级: {guidance.get('difficulty_level', '未指定')}
- 示例需求: {guidance.get('examples_needed', '未指定')}
- 练习活动: {guidance.get('practice_activities', '未指定')}

请严格按照上述指导设计内容，确保结构清晰、难度适当、示例充分、练习有效。"""

        # 构建教学资源建议
        teaching_resources_content = ""
        if chapter_info and chapter_info.get('teaching_resources'):
            resources = chapter_info['teaching_resources']
            teaching_resources_content = f"""

## 教学资源建议
- 互动活动: {', '.join(resources.get('interactive_activities', []))}
- 媒体类型: {', '.join(resources.get('media_types', []))}
- 评估方法: {', '.join(resources.get('assessment_methods', []))}

请在内容中体现这些教学资源的使用。"""

        # 构建布鲁姆分层目标
        bloom_objectives_content = ""
        if chapter_info and chapter_info.get('bloom_focus'):
            bloom_objectives_content = f"""

## 布鲁姆认知层级重点
本章节重点关注: {', '.join(chapter_info['bloom_focus'])}
请确保内容设计能够帮助学习者达到相应的认知层级。"""

        # 构建用户背景信息部分
        background_content = ""
        if user_background:
            background_content = f"""

## 用户背景信息（请在设计内容时充分考虑）
- 年龄/年级: {user_background.get('age', '未知')}
- 学习目标: {user_background.get('learningGoal', '未知')}
- 时间偏好: {user_background.get('timePreference', '未知')}
- 知识水平: {user_background.get('knowledgeLevel', '未知')}
- 目标受众: {user_background.get('targetAudience', '未知')}

请根据以上背景信息调整：
1. 内容难度和深度（根据年龄和知识水平）
2. 教学方法和活动设计（符合学习目标和时间偏好）
3. 示例和练习的复杂度
4. 语言表达的方式和风格"""

        content = f"""请根据以下信息，设计一个符合整体课程规划和教育理论的详细教学内容：

## 当前章节基本信息
章节ID: {section_info.get('id', 'Unknown')}
章节标题: {section_info.get('title', 'Unknown')}
章节描述: {section_info.get('description', 'No description provided')}
内容类型: {section_info.get('content_type', '概念讲解')}
活动建议: {section_info.get('activity_suggestion', '无特殊建议')}

学习目标:
{self._format_list(section_info.get('learning_objectives', []))}

关键要点:
{self._format_list(section_info.get('key_points', []))}

## 课程整体上下文（重要：内容设计必须与整体课程规划保持一致）
"""

        if context_info:
            content += f"{chr(10).join(context_info)}"
        else:
            content += "无可用的课程整体上下文信息，请确保内容的连贯性和适当的难度水平。"

        content += f"""

{design_guidance_content}
{teaching_resources_content}
{bloom_objectives_content}
{background_content}

## 设计要求（非常重要，请严格遵循）：
1. 内容必须与整体课程规划和课标要求保持一致
2. 考虑当前章节在整个课程中的位置，与前后章节建立清晰的知识连接
3. 根据用户背景和章节指导调整内容难度和教学方法
4. 确保内容支持布鲁姆分类层级中指定的认知目标
5. 提供详细的教学内容，包括概念解释、生动的示例和实际应用
6. 设计符合教育理论的教学活动和练习
7. 建议适合目标受众的教学媒体和资源
8. 开发有效的评估方法和问题

请以JSON格式返回你的回答，确保格式完全正确：
{json_template}
"""
        
        # 添加系统消息，强调利用CoursePlanner的记忆
        system_message = """你是一个专业的教学内容设计专家ContentDesigner。
        
重要指导原则：
1. 你必须完全遵循CoursePlanner的整体课程规划，将当前章节视为整体知识结构的一部分
2. 课程的连贯性至关重要 - 必须考虑前序和后续章节，构建清晰的知识脉络
3. 内容设计必须与课程大纲中定义的布鲁姆分类目标、课标对齐等保持一致
4. 用户背景信息是内容难度和教学方法设计的关键依据

请记住，你不是独立创作内容，而是严格按照整体课程规划来设计当前章节的具体内容。"""
        
        # 创建消息
        message = Message(role="user", content=content)
        
        # 发送消息并获取回复
        logger.info("=== CONTENT DESIGNER DEBUG ===")
        logger.info(f"章节信息: {section_info}")
        logger.info(f"是否有增强章节信息: {chapter_info is not None}")
        if chapter_info:
            logger.info(f"增强章节信息详情: {json.dumps(chapter_info, ensure_ascii=False, indent=2)}")
        logger.info(f"发送给Agent的完整消息内容: {content}")
        logger.info("=== 开始调用Ollama ===")
        
        # 设置系统提示，但不改变当前的agent.arun接口调用方式
        self.agent.model.system = system_message
        response = await self.agent.arun(message)
        
        logger.info("=== Ollama响应完成 ===")
        logger.info(f"原始响应长度: {len(response.content)} 字符")
        logger.info(f"原始响应前500字符: {response.content[:500]}")
        logger.info(f"原始响应后500字符: {response.content[-500:]}")
        
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
            
            # 存储内容到记忆管理器
            if course_id:
                try:
                    content_id = self.course_memory.store_section_content(
                        course_id, section_info, section_content
                    )
                    logger.info(f"Section content stored to memory with ID: {content_id}")
                except Exception as e:
                    logger.warning(f"Failed to store section content to memory: {e}")
            
            return section_content
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse ContentDesigner response as direct JSON: {e}")
            
            # 尝试从markdown代码块中提取JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', cleaned_content, re.DOTALL)
            if json_match:
                try:
                    section_content = json.loads(json_match.group(1))
                    logger.info("Successfully extracted JSON from markdown code block")
                    
                    # 存储内容到记忆管理器
                    if course_id:
                        try:
                            content_id = self.course_memory.store_section_content(
                                course_id, section_info, section_content
                            )
                            logger.info(f"Section content stored to memory with ID: {content_id}")
                        except Exception as e:
                            logger.warning(f"Failed to store section content to memory: {e}")
                    
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
                    
                    # 存储内容到记忆管理器
                    if course_id:
                        try:
                            content_id = self.course_memory.store_section_content(
                                course_id, section_info, section_content
                            )
                            logger.info(f"Section content stored to memory with ID: {content_id}")
                        except Exception as e:
                            logger.warning(f"Failed to store section content to memory: {e}")
                    
                    return section_content
                except json.JSONDecodeError:
                    continue
            
            # 如果所有解析都失败，创建一个默认格式的响应
            logger.warning("All JSON parsing attempts failed, creating default content structure")
            default_content = {
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
            
            # 存储默认内容到记忆管理器
            if course_id:
                try:
                    content_id = self.course_memory.store_section_content(
                        course_id, section_info, default_content
                    )
                    logger.info(f"Default section content stored to memory with ID: {content_id}")
                except Exception as e:
                    logger.warning(f"Failed to store default section content to memory: {e}")
            
            return default_content
    
    async def get_full_course_context(self, course_id: int) -> Dict[str, Any]:
        """
        获取完整的课程上下文信息，包括课程大纲、布鲁姆分类目标、课标对齐等
        作为ContentDesigner的全局指导
        
        Args:
            course_id: 课程ID
            
        Returns:
            Dict[str, Any]: 包含完整课程上下文的字典
        """
        logger.info(f"获取课程ID {course_id} 的完整上下文信息")
        
        try:
            # 获取课程大纲
            course_outline = self.memory_manager.get_course_outline(course_id)
            if not course_outline:
                logger.warning(f"未找到课程ID {course_id} 的大纲信息")
                return {}
            
            # 获取课程结构
            course_structure = self.course_memory.get_course_structure(course_id)
            
            # 构建完整的课程上下文信息
            full_context = {
                "course_info": {
                    "id": course_id,
                    "title": course_outline.get("course_title", course_outline.get("title")),
                    "description": course_outline.get("course_description", ""),
                },
                "bloom_taxonomy_objectives": course_outline.get("bloom_taxonomy_objectives", {}),
                "curriculum_alignment": course_outline.get("curriculum_alignment", {}),
                "background_analysis": course_outline.get("background_analysis", {}),
                "structure": course_structure
            }
            
            logger.info(f"成功获取课程ID {course_id} 的完整上下文信息")
            return full_context
        except Exception as e:
            logger.error(f"获取课程上下文信息时发生错误: {e}")
            return {}
    
    def get_section_content(self, section_id: str) -> Optional[Dict[str, Any]]:
        """
        从记忆管理器中获取章节内容
        
        Args:
            section_id: 章节ID
            
        Returns:
            章节内容或None
        """
        return self.course_memory.get_section_content_by_id(section_id)
    
    def search_related_content(self, keywords: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相关的课程内容
        
        Args:
            keywords: 搜索关键词
            limit: 返回结果限制
            
        Returns:
            相关内容列表
        """
        return self.course_memory.search_related_content(keywords, limit)
    
    def _format_list(self, items: List[str]) -> str:
        """将列表格式化为带编号的文本，支持字符串、字典和列表多种格式"""
        if not items:
            return "无"
        
        if isinstance(items, list):
            formatted_items = []
            for i, item in enumerate(items):
                if isinstance(item, str):
                    formatted_items.append(f"{i+1}. {item}")
                elif isinstance(item, dict):
                    # 尝试提取字典中的关键信息
                    item_text = item.get('description', item.get('text', item.get('name', str(item))))
                    formatted_items.append(f"{i+1}. {item_text}")
                else:
                    formatted_items.append(f"{i+1}. {str(item)}")
            return "\n".join(formatted_items)
        elif isinstance(items, dict):
            # 处理字典格式，常见于布鲁姆分类目标等
            formatted_items = []
            for key, values in items.items():
                if isinstance(values, list) and values:
                    formatted_items.append(f"【{key}】: {', '.join(values)}")
            return "\n".join(formatted_items) if formatted_items else "无"
        else:
            return str(items)

# 创建一个全局的ContentDesignerAgent实例
content_designer = ContentDesignerAgent()
