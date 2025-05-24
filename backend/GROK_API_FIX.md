# xAI (Grok) API 修复指南

## 问题说明

项目中使用的xAI (Grok) API密钥已被封禁，导致系统报错:

```
ERROR: API key is currently blocked: Blocked due to API key leak
```

## 解决方案

本次修复通过以下步骤解决了API密钥被封禁的问题:

1. 将 `CoursePlannerAgent` 默认使用的模型从 "grok" 更改为 "qwen3_32b"
2. 在模型配置文件 `models.yaml` 中，将 `content_verifier` 从 "grok" 改为 "qwen3_32b"
3. 在模型管理器 `model_manager.py` 中增加了检测xAI API封禁的逻辑，并自动切换至备用模型
4. 优化了错误处理和日志，确保在API密钥问题时给出明确的错误信息

## 具体修改

1. `/src/agents/teaching_team/course_planner.py`:
   - 修改初始化函数，默认使用qwen3_32b模型

2. `/config/models.yaml`:
   - 将content_verifier的model_code从"grok"修改为"qwen3_32b"

3. `/src/utils/model_manager.py`:
   - 增加xAI API封禁检测和自动切换至备用模型的逻辑
   - 优化错误处理，提供更明确的错误信息
   - 对使用grok模型的配置自动切换到备用模型

## 维护建议

1. **移除对xAI API的依赖**:
   - 暂时停止使用所有xAI (Grok) API相关功能
   - 不要在新功能中使用xAI的API

2. **使用替代模型**:
   - 对于需要高性能的场景，优先使用Ollama的qwen3_32b模型
   - 对于较小规模任务，可以使用qwen3_14b或llama3_8b
   - 如果需要在线服务，考虑使用OpenAI的GPT-4o或Gemini

3. **更新API密钥管理**:
   - 确保所有API密钥妥善保存，避免再次泄露
   - 考虑使用环境变量或专用密钥管理系统管理API密钥

## 长期解决方案

1. 完全移除对xAI (Grok) API的依赖，使用其他可靠的替代品
2. 构建更健壮的模型回退机制，确保单一API故障不会影响整个系统
3. 完善API密钥轮换和监控机制，及时发现和处理API问题
