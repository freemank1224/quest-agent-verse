# WebSocket 聊天功能调试指南

## 问题描述
InteractiveLearning页面中用户发送消息后无法接收到Agent回复。

## 调试步骤

### 1. 确认后端服务运行
确保后端服务已启动并且正常工作：
```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 使用WebSocket调试器
1. 访问 `http://localhost:3000/websocket-debug` (前端调试页面)
2. 或者在InteractiveLearning页面点击"打开WebSocket调试器"链接

### 3. 观察调试结果

#### 正常情况下应该看到：
- ✅ 状态显示为"CONNECTED"
- ✅ 日志中显示"WebSocket连接成功建立!"
- ✅ 日志中显示"发送测试消息"
- ✅ 日志中显示"收到回复"以及完整的回复JSON数据

#### 异常情况及解决方案：

**连接失败 (状态显示ERROR)**
- 检查后端服务是否运行在8000端口
- 检查防火墙设置
- 确认WebSocket URL配置正确

**连接成功但无回复**
- 检查后端日志是否有错误信息
- 确认Ollama服务是否正常运行
- 检查模型是否正确加载

**回复格式错误**
- 检查Agent返回的数据格式
- 确认JSON解析是否正确

### 4. 环境变量检查
调试器会显示以下环境变量：
- `VITE_API_URL`: 默认为 `http://localhost:8000/api`
- `VITE_WS_URL`: 默认为 `ws://localhost:8000/api`

如果前端运行在不同端口或域名，需要创建`.env`文件配置正确的URL。

### 5. 手动测试
在调试器中可以：
1. 输入自定义测试消息
2. 通过ChatContext发送消息
3. 观察完整的消息收发过程

## 已知问题和解决方案

### 后端已验证正常工作
通过`backend/test_websocket_chat.py`测试确认：
- ✅ WebSocket连接正常
- ✅ 消息处理正常  
- ✅ Agent回复正常
- ✅ 超时问题已修复(设置了600秒超时)

### 可能的前端问题
1. **环境变量配置错误**
2. **WebSocket连接时机问题**
3. **消息处理逻辑异常**
4. **组件生命周期导致连接中断**

### 解决方案
1. 使用调试器确认具体问题点
2. 检查浏览器开发者工具的Network面板
3. 查看Console中的WebSocket相关日志
4. 对比正常工作的后端测试和前端实现的差异

## 调试完成后
问题解决后，可以：
1. 移除调试链接
2. 删除调试相关文件
3. 确认正常聊天功能工作

## 联系信息
如果调试器显示连接正常但InteractiveLearning页面仍有问题，请提供：
1. 调试器的完整日志
2. 浏览器开发者工具的截图
3. 具体的错误描述 