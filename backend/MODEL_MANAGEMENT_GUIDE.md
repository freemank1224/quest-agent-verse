# AI教学系统模型管理指南

## 🎯 概述

本指南介绍如何使用统一的模型配置管理系统，实现对AI教学系统中所有Agent模型的灵活管理。

### 核心特性

- **🔧 配置化管理** - 通过YAML配置文件统一管理所有模型
- **🏢 分Team管理** - 支持教学团队、学习团队、监控团队独立配置
- **🔄 动态切换** - 运行时无需重启即可切换模型
- **🛡️ 备用机制** - 自动故障转移到备用模型
- **⚡ 预设配置** - 一键应用高性能、经济模式等预设
- **🌍 环境管理** - 开发/测试/生产环境独立配置

## 📁 文件结构

```
backend/
├── config/
│   └── models.yaml              # 模型配置文件
├── src/
│   ├── utils/
│   │   └── model_manager.py     # 模型管理器
│   ├── agents/
│   │   └── teaching_team/
│   │       └── modern_teacher_agent.py  # 现代化Agent
│   └── api/
│       └── model_management.py  # 管理API
└── test_model_management.py     # 测试脚本
```

## 🔧 配置文件详解

### 基础配置结构

```yaml
# config/models.yaml

# 全局默认配置
global_defaults:
  default_provider: "ollama"
  default_model_code: "qwen3_32b"
  timeout: 30
  max_retries: 3

# 模型提供商配置
model_providers:
  # OpenAI配置
  openai:
    gpt4_turbo:
      provider: "openai"
      model_id: "gpt-4-turbo"
      description: "GPT-4 Turbo - 高性能通用模型"
      config:
        api_key: "${OPENAI_API_KEY}"
        temperature: 0.7
        max_tokens: 4096
        timeout: 30

  # xAI配置
  xai:
    grok_beta:
      provider: "xai"
      model_id: "grok-beta"
      description: "Grok Beta - xAI的主力模型"
      config:
        api_key: "${XAI_API_KEY}"
        base_url: "https://api.x.ai/v1"
        temperature: 0.7
        max_tokens: 4096

  # Google Gemini配置
  gemini:
    gemini_pro:
      provider: "gemini"
      model_id: "gemini-pro"
      description: "Gemini Pro - Google的高性能模型"
      config:
        api_key: "${GOOGLE_API_KEY}"
        temperature: 0.7
        max_tokens: 4096

  # Ollama本地模型配置
  ollama:
    qwen3_32b:
      provider: "ollama"
      model_id: "qwen3:32b"
      description: "Qwen3 32B - 高性能中文模型"
      config:
        host: "http://localhost:11434"
        timeout: 60
        keep_alive: "5m"

# Agent团队配置
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "qwen3_32b"
      fallback_models: ["gpt4_turbo", "gemini_pro"]
      specific_config:
        temperature: 0.7
        max_tokens: 2048
        enable_reasoning: true
        enable_memory: true

# 快速切换预设
presets:
  high_performance:
    teaching_team:
      teacher_agent: "gpt4_turbo"
      course_planner: "gpt4_turbo"
  
  cost_effective:
    teaching_team:
      teacher_agent: "qwen3_32b"
      course_planner: "qwen3_32b"
```

## 🚀 快速开始

### 1. 环境变量配置

```bash
# 设置API密钥
export OPENAI_API_KEY="your_openai_api_key"
export XAI_API_KEY="your_xai_api_key"
export GOOGLE_API_KEY="your_google_api_key"

# 设置运行环境
export ENVIRONMENT="development"  # development, testing, production
```

### 2. 基础使用

```python
from utils.model_manager import get_agent_model

# 获取教师Agent的模型（使用默认配置）
teacher_model = get_agent_model("teaching_team", "teacher_agent")

# 使用高性能预设
teacher_model = get_agent_model("teaching_team", "teacher_agent", "high_performance")
```

### 3. 创建现代化Agent

```python
from agents.teaching_team.modern_teacher_agent import ModernTeacherAgent

# 创建使用默认配置的教师Agent
teacher = ModernTeacherAgent()

# 创建使用高性能预设的教师Agent
teacher = ModernTeacherAgent(preset="high_performance")

# 创建使用经济模式的教师Agent
teacher = ModernTeacherAgent(preset="cost_effective")
```

## 🔄 模型切换操作

### 1. 通过代码切换

```python
from utils.model_manager import get_model_manager

manager = get_model_manager()

# 切换单个Agent的模型
manager.update_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")

# 应用预设配置到所有Agent
manager.apply_preset("high_performance")

# 获取当前模型信息
model_info = manager.get_agent_current_model("teaching_team", "teacher_agent")
print(f"当前模型: {model_info['model_code']}")
```

### 2. 通过配置文件切换

直接修改 `config/models.yaml` 文件：

```yaml
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "gpt4_turbo"  # 改为使用GPT-4
      fallback_models: ["gemini_pro", "qwen3_32b"]
```

然后重新加载配置：

```python
manager.reload_config()
```

### 3. 通过API切换

```bash
# 切换单个Agent模型
curl -X POST "http://localhost:8000/api/models/agent/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "teaching_team",
    "agent_name": "teacher_agent", 
    "model_code": "gpt4_turbo"
  }'

# 应用预设配置
curl -X POST "http://localhost:8000/api/models/preset/apply" \
  -H "Content-Type: application/json" \
  -d '{"preset_name": "high_performance"}'
```

## 📊 管理API接口

### 获取模型状态

```bash
# 获取所有模型状态
GET /api/models/status

# 获取可用模型列表
GET /api/models/available

# 获取特定Agent的模型信息
GET /api/models/agent/{team_name}/{agent_name}

# 健康检查
GET /api/models/health
```

### 模型管理操作

```bash
# 切换Agent模型
POST /api/models/agent/switch
{
  "team_name": "teaching_team",
  "agent_name": "teacher_agent",
  "model_code": "gpt4_turbo"
}

# 应用预设配置
POST /api/models/preset/apply
{
  "preset_name": "high_performance"
}

# 重新加载配置
POST /api/models/reload

# 清除模型缓存
DELETE /api/models/cache
```

## 🎛️ 预设配置

系统提供三种预设配置：

### 1. 高性能预设 (high_performance)
- 使用最先进的模型（GPT-4, Gemini 1.5 Pro等）
- 适合生产环境和重要任务
- 成本较高但效果最佳

### 2. 经济模式 (cost_effective)
- 平衡性能和成本
- 混合使用云服务和本地模型
- 适合日常开发和测试

### 3. 本地优先 (local_first)
- 优先使用本地Ollama模型
- 成本最低，隐私性最好
- 适合开发环境和离线场景

## 🔧 高级配置

### 1. 添加新的模型提供商

```yaml
model_providers:
  # 添加新的提供商
  anthropic:
    claude_3:
      provider: "anthropic"
      model_id: "claude-3-opus-20240229"
      description: "Claude 3 Opus - Anthropic的旗舰模型"
      config:
        api_key: "${ANTHROPIC_API_KEY}"
        temperature: 0.7
        max_tokens: 4096
```

### 2. 自定义Agent配置

```yaml
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "claude_3"
      fallback_models: ["gpt4_turbo", "gemini_pro"]
      specific_config:
        temperature: 0.8        # 更高的创造性
        max_tokens: 3072        # 自定义token限制
        enable_reasoning: true   # 启用推理工具
        custom_prompt: "你是一个专业的AI教师..."
```

### 3. 环境特定配置

```yaml
environments:
  development:
    default_provider: "ollama"
    log_level: "DEBUG"
    enable_fallback: true
    
  production:
    default_provider: "openai"
    log_level: "WARNING"
    enable_fallback: true
    rate_limit:
      requests_per_minute: 100
      burst_limit: 10
```

## 🧪 测试和验证

### 运行测试脚本

```bash
cd backend
python test_model_management.py
```

测试内容包括：
- 配置文件验证
- 模型管理器初始化
- 模型实例创建
- 动态切换功能
- 预设配置应用
- API接口测试

### 手动验证

```python
# 验证模型切换
from utils.model_manager import get_model_manager

manager = get_model_manager()

# 查看当前配置
status = manager.get_model_status()
print(f"环境: {status['environment']}")
print(f"可用提供商: {status['available_providers']}")

# 测试模型切换
original_model = manager.get_agent_current_model("teaching_team", "teacher_agent")
print(f"原始模型: {original_model['model_code']}")

# 切换到新模型
success = manager.update_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")
if success:
    new_model = manager.get_agent_current_model("teaching_team", "teacher_agent")
    print(f"新模型: {new_model['model_code']}")
```

## 🚨 故障排除

### 常见问题

1. **配置文件加载失败**
   ```
   错误: 配置文件不存在: config/models.yaml
   解决: 确保配置文件路径正确，或使用绝对路径
   ```

2. **API密钥未设置**
   ```
   错误: 创建 openai 模型实例失败
   解决: 设置环境变量 export OPENAI_API_KEY="your_key"
   ```

3. **Ollama连接失败**
   ```
   错误: 无法连接到 http://localhost:11434
   解决: 启动Ollama服务 ollama serve
   ```

4. **模型代号不存在**
   ```
   错误: 找不到模型配置: unknown_model
   解决: 检查配置文件中的模型代号是否正确
   ```

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查模型状态**
   ```python
   manager = get_model_manager()
   status = manager.get_model_status()
   print(json.dumps(status, indent=2, ensure_ascii=False))
   ```

3. **清除缓存重试**
   ```python
   manager.clear_cache()
   manager.reload_config()
   ```

## 📈 性能优化

### 1. 模型缓存
- 系统自动缓存已创建的模型实例
- 避免重复初始化提高性能
- 可手动清除缓存强制重新创建

### 2. 备用模型策略
- 配置多个备用模型确保可用性
- 按优先级自动故障转移
- 记录失败原因便于调试

### 3. 环境优化
- 开发环境使用本地模型降低延迟
- 生产环境使用云服务保证稳定性
- 测试环境禁用备用模型快速失败

## 🔮 未来扩展

### 计划功能

1. **模型性能监控**
   - 响应时间统计
   - 成功率监控
   - 成本追踪

2. **智能模型选择**
   - 基于任务类型自动选择最适合的模型
   - 负载均衡和动态调度
   - A/B测试支持

3. **配置热更新**
   - 无需重启的配置更新
   - 配置版本管理
   - 回滚机制

4. **Web管理界面**
   - 可视化配置管理
   - 实时状态监控
   - 操作日志记录

## 📞 支持

如有问题或建议，请：

1. 查看本指南的故障排除部分
2. 运行测试脚本验证配置
3. 检查日志文件获取详细错误信息
4. 提交Issue描述具体问题

---

**注意**: 请确保在生产环境中妥善保管API密钥，建议使用环境变量或密钥管理服务。 