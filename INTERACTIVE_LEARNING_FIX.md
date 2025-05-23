# InteractiveLearning 页面修复说明

## 问题描述

在 InteractiveLearning.tsx 页面上的对话无法正确显示，后端报错：
```
AttributeError: 'NoneType' object has no attribute 'lower'
```

## 问题根因

1. **记忆管理器中的空值处理**：`memory_manager.py` 中的 `calculate_topic_relevance` 方法没有处理 `current_topic` 为 `None` 的情况
2. **学习主题未设置**：InteractiveLearning 页面没有向后端设置当前学习主题
3. **客户端ID不一致**：ChatContext 和 InteractiveLearning 页面使用了不同的客户端ID生成逻辑

## 修复方案

### 1. 后端修复

#### A. 修复 memory_manager.py 中的空值处理
```python
def calculate_topic_relevance(self, current_topic: str, user_message: str) -> float:
    # 检查current_topic是否为空或None
    if not current_topic or current_topic is None:
        logger.warning("current_topic is None or empty, returning default relevance score")
        return 1.0
    
    # 检查user_message是否为空或None
    if not user_message or user_message is None:
        logger.warning("user_message is None or empty, returning default relevance score")
        return 1.0
    
    # 使用try-catch包装核心逻辑
    try:
        topic_words = set(current_topic.lower().split())
        message_words = set(user_message.lower().split())
        # ... 其他逻辑
    except Exception as e:
        logger.error(f"Error calculating topic relevance: {e}")
        return 1.0  # 出错时返回默认相关性
```

#### B. 修复 teacher_agent.py 中的主题获取逻辑
```python
# 获取当前学习主题，确保不为None
current_topic = self.client_sessions[client_id].get("current_topic")
if not current_topic:
    current_topic = "一般学习"  # 设置默认主题
    self.client_sessions[client_id]["current_topic"] = current_topic
    logger.info(f"Set default topic for client {client_id}: {current_topic}")
```

#### C. 添加设置学习主题的API端点
```python
@router.post("/teaching/set-context")
async def set_teaching_context(request: dict):
    """设置教学上下文，包括学习主题"""
    client_id = request.get("client_id")
    topic = request.get("topic")
    session_id = request.get("session_id")
    
    if not client_id or not topic:
        raise HTTPException(status_code=400, detail="client_id and topic are required")
    
    context = {
        "topic": topic,
        "session_id": session_id or str(uuid.uuid4())
    }
    
    from src.agents.teaching_team.teacher_agent import teacher
    await teacher.set_teaching_context(client_id, context)
    
    return JSONResponse(content={"status": "success", "context": context})
```

### 2. 前端修复

#### A. 添加设置学习主题的API调用
```typescript
// src/services/api.ts
export const setTeachingContext = async (clientId: string, topic: string, sessionId?: string): Promise<any> => {
  try {
    const response = await fetch(`${API_URL}/teaching/set-context`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        client_id: clientId,
        topic: topic,
        session_id: sessionId 
      }),
    });
    
    return await checkResponse(response);
  } catch (error) {
    console.error('Error setting teaching context:', error);
    throw error;
  }
};
```

#### B. 修复 ChatContext 中的客户端ID管理
```typescript
// 生成或获取持久化的客户端ID
const getClientId = () => {
  let clientId = localStorage.getItem('client_id');
  if (!clientId) {
    clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('client_id', clientId);
  }
  return clientId;
};

// 在ChatProvider中使用
const [clientId] = useState<string>(getClientId());
```

#### C. 修改 InteractiveLearning 页面设置学习主题
```typescript
useEffect(() => {
  const initializeLearning = async () => {
    if (!initialPrompt || !clientId) return;

    try {
      // 1. 获取用户进度
      setIsLoadingProgress(true);
      const data = await getUserProgress();
      setUserProgress(data);

      // 2. 设置学习主题
      console.log('Setting teaching context:', { clientId, topic: initialPrompt });
      
      await setTeachingContext(clientId, initialPrompt);
      setIsContextSet(true);
      
      console.log('Teaching context set successfully');
      toast.success(`学习主题已设置为：${initialPrompt}`);

      // 3. 添加欢迎消息（如果还没有消息）
      if (messages.length === 0) {
        const welcomeMessage = `欢迎来到"${initialPrompt}"的互动学习！我是您的AI学习助手，可以帮助您回答问题、解释概念、提供练习题等。请问有什么我可以帮助您的？`;
        addMessage(welcomeMessage, 'agent');
      }

    } catch (error) {
      console.error('Error initializing learning:', error);
      toast.error('初始化学习环境失败，请重试');
    } finally {
      setIsLoadingProgress(false);
    }
  };

  initializeLearning();
}, [initialPrompt, clientId]);
```

## 修复效果

1. **错误消除**：不再出现 `AttributeError: 'NoneType' object has no attribute 'lower'` 错误
2. **主题设置**：InteractiveLearning 页面正确设置学习主题
3. **ID一致性**：确保前端和后端使用相同的客户端ID
4. **用户体验**：显示当前学习主题和设置状态

## 测试步骤

1. **启动服务**：
   ```bash
   # 前端
   npm run dev
   
   # 后端
   cd backend && python src/main.py
   ```

2. **测试流程**：
   - 访问首页，输入学习主题（如"Python编程基础"）
   - 跳转到课程规划页面，查看大纲
   - 点击"开始学习"进入互动学习页面
   - 观察页面左侧显示"✓ 主题已设置"
   - 在聊天框中输入消息，验证对话正常工作

3. **预期结果**：
   - 页面正确显示当前学习主题
   - 聊天功能正常工作，无后端错误
   - 浏览器控制台显示正确的WebSocket连接日志

## 技术改进

- **错误处理**：增强了空值和异常情况的处理
- **一致性**：统一了客户端ID的生成和使用逻辑
- **可观测性**：添加了详细的日志输出便于调试
- **用户体验**：增加了主题设置状态的可视化反馈

现在 InteractiveLearning 页面的对话功能应该可以正常工作了！ 