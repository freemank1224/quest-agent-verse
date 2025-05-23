import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from pathlib import Path
import uuid

from agno.memory.v2 import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.schema import UserMemory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgnoMemoryManager:
    """
    基于Agno v2 Memory系统的记忆管理器适配器
    
    提供与原MemoryManager完全兼容的API接口，但使用agno内置的现代memory架构
    负责统一管理：
    1. 课程内容存储（课程大纲、章节内容）- 映射到User Memories
    2. 学习进度跟踪 - 映射到Session State + User Memories
    3. 教学记录管理 - 映射到Session Summaries + User Memories
    4. 主题跟踪 - 映射到Session State
    """
    
    def __init__(self, db_path: str = "memory/teaching_memory.db"):
        """
        初始化agno记忆管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_memory_directory()
        
        # 初始化agno memory系统
        agno_db_path = db_path.replace('.db', '_agno.db')
        self.db = SqliteMemoryDb(db_file=agno_db_path, table_name="memories")
        self.memory = Memory(db=self.db)
        
        # 内部计数器和映射
        self._course_counter = self._load_course_counter()
        self._section_mapping = self._load_section_mapping()
        
        logger.info(f"AgnoMemoryManager initialized with database: {agno_db_path}")
    
    def _ensure_memory_directory(self):
        """确保记忆目录存在"""
        memory_dir = Path(self.db_path).parent
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录结构
        subdirs = ["courses/outlines", "courses/contents", "progress/sessions", 
                   "progress/achievements", "teaching/interactions", "teaching/topics"]
        
        for subdir in subdirs:
            (memory_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def _load_course_counter(self) -> int:
        """加载课程计数器"""
        counter_file = Path(self.db_path).parent / "course_counter.txt"
        if counter_file.exists():
            try:
                return int(counter_file.read_text().strip())
            except:
                pass
        return 1
    
    def _save_course_counter(self):
        """保存课程计数器"""
        counter_file = Path(self.db_path).parent / "course_counter.txt"
        counter_file.write_text(str(self._course_counter))
    
    def _load_section_mapping(self) -> Dict[str, int]:
        """加载章节映射"""
        mapping_file = Path(self.db_path).parent / "section_mapping.json"
        if mapping_file.exists():
            try:
                return json.loads(mapping_file.read_text())
            except:
                pass
        return {}
    
    def _save_section_mapping(self):
        """保存章节映射"""
        mapping_file = Path(self.db_path).parent / "section_mapping.json"
        mapping_file.write_text(json.dumps(self._section_mapping))
    
    # 课程内容存储方法
    def store_course_outline(self, topic: str, outline_data: Dict[str, Any]) -> int:
        """
        存储课程大纲到agno user memories
        
        Args:
            topic: 课程主题
            outline_data: 课程大纲数据
            
        Returns:
            course_id: 课程ID
        """
        course_id = self._course_counter
        self._course_counter += 1
        
        # 构造memory数据
        memory_data = {
            'course_id': course_id,
            'topic': topic,
            'course_title': outline_data.get('course_title', ''),
            'course_description': outline_data.get('course_description', ''),
            'learning_objectives': outline_data.get('learning_objectives', []),
            'sections': outline_data.get('sections', []),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 创建UserMemory对象
        user_memory = UserMemory(
            memory=f"课程大纲: {outline_data.get('course_title', topic)}",
            topics=["course_outline", topic, str(course_id)],
            input=json.dumps(memory_data)
        )
        
        # 添加到agno memory
        self.memory.add_user_memory(
            memory=user_memory,
            user_id="system"
        )
        
        self._save_course_counter()
        logger.info(f"Course outline stored with ID: {course_id}")
        return course_id
    
    def store_section_content(self, course_id: int, section_id: str, 
                            title: str, content_data: Dict[str, Any]) -> int:
        """
        存储章节内容到agno user memories
        
        Args:
            course_id: 课程ID
            section_id: 章节ID
            title: 章节标题
            content_data: 章节内容数据
            
        Returns:
            content_id: 内容ID
        """
        content_id = len(self._section_mapping) + 1
        self._section_mapping[section_id] = content_id
        
        # 构造section数据
        section_data = {
            'content_id': content_id,
            'course_id': course_id,
            'section_id': section_id,
            'title': title,
            'content': content_data,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 创建UserMemory对象
        user_memory = UserMemory(
            memory=f"章节内容: {title}",
            topics=["section_content", section_id, str(course_id)],
            input=json.dumps(section_data)
        )
        
        # 添加到agno memory
        self.memory.add_user_memory(
            memory=user_memory,
            user_id="system"
        )
        
        self._save_section_mapping()
        logger.info(f"Section content stored with ID: {content_id}")
        return content_id
    
    def get_course_outline(self, course_id: int) -> Optional[Dict[str, Any]]:
        """从agno memories获取课程大纲"""
        try:
            # 搜索相关memories
            memories = self.memory.search_user_memories(
                user_id="system",
                query=f"course_id:{course_id}",
                limit=10
            )
            
            for memory in memories:
                if memory.topics and "course_outline" in memory.topics and str(course_id) in memory.topics:
                    try:
                        data = json.loads(memory.input or '{}')
                        if data.get('course_id') == course_id:
                            return {
                                'id': data['course_id'],
                                'topic': data['topic'],
                                'course_title': data['course_title'],
                                'course_description': data['course_description'],
                                'learning_objectives': data['learning_objectives'],
                                'sections': data['sections'],
                                'created_at': data['created_at']
                            }
                    except json.JSONDecodeError:
                        continue
            
            return None
        except Exception as e:
            logger.error(f"Error getting course outline: {e}")
            return None
    
    def get_section_content(self, section_id: str) -> Optional[Dict[str, Any]]:
        """从agno memories获取章节内容"""
        try:
            # 搜索相关memories
            memories = self.memory.search_user_memories(
                user_id="system",
                query=section_id,
                limit=10
            )
            
            for memory in memories:
                if memory.topics and "section_content" in memory.topics and section_id in memory.topics:
                    try:
                        data = json.loads(memory.input or '{}')
                        if data.get('section_id') == section_id:
                            return {
                                'id': data['content_id'],
                                'course_id': data['course_id'],
                                'section_id': data['section_id'],
                                'title': data['title'],
                                'content': data['content'],
                                'created_at': data['created_at']
                            }
                    except json.JSONDecodeError:
                        continue
            
            return None
        except Exception as e:
            logger.error(f"Error getting section content: {e}")
            return None
    
    def search_courses_by_topic(self, topic_keywords: str) -> List[Dict[str, Any]]:
        """根据主题关键词搜索课程"""
        try:
            # 搜索相关的课程大纲memories
            memories = self.memory.search_user_memories(
                user_id="system",
                query=topic_keywords,
                limit=20
            )
            
            results = []
            seen_courses = set()
            
            for memory in memories:
                if memory.topics and "course_outline" in memory.topics:
                    try:
                        data = json.loads(memory.input or '{}')
                        course_id = data.get('course_id')
                        
                        if course_id not in seen_courses:
                            results.append({
                                'id': course_id,
                                'topic': data.get('topic', ''),
                                'title': data.get('course_title', ''),
                                'course_title': data.get('course_title', ''),
                                'description': data.get('course_description', ''),
                                'course_description': data.get('course_description', ''),
                                'created_at': data.get('created_at', '')
                            })
                            seen_courses.add(course_id)
                    except json.JSONDecodeError:
                        continue
            
            return results
        except Exception as e:
            logger.error(f"Error searching courses: {e}")
            return []
    
    # 学习进度管理方法 - 使用session state和user memories
    def update_learning_progress(self, client_id: str, course_id: int, 
                               section_id: str, progress_data: Dict[str, Any]):
        """更新学习进度到session state和user memories"""
        try:
            # 获取或创建session state
            session_state = self._get_session_state(client_id) or {}
            
            # 更新进度数据
            progress_key = f"progress_{course_id}_{section_id}"
            session_state[progress_key] = {
                'course_id': course_id,
                'section_id': section_id,
                'progress_data': progress_data,
                'comprehension_score': progress_data.get('comprehension_score', 0),
                'interaction_count': session_state.get(progress_key, {}).get('interaction_count', 0) + 1,
                'last_activity': datetime.now().isoformat(),
                'created_at': session_state.get(progress_key, {}).get('created_at', datetime.now().isoformat())
            }
            
            # 保存session state
            self._save_session_state(client_id, session_state)
            
            # 同时创建长期记忆
            memory_string = f"学习进度: 课程{course_id}章节{section_id}理解度{progress_data.get('comprehension_score', 0)}"
            progress_memory = UserMemory(
                memory=memory_string,
                topics=["learning_progress", str(course_id), section_id],
                input=json.dumps(progress_data)
            )
            
            self.memory.add_user_memory(
                memory=progress_memory,
                user_id=client_id
            )
            
        except Exception as e:
            logger.error(f"Error updating learning progress: {e}")
    
    def get_learning_progress(self, client_id: str, 
                            course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取学习进度"""
        try:
            session_state = self._get_session_state(client_id) or {}
            results = []
            
            for key, value in session_state.items():
                if key.startswith("progress_"):
                    if course_id is None or value.get('course_id') == course_id:
                        results.append({
                            'id': len(results) + 1,
                            'course_id': value['course_id'],
                            'section_id': value['section_id'],
                            'progress_data': value['progress_data'],
                            'comprehension_score': value['comprehension_score'],
                            'interaction_count': value['interaction_count'],
                            'last_activity': value['last_activity']
                        })
            
            # 按最后活动时间排序
            results.sort(key=lambda x: x['last_activity'], reverse=True)
            return results
        except Exception as e:
            logger.error(f"Error getting learning progress: {e}")
            return []
    
    # 教学记录管理方法 - 使用session state和user memories
    def record_teaching_interaction(self, client_id: str, session_id: str,
                                  topic: str, interaction_type: str,
                                  content: str, response: str,
                                  topic_relevance: float = 1.0):
        """记录教学互动到session state和user memories"""
        try:
            # 获取或创建session state
            session_state = self._get_session_state(client_id) or {}
            
            # 添加交互记录到session state
            interactions_key = "teaching_interactions"
            if interactions_key not in session_state:
                session_state[interactions_key] = []
            
            interaction_record = {
                'session_id': session_id,
                'topic': topic,
                'interaction_type': interaction_type,
                'content': content,
                'response': response,
                'topic_relevance': topic_relevance,
                'created_at': datetime.now().isoformat()
            }
            
            session_state[interactions_key].append(interaction_record)
            
            # 保持最近100条记录
            if len(session_state[interactions_key]) > 100:
                session_state[interactions_key] = session_state[interactions_key][-100:]
            
            self._save_session_state(client_id, session_state)
            
            # 创建user memory记录重要交互
            if topic_relevance >= 0.7:  # 只记录相关性高的交互
                interaction_memory = UserMemory(
                    memory=f"教学交互: {interaction_type} - {content[:50]}...",
                    topics=["teaching_interaction", topic, interaction_type],
                    input=json.dumps(interaction_record)
                )
                
                self.memory.add_user_memory(
                    memory=interaction_memory,
                    user_id=client_id
                )
            
            # 每10次交互创建一次session summary
            if len(session_state[interactions_key]) % 10 == 0:
                self._create_session_summary(client_id, session_id, session_state[interactions_key][-10:])
            
        except Exception as e:
            logger.error(f"Error recording teaching interaction: {e}")
    
    def get_teaching_history(self, client_id: str, 
                           session_id: Optional[str] = None,
                           limit: int = 10) -> List[Dict[str, Any]]:
        """获取教学历史记录"""
        try:
            session_state = self._get_session_state(client_id) or {}
            interactions = session_state.get("teaching_interactions", [])
            
            # 过滤session_id
            if session_id:
                interactions = [i for i in interactions if i.get('session_id') == session_id]
            
            # 按时间倒序排列并限制数量
            interactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return interactions[:limit]
        except Exception as e:
            logger.error(f"Error getting teaching history: {e}")
            return []
    
    # 主题控制方法 - 使用session state
    def update_topic_tracking(self, client_id: str, session_id: str,
                            current_topic: str):
        """更新主题跟踪"""
        try:
            session_state = self._get_session_state(client_id) or {}
            
            # 更新当前主题
            previous_topic = session_state.get('current_topic')
            if previous_topic and previous_topic != current_topic:
                # 计算上一个主题的持续时间
                topic_start_time = session_state.get('topic_start_time')
                if topic_start_time:
                    start_time = datetime.fromisoformat(topic_start_time)
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    # 记录主题历史
                    if 'topic_history' not in session_state:
                        session_state['topic_history'] = []
                    
                    session_state['topic_history'].append({
                        'topic': previous_topic,
                        'start_time': topic_start_time,
                        'duration': duration,
                        'end_time': datetime.now().isoformat()
                    })
            
            # 设置新主题
            session_state['current_topic'] = current_topic
            session_state['topic_start_time'] = datetime.now().isoformat()
            session_state['session_id'] = session_id
            
            self._save_session_state(client_id, session_state)
        except Exception as e:
            logger.error(f"Error updating topic tracking: {e}")
    
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
        try:
            # 获取最近的教学记录
            recent_interactions = self.get_teaching_history(client_id, session_id, limit=5)
            
            if len(recent_interactions) < 3:
                return False
            
            # 计算平均相关性
            relevance_scores = [i.get('topic_relevance', 1.0) for i in recent_interactions]
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            
            return avg_relevance < threshold
        except Exception as e:
            logger.error(f"Error checking topic deviation: {e}")
            return False
    
    # 记忆辅助方法
    def get_memory_summary(self, client_id: str) -> Dict[str, Any]:
        """获取记忆摘要"""
        try:
            # 从session state获取统计信息
            session_state = self._get_session_state(client_id) or {}
            
            # 计算课程数量和章节数量
            course_count = 0
            section_count = 0
            total_interactions = 0
            score_sum = 0
            score_count = 0
            
            for key, value in session_state.items():
                if key.startswith("progress_"):
                    course_count += 1
                    section_count += 1
                    total_interactions += value.get('interaction_count', 0)
                    score = value.get('comprehension_score', 0)
                    if score > 0:
                        score_sum += score
                        score_count += 1
            
            avg_score = score_sum / score_count if score_count > 0 else 0
            
            # 获取最近的主题
            interactions = session_state.get("teaching_interactions", [])
            recent_topics = list(set([i.get('topic', '') for i in interactions[-5:]]))
            
            return {
                'course_count': course_count,
                'section_count': section_count,
                'average_score': avg_score,
                'total_interactions': total_interactions,
                'recent_topics': recent_topics
            }
        except Exception as e:
            logger.error(f"Error getting memory summary: {e}")
            return {
                'course_count': 0,
                'section_count': 0,
                'average_score': 0,
                'total_interactions': 0,
                'recent_topics': []
            }
    
    def suggest_review_content(self, client_id: str) -> List[Dict[str, Any]]:
        """根据学习进度建议复习内容"""
        try:
            progress_data = self.get_learning_progress(client_id)
            
            # 筛选理解度低的内容
            suggestions = []
            for progress in progress_data:
                if progress['comprehension_score'] < 0.7:
                    # 获取章节内容
                    section_content = self.get_section_content(progress['section_id'])
                    if section_content:
                        suggestions.append({
                            'section_id': progress['section_id'],
                            'title': section_content['title'],
                            'comprehension_score': progress['comprehension_score'],
                            'last_activity': progress['last_activity']
                        })
            
            # 按最后活动时间排序，返回最旧的3个
            suggestions.sort(key=lambda x: x['last_activity'])
            return suggestions[:3]
        except Exception as e:
            logger.error(f"Error suggesting review content: {e}")
            return []
    
    # 辅助方法
    def _get_session_state(self, client_id: str) -> Optional[Dict[str, Any]]:
        """获取session state"""
        try:
            # 从文件系统读取session state（简化实现）
            state_file = Path(self.db_path).parent / f"session_state_{client_id}.json"
            if state_file.exists():
                return json.loads(state_file.read_text())
            return None
        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            return None
    
    def _save_session_state(self, client_id: str, session_state: Dict[str, Any]):
        """保存session state"""
        try:
            state_file = Path(self.db_path).parent / f"session_state_{client_id}.json"
            state_file.write_text(json.dumps(session_state, indent=2))
        except Exception as e:
            logger.error(f"Error saving session state: {e}")
    
    def _create_session_summary(self, client_id: str, session_id: str, interactions: List[Dict[str, Any]]):
        """创建session summary"""
        try:
            # 构建摘要
            summary_data = {
                'session_id': session_id,
                'interaction_count': len(interactions),
                'topics_covered': list(set([i.get('topic', '') for i in interactions])),
                'avg_relevance': sum([i.get('topic_relevance', 1.0) for i in interactions]) / len(interactions),
                'created_at': datetime.now().isoformat()
            }
            
            # 创建user memory存储摘要
            summary_memory = UserMemory(
                memory=f"会话摘要: {session_id} - {len(interactions)}次交互",
                topics=["session_summary", session_id],
                input=json.dumps(summary_data)
            )
            
            self.memory.add_user_memory(
                memory=summary_memory,
                user_id=client_id
            )
        except Exception as e:
            logger.error(f"Error creating session summary: {e}") 