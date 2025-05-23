import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .memory_manager import MemoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourseMemory:
    """
    课程记忆管理组件
    
    专门负责课程内容的存储、检索和管理，包括：
    1. 课程大纲存储和查询
    2. 章节内容管理
    3. 课程进度跟踪
    4. 内容关联和版本管理
    """
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """
        初始化课程记忆组件
        
        Args:
            memory_manager: 记忆管理器实例，如果为None则创建新实例
        """
        self.memory_manager = memory_manager or MemoryManager()
        logger.info("CourseMemory initialized")
    
    def store_course_outline(self, topic: str, outline_data: Dict[str, Any], 
                           creator_info: Optional[Dict[str, Any]] = None) -> int:
        """
        存储课程大纲到记忆中
        
        Args:
            topic: 课程主题
            outline_data: CoursePlannerAgent生成的课程大纲数据
            creator_info: 创建者信息（可选）
            
        Returns:
            course_id: 存储的课程ID
        """
        logger.info(f"Storing course outline for topic: {topic}")
        
        # 增强课程数据，添加元信息
        enhanced_outline = outline_data.copy()
        enhanced_outline['metadata'] = {
            'creator': creator_info or {'agent': 'CoursePlannerAgent'},
            'creation_method': 'ai_generated',
            'topic_keywords': self._extract_keywords(topic),
            'storage_timestamp': datetime.now().isoformat()
        }
        
        course_id = self.memory_manager.store_course_outline(topic, enhanced_outline)
        
        logger.info(f"Course outline stored successfully with ID: {course_id}")
        return course_id
    
    def store_section_content(self, course_id: int, section_info: Dict[str, Any],
                            content_data: Dict[str, Any]) -> int:
        """
        存储章节内容到记忆中
        
        Args:
            course_id: 课程ID
            section_info: 章节信息
            content_data: ContentDesignerAgent生成的章节内容
            
        Returns:
            content_id: 存储的内容ID
        """
        section_id = section_info.get('id', 'unknown')
        title = section_info.get('title', '未命名章节')
        
        logger.info(f"Storing section content for section: {section_id}")
        
        # 增强内容数据，添加元信息
        enhanced_content = content_data.copy()
        enhanced_content['metadata'] = {
            'section_info': section_info,
            'creator': {'agent': 'ContentDesignerAgent'},
            'creation_method': 'ai_generated',
            'storage_timestamp': datetime.now().isoformat(),
            'content_type': 'structured_teaching_material'
        }
        
        content_id = self.memory_manager.store_section_content(
            course_id, section_id, title, enhanced_content
        )
        
        logger.info(f"Section content stored successfully with ID: {content_id}")
        return content_id
    
    def get_course_by_topic(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        根据主题获取课程大纲
        
        Args:
            topic: 课程主题
            
        Returns:
            课程数据或None
        """
        courses = self.memory_manager.search_courses_by_topic(topic)
        
        if courses:
            # 返回最新的匹配课程
            latest_course = courses[0]
            course_data = self.memory_manager.get_course_outline(latest_course['id'])
            return course_data
        
        return None
    
    def get_section_content_by_id(self, section_id: str) -> Optional[Dict[str, Any]]:
        """
        根据章节ID获取章节内容
        
        Args:
            section_id: 章节ID
            
        Returns:
            章节内容或None
        """
        return self.memory_manager.get_section_content(section_id)
    
    def get_course_sections(self, course_id: int) -> List[Dict[str, Any]]:
        """
        获取课程的所有章节
        
        Args:
            course_id: 课程ID
            
        Returns:
            章节列表
        """
        course_data = self.memory_manager.get_course_outline(course_id)
        if course_data:
            return course_data.get('sections', [])
        return []
    
    def search_related_content(self, keywords: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相关的课程内容
        
        Args:
            keywords: 搜索关键词
            limit: 返回结果限制
            
        Returns:
            相关内容列表
        """
        courses = self.memory_manager.search_courses_by_topic(keywords)
        return courses[:limit]
    
    def get_course_structure(self, course_id: int) -> Dict[str, Any]:
        """
        获取课程的完整结构信息
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程结构信息
        """
        course_data = self.memory_manager.get_course_outline(course_id)
        if not course_data:
            return {}
        
        # 获取所有章节的详细信息
        sections = course_data.get('sections', [])
        detailed_sections = []
        
        for section in sections:
            section_id = section.get('id')
            if section_id:
                content = self.memory_manager.get_section_content(section_id)
                if content:
                    section['has_content'] = True
                    section['content_created_at'] = content['created_at']
                else:
                    section['has_content'] = False
            detailed_sections.append(section)
        
        return {
            'course_info': course_data,
            'sections': detailed_sections,
            'total_sections': len(sections),
            'sections_with_content': sum(1 for s in detailed_sections if s.get('has_content', False))
        }
    
    def update_course_progress(self, course_id: int, progress_info: Dict[str, Any]):
        """
        更新课程进度信息
        
        Args:
            course_id: 课程ID
            progress_info: 进度信息
        """
        # 这里可以添加课程级别的进度跟踪逻辑
        # 目前先记录到日志
        logger.info(f"Course {course_id} progress updated: {progress_info}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            关键词列表
        """
        # 简单的关键词提取，实际应用中可以使用更复杂的NLP方法
        import re
        
        # 移除标点符号，分割单词
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤常见停用词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个'}
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 返回去重后的关键词
        return list(set(keywords))