# Agno Memory 系统迁移指南

本指南将帮助您将现有项目从原始SQLite memory系统迁移到基于Agno v2 Memory的新架构。

## 🎯 迁移目标

将当前的memory架构重构为agno内置的memory架构，同时保持功能完全一致。

## 📋 迁移前后对比

### 原始实现
```python
from memory.memory_manager import MemoryManager
from memory.course_memory import CourseMemory

# 直接使用SQLite实现
memory_manager = MemoryManager("memory/teaching_memory.db")
course_memory = CourseMemory(memory_manager)
```

### 新实现（推荐）
```python
from memory import create_memory_manager, create_course_memory

# 使用工厂函数，自动选择实现
memory_manager = create_memory_manager("memory/teaching_memory.db", use_agno=True)
course_memory = create_course_memory(memory_manager, use_agno=True)
```

## 🚀 快速开始

### 1. 启用Agno Memory系统

设置环境变量：
```bash
export USE_AGNO_MEMORY=true
```

或者在代码中明确指定：
```python
from memory import create_memory_manager
memory_manager = create_memory_manager(use_agno=True)
```

### 2. 基本使用示例

```python
from memory import create_memory_manager, create_course_memory

# 创建memory管理器（使用agno实现）
memory_manager = create_memory_manager(use_agno=True)

# 存储课程大纲
course_data = {
    'course_title': 'Python编程基础',
    'course_description': '学习Python编程的基础知识',
    'learning_objectives': ['掌握变量和数据类型', '理解控制流'],
    'sections': [
        {'id': 'section_1', 'title': '变量和数据类型'},
        {'id': 'section_2', 'title': '控制流程'}
    ]
}

course_id = memory_manager.store_course_outline('Python编程', course_data)
print(f"课程已存储，ID: {course_id}")

# 检索课程
course = memory_manager.get_course_outline(course_id)
print(f"检索到课程: {course['course_title']}")

# 搜索课程
results = memory_manager.search_courses_by_topic('Python')
print(f"找到 {len(results)} 个相关课程")
```

## 📊 数据迁移

### 自动迁移

如果您有现有的SQLite数据，可以使用内置的迁移工具：

```python
from memory import migrate_to_agno

# 执行数据迁移
results = migrate_to_agno(
    old_db_path="memory/teaching_memory.db",
    new_db_path="memory/teaching_memory.db"
)

print("迁移结果:", results)
```

### 手动迁移脚本

```python
#!/usr/bin/env python3
import os
from memory.migrate_to_agno import MemoryMigrator

def main():
    # 迁移数据
    migrator = MemoryMigrator(
        old_db_path="memory/teaching_memory.db",
        new_db_path="memory/teaching_memory.db"
    )
    
    # 执行迁移
    print("开始数据迁移...")
    results = migrator.migrate_all()
    print(f"迁移完成: {results}")
    
    # 验证迁移
    print("验证迁移结果...")
    validation = migrator.validate_migration()
    print(f"验证结果: {validation}")
    
    if validation['validation_passed']:
        print("✅ 数据迁移成功！")
    else:
        print("❌ 数据迁移存在问题:", validation['issues'])

if __name__ == "__main__":
    main()
```

## 🔄 代码迁移步骤

### 步骤1: 更新导入语句

**原来：**
```python
from memory.memory_manager import MemoryManager
from memory.course_memory import CourseMemory
```

**现在：**
```python
from memory import create_memory_manager, create_course_memory
# 或者直接使用新实现
from memory import AgnoMemoryManager, AgnoCourseMemory
```

### 步骤2: 更新初始化代码

**原来：**
```python
memory_manager = MemoryManager("memory/teaching_memory.db")
course_memory = CourseMemory(memory_manager)
```

**现在：**
```python
memory_manager = create_memory_manager("memory/teaching_memory.db", use_agno=True)
course_memory = create_course_memory(memory_manager, use_agno=True)
```

### 步骤3: 验证功能

所有原有的API调用保持不变：

```python
# 这些调用在新系统中完全一样
course_id = memory_manager.store_course_outline(topic, data)
course = memory_manager.get_course_outline(course_id)
progress = memory_manager.get_learning_progress(client_id)
# ... 等等
```

## 🏗️ 架构对比

### 数据存储映射

| 原始SQLite表 | Agno Memory映射 | 说明 |
|-------------|----------------|------|
| course_outlines | User Memories | 课程大纲存储为系统用户记忆 |
| section_contents | User Memories | 章节内容存储为系统用户记忆 |
| learning_progress | Session State + User Memories | 学习进度存储在会话状态和用户记忆中 |
| teaching_records | Session State + User Memories | 教学记录存储在会话状态和用户记忆中 |
| topic_tracking | Session State | 主题跟踪存储在会话状态中 |

### 新特性优势

1. **结构化存储**: 使用agno的UserMemory schema，更好的数据组织
2. **语义搜索**: 利用agno的搜索能力，更智能的内容检索
3. **会话管理**: 更好的会话状态管理和摘要生成
4. **扩展性**: 可以轻松扩展到PostgreSQL等其他数据库
5. **标准化**: 遵循agno的memory最佳实践

## 🧪 测试验证

运行测试脚本验证迁移：

```bash
cd backend
python test_agno_memory.py
```

预期输出：
```
🚀 开始Agno Memory系统测试
=== 测试AgnoMemoryManager ===
...
🎉 所有测试通过！
```

## 🔧 故障排除

### 常见问题

1. **导入错误**
   ```
   ModuleNotFoundError: No module named 'agno'
   ```
   **解决方案**: 确认agno已安装：`pip install agno==1.5.3`

2. **数据库权限错误**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **解决方案**: 检查数据库文件权限，确保应用有读写权限

3. **内存数据不一致**
   **解决方案**: 运行数据验证：
   ```python
   from memory.migrate_to_agno import MemoryMigrator
   migrator = MemoryMigrator()
   validation = migrator.validate_migration()
   ```

### 调试技巧

1. **启用详细日志**：
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查数据库内容**：
   ```python
   from memory import create_memory_manager
   memory = create_memory_manager(use_agno=True)
   
   # 查看用户记忆
   memories = memory.memory.get_user_memories(user_id="system")
   print(f"系统记忆数量: {len(memories)}")
   ```

3. **比较新旧实现**：
   ```python
   # 创建两个实例进行对比
   old_memory = create_memory_manager(use_agno=False)
   new_memory = create_memory_manager(use_agno=True)
   
   # 执行相同操作并比较结果
   ```

## 📈 性能优化

### 配置建议

1. **数据库优化**：
   ```python
   # 使用PostgreSQL获得更好性能（生产环境）
   from agno.memory.v2.db.postgres import PostgresMemoryDb
   db = PostgresMemoryDb(db_url="postgresql://user:pass@localhost/db")
   ```

2. **批量操作**：
   ```python
   # 批量存储课程内容
   for section in sections:
       memory_manager.store_section_content(course_id, section['id'], 
                                           section['title'], section['content'])
   ```

3. **缓存策略**：
   ```python
   # 缓存频繁访问的数据
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_cached_course(course_id):
       return memory_manager.get_course_outline(course_id)
   ```

## 🚦 生产部署

### 部署检查清单

- [ ] 数据迁移完成并验证
- [ ] 设置正确的环境变量
- [ ] 数据库权限配置正确
- [ ] 备份原始数据
- [ ] 性能测试通过
- [ ] 监控和日志配置完成

### 环境变量

```bash
# 启用agno memory
export USE_AGNO_MEMORY=true

# 数据库配置（如果使用PostgreSQL）
export AGNO_DB_URL="postgresql://user:pass@localhost/agno_memory"

# 日志级别
export LOG_LEVEL=INFO
```

## 📚 更多资源

- [Agno官方文档](https://deepwiki.com/agno-agi/agno/2.3-memory-system)
- [Agno Memory v2架构](https://deepwiki.com/agno-agi/agno/2.3-memory-system)
- [项目原始memory实现](./src/memory/memory_manager.py)
- [新agno实现](./src/memory/agno_memory_manager.py)

## 🤝 支持

如果在迁移过程中遇到问题，请：

1. 查看测试脚本：`test_agno_memory.py`
2. 检查日志输出
3. 运行验证脚本确认数据一致性
4. 参考上述故障排除指南

迁移成功后，您将享受到agno现代化memory架构带来的所有优势！🎉 