"""
AI教学系统记忆管理模块

该模块提供了完整的记忆管理功能，包括：
- 课程内容存储和检索
- 学习进度跟踪
- 教学记录管理
- 主题控制和记忆辅助功能

现在支持两种memory实现：
1. 原始SQLite实现 (MemoryManager, CourseMemory)
2. 基于Agno v2 Memory的实现 (AgnoMemoryManager, AgnoCourseMemory) - 推荐

使用环境变量 USE_AGNO_MEMORY=true 来启用新的agno memory系统
"""

import os
from typing import Type, Union

# 导入原始实现
from .memory_manager import MemoryManager
from .course_memory import CourseMemory

# 导入新的agno实现
from .agno_memory_manager import AgnoMemoryManager
from .agno_course_memory import AgnoCourseMemory

# 导入迁移工具
from .migrate_to_agno import MemoryMigrator

# 检查是否启用agno memory
USE_AGNO_MEMORY = os.getenv('USE_AGNO_MEMORY', 'false').lower() == 'true'

# 动态选择实现
if USE_AGNO_MEMORY:
    # 使用agno实现作为默认实现
    DefaultMemoryManager = AgnoMemoryManager
    DefaultCourseMemory = AgnoCourseMemory
    print("使用Agno Memory v2系统")
else:
    # 使用原始实现作为默认实现
    DefaultMemoryManager = MemoryManager
    DefaultCourseMemory = CourseMemory
    print("使用原始SQLite Memory系统")

# 为了向后兼容，提供工厂函数
def create_memory_manager(db_path: str = "memory/teaching_memory.db", 
                         use_agno: bool = None) -> Union[MemoryManager, AgnoMemoryManager]:
    """
    创建记忆管理器实例
    
    Args:
        db_path: 数据库路径
        use_agno: 是否使用agno实现，None表示使用环境变量设置
        
    Returns:
        记忆管理器实例
    """
    if use_agno is None:
        use_agno = USE_AGNO_MEMORY
    
    if use_agno:
        return AgnoMemoryManager(db_path)
    else:
        return MemoryManager(db_path)

def create_course_memory(memory_manager=None, 
                        use_agno: bool = None) -> Union[CourseMemory, AgnoCourseMemory]:
    """
    创建课程记忆实例
    
    Args:
        memory_manager: 记忆管理器实例，None表示自动创建
        use_agno: 是否使用agno实现，None表示使用环境变量设置
        
    Returns:
        课程记忆实例
    """
    if use_agno is None:
        use_agno = USE_AGNO_MEMORY
    
    if use_agno:
        return AgnoCourseMemory(memory_manager)
    else:
        return CourseMemory(memory_manager)

# 提供迁移功能
def migrate_to_agno(old_db_path: str = "memory/teaching_memory.db", 
                   new_db_path: str = "memory/teaching_memory.db"):
    """
    将数据从原始SQLite系统迁移到agno系统
    
    Args:
        old_db_path: 原数据库路径
        new_db_path: 新数据库基础路径
        
    Returns:
        迁移结果
    """
    migrator = MemoryMigrator(old_db_path, new_db_path)
    return migrator.migrate_all()

# 向后兼容的导出
__all__ = [
    # 原始实现
    "MemoryManager", 
    "CourseMemory",
    
    # Agno实现
    "AgnoMemoryManager",
    "AgnoCourseMemory", 
    
    # 动态选择的默认实现
    "DefaultMemoryManager",
    "DefaultCourseMemory",
    
    # 工厂函数
    "create_memory_manager",
    "create_course_memory",
    
    # 迁移工具
    "MemoryMigrator",
    "migrate_to_agno",
    
    # 配置
    "USE_AGNO_MEMORY"
] 