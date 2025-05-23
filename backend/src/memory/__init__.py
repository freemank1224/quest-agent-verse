"""
AI教学系统记忆管理模块

该模块提供了完整的记忆管理功能，包括：
- 课程内容存储和检索
- 学习进度跟踪
- 教学记录管理
- 主题控制和记忆辅助功能
"""

from .memory_manager import MemoryManager
from .course_memory import CourseMemory

__all__ = ["MemoryManager", "CourseMemory"] 