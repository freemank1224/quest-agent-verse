#!/usr/bin/env python3
"""
数据迁移工具：将现有SQLite memory数据迁移到Agno Memory系统

此工具用于将原有的MemoryManager SQLite数据库中的数据
迁移到新的AgnoMemoryManager系统中，确保数据一致性和完整性。
"""

import logging
import sqlite3
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from .memory_manager import MemoryManager
from .agno_memory_manager import AgnoMemoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryMigrator:
    """
    记忆数据迁移工具
    
    负责将原有SQLite数据库中的数据迁移到新的Agno Memory系统
    """
    
    def __init__(self, old_db_path: str = "memory/teaching_memory.db", 
                 new_db_path: str = "memory/teaching_memory.db"):
        """
        初始化迁移工具
        
        Args:
            old_db_path: 原有数据库路径
            new_db_path: 新数据库基础路径
        """
        self.old_db_path = old_db_path
        self.new_db_path = new_db_path
        
        # 检查原数据库是否存在
        if not Path(old_db_path).exists():
            raise FileNotFoundError(f"原数据库文件不存在: {old_db_path}")
        
        self.old_memory = MemoryManager(old_db_path)
        self.new_memory = AgnoMemoryManager(new_db_path)
        
        logger.info(f"Migration initialized: {old_db_path} -> {new_db_path}")
    
    def migrate_all(self) -> Dict[str, Any]:
        """
        执行完整的数据迁移
        
        Returns:
            迁移结果统计
        """
        logger.info("开始完整数据迁移...")
        
        results = {
            'courses_migrated': 0,
            'sections_migrated': 0,
            'progress_records_migrated': 0,
            'interaction_records_migrated': 0,
            'topic_tracking_migrated': 0,
            'errors': []
        }
        
        try:
            # 1. 迁移课程大纲
            logger.info("迁移课程大纲...")
            course_mapping = self._migrate_course_outlines()
            results['courses_migrated'] = len(course_mapping)
            
            # 2. 迁移章节内容
            logger.info("迁移章节内容...")
            section_count = self._migrate_section_contents(course_mapping)
            results['sections_migrated'] = section_count
            
            # 3. 迁移学习进度
            logger.info("迁移学习进度...")
            progress_count = self._migrate_learning_progress(course_mapping)
            results['progress_records_migrated'] = progress_count
            
            # 4. 迁移教学记录
            logger.info("迁移教学记录...")
            interaction_count = self._migrate_teaching_records()
            results['interaction_records_migrated'] = interaction_count
            
            # 5. 迁移主题跟踪
            logger.info("迁移主题跟踪...")
            topic_count = self._migrate_topic_tracking()
            results['topic_tracking_migrated'] = topic_count
            
            logger.info(f"数据迁移完成: {results}")
            
        except Exception as e:
            error_msg = f"迁移过程中发生错误: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def _migrate_course_outlines(self) -> Dict[int, int]:
        """
        迁移课程大纲
        
        Returns:
            旧课程ID到新课程ID的映射
        """
        course_mapping = {}
        
        try:
            # 从原数据库获取所有课程大纲
            with sqlite3.connect(self.old_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM course_outlines 
                    ORDER BY created_at ASC
                """)
                
                for row in cursor.fetchall():
                    try:
                        # 构建课程数据
                        outline_data = {
                            'course_title': row['title'],
                            'course_description': row['description'],
                            'learning_objectives': json.loads(row['learning_objectives'] or '[]'),
                            'sections': json.loads(row['sections'] or '[]'),
                        }
                        
                        # 存储到新系统
                        new_course_id = self.new_memory.store_course_outline(
                            topic=row['topic'],
                            outline_data=outline_data
                        )
                        
                        course_mapping[row['id']] = new_course_id
                        logger.info(f"迁移课程: {row['id']} -> {new_course_id}")
                        
                    except Exception as e:
                        logger.error(f"迁移课程 {row['id']} 失败: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"读取课程大纲失败: {e}")
        
        return course_mapping
    
    def _migrate_section_contents(self, course_mapping: Dict[int, int]) -> int:
        """
        迁移章节内容
        
        Args:
            course_mapping: 课程ID映射
            
        Returns:
            迁移的章节数量
        """
        migrated_count = 0
        
        try:
            with sqlite3.connect(self.old_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM section_contents 
                    ORDER BY created_at ASC
                """)
                
                for row in cursor.fetchall():
                    try:
                        # 获取新的课程ID
                        old_course_id = row['course_id']
                        new_course_id = course_mapping.get(old_course_id)
                        
                        if new_course_id is None:
                            logger.warning(f"找不到课程映射: {old_course_id}")
                            continue
                        
                        # 解析内容数据
                        content_data = json.loads(row['content'] or '{}')
                        
                        # 存储到新系统
                        self.new_memory.store_section_content(
                            course_id=new_course_id,
                            section_id=row['section_id'],
                            title=row['title'],
                            content_data=content_data
                        )
                        
                        migrated_count += 1
                        logger.info(f"迁移章节: {row['section_id']}")
                        
                    except Exception as e:
                        logger.error(f"迁移章节 {row['section_id']} 失败: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"读取章节内容失败: {e}")
        
        return migrated_count
    
    def _migrate_learning_progress(self, course_mapping: Dict[int, int]) -> int:
        """
        迁移学习进度
        
        Args:
            course_mapping: 课程ID映射
            
        Returns:
            迁移的进度记录数量
        """
        migrated_count = 0
        
        try:
            with sqlite3.connect(self.old_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM learning_progress 
                    ORDER BY created_at ASC
                """)
                
                for row in cursor.fetchall():
                    try:
                        # 获取新的课程ID
                        old_course_id = row['course_id']
                        new_course_id = course_mapping.get(old_course_id)
                        
                        if new_course_id is None:
                            logger.warning(f"找不到课程映射: {old_course_id}")
                            continue
                        
                        # 解析进度数据
                        progress_data = json.loads(row['progress_data'] or '{}')
                        progress_data['comprehension_score'] = row['comprehension_score']
                        
                        # 迁移到新系统
                        self.new_memory.update_learning_progress(
                            client_id=row['client_id'],
                            course_id=new_course_id,
                            section_id=row['section_id'],
                            progress_data=progress_data
                        )
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.error(f"迁移学习进度失败: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"读取学习进度失败: {e}")
        
        return migrated_count
    
    def _migrate_teaching_records(self) -> int:
        """
        迁移教学记录
        
        Returns:
            迁移的记录数量
        """
        migrated_count = 0
        
        try:
            with sqlite3.connect(self.old_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM teaching_records 
                    ORDER BY created_at ASC
                """)
                
                for row in cursor.fetchall():
                    try:
                        # 迁移教学记录
                        self.new_memory.record_teaching_interaction(
                            client_id=row['client_id'],
                            session_id=row['session_id'] or 'migrated_session',
                            topic=row['topic'] or '未知主题',
                            interaction_type=row['interaction_type'] or 'unknown',
                            content=row['content'] or '',
                            response=row['response'] or '',
                            topic_relevance=row['topic_relevance'] or 1.0
                        )
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.error(f"迁移教学记录失败: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"读取教学记录失败: {e}")
        
        return migrated_count
    
    def _migrate_topic_tracking(self) -> int:
        """
        迁移主题跟踪
        
        Returns:
            迁移的跟踪记录数量
        """
        migrated_count = 0
        
        try:
            with sqlite3.connect(self.old_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM topic_tracking 
                    ORDER BY created_at ASC
                """)
                
                for row in cursor.fetchall():
                    try:
                        # 迁移主题跟踪
                        if row['current_topic']:
                            self.new_memory.update_topic_tracking(
                                client_id=row['client_id'],
                                session_id=row['session_id'] or 'migrated_session',
                                current_topic=row['current_topic']
                            )
                            migrated_count += 1
                        
                    except Exception as e:
                        logger.error(f"迁移主题跟踪失败: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"读取主题跟踪失败: {e}")
        
        return migrated_count
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        验证迁移结果
        
        Returns:
            验证结果
        """
        logger.info("验证迁移结果...")
        
        validation_results = {
            'old_db_stats': self._get_old_db_stats(),
            'new_db_stats': self._get_new_db_stats(),
            'validation_passed': True,
            'issues': []
        }
        
        # 比较统计数据
        old_stats = validation_results['old_db_stats']
        new_stats = validation_results['new_db_stats']
        
        # 检查课程数量
        if old_stats['courses'] != new_stats['courses']:
            validation_results['validation_passed'] = False
            validation_results['issues'].append(
                f"课程数量不匹配: 原{old_stats['courses']}, 新{new_stats['courses']}"
            )
        
        # 检查章节数量
        if old_stats['sections'] != new_stats['sections']:
            validation_results['validation_passed'] = False
            validation_results['issues'].append(
                f"章节数量不匹配: 原{old_stats['sections']}, 新{new_stats['sections']}"
            )
        
        return validation_results
    
    def _get_old_db_stats(self) -> Dict[str, int]:
        """获取原数据库统计信息"""
        stats = {}
        
        try:
            with sqlite3.connect(self.old_db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM course_outlines")
                stats['courses'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM section_contents")
                stats['sections'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM learning_progress")
                stats['progress_records'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM teaching_records")
                stats['teaching_records'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM topic_tracking")
                stats['topic_tracking'] = cursor.fetchone()[0]
        
        except Exception as e:
            logger.error(f"获取原数据库统计失败: {e}")
            stats = {'error': str(e)}
        
        return stats
    
    def _get_new_db_stats(self) -> Dict[str, int]:
        """获取新数据库统计信息"""
        # 简化的统计，实际应该查询agno数据库
        # 这里使用近似方法
        stats = {
            'courses': 0,
            'sections': 0,
            'progress_records': 0,
            'teaching_records': 0,
            'topic_tracking': 0
        }
        
        try:
            # 从agno数据库获取统计（简化实现）
            agno_db_path = self.new_db_path.replace('.db', '_agno.db')
            if Path(agno_db_path).exists():
                with sqlite3.connect(agno_db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM memories")
                    total_memories = cursor.fetchone()[0]
                    
                    # 估算各类型数量（简化）
                    stats['courses'] = total_memories // 4  # 假设1/4是课程相关
                    stats['sections'] = total_memories // 4
                    
        except Exception as e:
            logger.error(f"获取新数据库统计失败: {e}")
            stats['error'] = str(e)
        
        return stats


def main():
    """主函数 - 执行迁移"""
    import sys
    
    old_db_path = sys.argv[1] if len(sys.argv) > 1 else "memory/teaching_memory.db"
    new_db_path = sys.argv[2] if len(sys.argv) > 2 else "memory/teaching_memory.db"
    
    try:
        migrator = MemoryMigrator(old_db_path, new_db_path)
        
        # 执行迁移
        results = migrator.migrate_all()
        print(f"迁移完成: {results}")
        
        # 验证迁移
        validation = migrator.validate_migration()
        print(f"验证结果: {validation}")
        
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 