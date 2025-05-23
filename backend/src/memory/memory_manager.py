import logging
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryManager:
    """
    记忆管理器 - AI教学系统的核心记忆组件
    
    负责统一管理：
    1. 课程内容存储（课程大纲、章节内容）
    2. 学习进度跟踪
    3. 教学记录管理
    4. 记忆查询和检索
    """
    
    def __init__(self, db_path: str = "memory/teaching_memory.db"):
        """
        初始化记忆管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_memory_directory()
        self._init_database()
        logger.info(f"MemoryManager initialized with database: {db_path}")
    
    def _ensure_memory_directory(self):
        """确保记忆目录存在"""
        memory_dir = Path(self.db_path).parent
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录结构
        subdirs = ["courses/outlines", "courses/contents", "progress/sessions", 
                   "progress/achievements", "teaching/interactions", "teaching/topics"]
        
        for subdir in subdirs:
            (memory_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # 课程大纲表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS course_outlines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    learning_objectives TEXT, -- JSON格式
                    sections TEXT, -- JSON格式
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 章节内容表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS section_contents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    section_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT, -- JSON格式，包含详细内容
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES course_outlines (id)
                )
            """)
            
            # 学习进度表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    course_id INTEGER,
                    section_id TEXT,
                    progress_data TEXT, -- JSON格式
                    comprehension_score REAL DEFAULT 0,
                    interaction_count INTEGER DEFAULT 0,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES course_outlines (id)
                )
            """)
            
            # 教学记录表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS teaching_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    session_id TEXT,
                    topic TEXT,
                    interaction_type TEXT, -- 'question', 'answer', 'explanation', 'practice'
                    content TEXT,
                    response TEXT,
                    topic_relevance REAL DEFAULT 1.0, -- 主题相关性评分
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 主题跟踪表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS topic_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    session_id TEXT,
                    current_topic TEXT,
                    topic_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    topic_duration INTEGER DEFAULT 0, -- 秒
                    deviation_count INTEGER DEFAULT 0,
                    total_interactions INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database tables initialized successfully")
    
    # 课程内容存储方法
    def store_course_outline(self, topic: str, outline_data: Dict[str, Any]) -> int:
        """
        存储课程大纲
        
        Args:
            topic: 课程主题
            outline_data: 课程大纲数据
            
        Returns:
            course_id: 课程ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO course_outlines (topic, title, description, learning_objectives, sections)
                VALUES (?, ?, ?, ?, ?)
            """, (
                topic,
                outline_data.get('course_title', ''),
                outline_data.get('course_description', ''),
                json.dumps(outline_data.get('learning_objectives', [])),
                json.dumps(outline_data.get('sections', []))
            ))
            course_id = cursor.lastrowid
            conn.commit()
            
        logger.info(f"Course outline stored with ID: {course_id}")
        return course_id
    
    def store_section_content(self, course_id: int, section_id: str, 
                            title: str, content_data: Dict[str, Any]) -> int:
        """
        存储章节内容
        
        Args:
            course_id: 课程ID
            section_id: 章节ID
            title: 章节标题
            content_data: 章节内容数据
            
        Returns:
            content_id: 内容ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO section_contents (course_id, section_id, title, content)
                VALUES (?, ?, ?, ?)
            """, (
                course_id,
                section_id,
                title,
                json.dumps(content_data)
            ))
            content_id = cursor.lastrowid
            conn.commit()
            
        logger.info(f"Section content stored with ID: {content_id}")
        return content_id
    
    def get_course_outline(self, course_id: int) -> Optional[Dict[str, Any]]:
        """获取课程大纲"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM course_outlines WHERE id = ?
            """, (course_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'topic': row['topic'],
                    'course_title': row['title'],
                    'course_description': row['description'],
                    'learning_objectives': json.loads(row['learning_objectives']),
                    'sections': json.loads(row['sections']),
                    'created_at': row['created_at']
                }
        return None
    
    def get_section_content(self, section_id: str) -> Optional[Dict[str, Any]]:
        """获取章节内容"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM section_contents WHERE section_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (section_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'course_id': row['course_id'],
                    'section_id': row['section_id'],
                    'title': row['title'],
                    'content': json.loads(row['content']),
                    'created_at': row['created_at']
                }
        return None
    
    def search_courses_by_topic(self, topic_keywords: str) -> List[Dict[str, Any]]:
        """根据主题关键词搜索课程"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, topic, title, description, created_at
                FROM course_outlines 
                WHERE topic LIKE ? OR title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
            """, (f"%{topic_keywords}%", f"%{topic_keywords}%", f"%{topic_keywords}%"))
            
            # 映射字段名以保持一致性
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'topic': row['topic'],
                    'title': row['title'],  # 保持title用于向后兼容
                    'course_title': row['title'],  # 添加course_title以保持一致性
                    'description': row['description'],
                    'course_description': row['description'],  # 添加course_description以保持一致性
                    'created_at': row['created_at']
                })
            
            return results
    
    # 学习进度管理方法
    def update_learning_progress(self, client_id: str, course_id: int, 
                               section_id: str, progress_data: Dict[str, Any]):
        """更新学习进度"""
        with sqlite3.connect(self.db_path) as conn:
            # 检查是否已存在记录
            cursor = conn.execute("""
                SELECT id FROM learning_progress 
                WHERE client_id = ? AND course_id = ? AND section_id = ?
            """, (client_id, course_id, section_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                conn.execute("""
                    UPDATE learning_progress 
                    SET progress_data = ?, 
                        comprehension_score = ?,
                        interaction_count = interaction_count + 1,
                        last_activity = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    json.dumps(progress_data),
                    progress_data.get('comprehension_score', 0),
                    existing[0]
                ))
            else:
                # 创建新记录
                conn.execute("""
                    INSERT INTO learning_progress 
                    (client_id, course_id, section_id, progress_data, 
                     comprehension_score, interaction_count)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (
                    client_id, course_id, section_id,
                    json.dumps(progress_data),
                    progress_data.get('comprehension_score', 0)
                ))
            
            conn.commit()
    
    def get_learning_progress(self, client_id: str, 
                            course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取学习进度"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if course_id:
                cursor = conn.execute("""
                    SELECT * FROM learning_progress 
                    WHERE client_id = ? AND course_id = ?
                    ORDER BY last_activity DESC
                """, (client_id, course_id))
            else:
                cursor = conn.execute("""
                    SELECT * FROM learning_progress 
                    WHERE client_id = ?
                    ORDER BY last_activity DESC
                """, (client_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'course_id': row['course_id'],
                    'section_id': row['section_id'],
                    'progress_data': json.loads(row['progress_data']),
                    'comprehension_score': row['comprehension_score'],
                    'interaction_count': row['interaction_count'],
                    'last_activity': row['last_activity']
                })
            
            return results
    
    # 教学记录管理方法
    def record_teaching_interaction(self, client_id: str, session_id: str,
                                  topic: str, interaction_type: str,
                                  content: str, response: str,
                                  topic_relevance: float = 1.0):
        """记录教学互动"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO teaching_records 
                (client_id, session_id, topic, interaction_type, content, 
                 response, topic_relevance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (client_id, session_id, topic, interaction_type, 
                  content, response, topic_relevance))
            conn.commit()
    
    def get_teaching_history(self, client_id: str, 
                           session_id: Optional[str] = None,
                           limit: int = 10) -> List[Dict[str, Any]]:
        """获取教学历史记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if session_id:
                cursor = conn.execute("""
                    SELECT * FROM teaching_records 
                    WHERE client_id = ? AND session_id = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (client_id, session_id, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM teaching_records 
                    WHERE client_id = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (client_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # 主题控制方法
    def update_topic_tracking(self, client_id: str, session_id: str,
                            current_topic: str):
        """更新主题跟踪"""
        with sqlite3.connect(self.db_path) as conn:
            # 检查当前活跃的主题跟踪
            cursor = conn.execute("""
                SELECT id, topic_start_time FROM topic_tracking 
                WHERE client_id = ? AND session_id = ? 
                ORDER BY created_at DESC LIMIT 1
            """, (client_id, session_id))
            
            last_record = cursor.fetchone()
            
            if last_record:
                # 更新上一个主题的持续时间
                start_time = datetime.fromisoformat(last_record[1])
                duration = (datetime.now() - start_time).total_seconds()
                
                conn.execute("""
                    UPDATE topic_tracking 
                    SET topic_duration = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (duration, last_record[0]))
            
            # 创建新的主题跟踪记录
            conn.execute("""
                INSERT INTO topic_tracking 
                (client_id, session_id, current_topic)
                VALUES (?, ?, ?)
            """, (client_id, session_id, current_topic))
            
            conn.commit()
    
    def calculate_topic_relevance(self, current_topic: str, 
                                user_message: str) -> float:
        """
        计算用户消息与当前主题的相关性
        
        Args:
            current_topic: 当前学习主题
            user_message: 用户消息
            
        Returns:
            相关性评分 (0-1)
        """
        # 检查current_topic是否为空或None
        if not current_topic or current_topic is None:
            logger.warning("current_topic is None or empty, returning default relevance score")
            return 1.0
        
        # 检查user_message是否为空或None
        if not user_message or user_message is None:
            logger.warning("user_message is None or empty, returning default relevance score")
            return 1.0
        
        # 简单的关键词匹配方法
        # 实际应用中可以使用更复杂的语义相似度计算
        try:
            topic_words = set(current_topic.lower().split())
            message_words = set(user_message.lower().split())
            
            if not topic_words:
                return 1.0
            
            # 计算交集比例
            intersection = topic_words.intersection(message_words)
            relevance = len(intersection) / len(topic_words)
            
            # 确保最小相关性为0.1，避免过度严格
            return max(0.1, relevance)
        except Exception as e:
            logger.error(f"Error calculating topic relevance: {e}")
            return 1.0  # 出错时返回默认相关性
    
    def check_topic_deviation(self, client_id: str, session_id: str,
                            threshold: float = 0.3) -> bool:
        """
        检查是否偏离主题
        
        Args:
            client_id: 客户端ID
            session_id: 会话ID
            threshold: 偏离阈值
            
        Returns:
            是否偏离主题
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT AVG(topic_relevance) as avg_relevance,
                       COUNT(*) as interaction_count
                FROM teaching_records 
                WHERE client_id = ? AND session_id = ?
                AND created_at > datetime('now', '-10 minutes')
            """, (client_id, session_id))
            
            result = cursor.fetchone()
            
            if result and result[0] is not None and result[1] >= 3:
                avg_relevance = result[0]
                return avg_relevance < threshold
            
            return False
    
    # 记忆辅助方法
    def get_memory_summary(self, client_id: str) -> Dict[str, Any]:
        """获取记忆摘要"""
        with sqlite3.connect(self.db_path) as conn:
            # 获取学习统计
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT course_id) as course_count,
                       COUNT(DISTINCT section_id) as section_count,
                       AVG(comprehension_score) as avg_score,
                       SUM(interaction_count) as total_interactions
                FROM learning_progress 
                WHERE client_id = ?
            """, (client_id,))
            
            stats = cursor.fetchone()
            
            # 获取最近学习的主题
            cursor = conn.execute("""
                SELECT DISTINCT topic FROM teaching_records 
                WHERE client_id = ?
                ORDER BY created_at DESC LIMIT 5
            """, (client_id,))
            
            recent_topics = [row[0] for row in cursor.fetchall()]
            
            return {
                'course_count': stats[0] or 0,
                'section_count': stats[1] or 0,
                'average_score': stats[2] or 0,
                'total_interactions': stats[3] or 0,
                'recent_topics': recent_topics
            }
    
    def suggest_review_content(self, client_id: str) -> List[Dict[str, Any]]:
        """根据学习进度建议复习内容"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT lp.section_id, lp.comprehension_score, 
                       sc.title, sc.content,
                       lp.last_activity
                FROM learning_progress lp
                JOIN section_contents sc ON lp.section_id = sc.section_id
                WHERE lp.client_id = ? 
                AND lp.comprehension_score < 0.7
                ORDER BY lp.last_activity ASC
                LIMIT 3
            """, (client_id,))
            
            suggestions = []
            for row in cursor.fetchall():
                suggestions.append({
                    'section_id': row['section_id'],
                    'title': row['title'],
                    'comprehension_score': row['comprehension_score'],
                    'last_activity': row['last_activity']
                })
            
            return suggestions 