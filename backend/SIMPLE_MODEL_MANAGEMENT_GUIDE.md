# AI教学系统简化版模型管理指南

## 🎯 概述

这是一个简化的模型配置管理系统，专注于提供细粒度的Agent配置，让您可以轻松管理每个Agent使用的模型。

### 核心特性

- **🔧 简单配置** - 通过YAML配置文件直接管理每个Agent的模型
- **🤖 细粒度管理** - 每个Agent可以独立配置使用不同的模型
- **🔄 动态切换** - 运行时无需重启即可切换模型
- **🌐 多提供商支持** - 支持OpenAI、xAI、Gemini、Ollama四大提供商

## 📁 文件结构

```
backend/
├── config/
│   └── models.yaml              # 简化的模型配置文件
├── src/
│   ├── utils/
│   │   └── model_manager.py     # 简化的模型管理器
│   ├── agents/
│   │   └── teaching_team/
│   │       └── modern_teacher_agent.py  # 现代化Agent
│   └── api/
│       └── model_management.py  # 简化的管理API
```

## 🔧 配置文件

### 简化的配置结构

```yaml
# config/models.yaml

# 全局默认配置
global_defaults:
  default_provider: "ollama"
  default_model_code: "qwen3_32b"
  timeout: 30

# 模型提供商配置
model_providers:
  openai:
    gpt4_turbo:
      provider: "openai"
      model_id: "gpt-4-turbo"
      description: "GPT-4 Turbo - 高性能通用模型"
      config:
        api_key: "${OPENAI_API_KEY}"
        temperature: 0.7
        max_tokens: 4096
  
  ollama:
    qwen3_32b:
      provider: "ollama"
      model_id: "qwen3:32b"
      description: "Qwen3 32B - 高性能中文模型"
      config:
        host: "http://localhost:11434"
        timeout: 60

# Agent团队配置 - 细粒度配置
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "qwen3_32b"
    
    course_planner:
      model_code: "grok_beta"
    
    content_designer:
      model_code: "gemini_pro"
```

## 🚀 使用方式

### 1. 环境变量配置

```bash
# 设置API密钥
export OPENAI_API_KEY="your_openai_api_key"
export XAI_API_KEY="your_xai_api_key"
export GOOGLE_API_KEY="your_google_api_key"
```

### 2. 基础使用

```python
from utils.model_manager import get_agent_model

# 获取教师Agent的模型
teacher_model = get_agent_model("teaching_team", "teacher_agent")

# 获取课程规划Agent的模型
planner_model = get_agent_model("teaching_team", "course_planner")
```

### 3. 创建Agent

```python
from agents.teaching_team.modern_teacher_agent import ModernTeacherAgent

# 创建教师Agent（会自动使用配置文件中的模型）
teacher = ModernTeacherAgent()
```

## 🔄 模型切换

### 方式1: 修改配置文件

直接编辑 `config/models.yaml` 文件：

```yaml
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "gpt4_turbo"  # 改为使用GPT-4
```

### 方式2: 通过代码切换

```python
from utils.model_manager import get_model_manager

manager = get_model_manager()

# 切换教师Agent的模型
manager.update_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")
```

### 方式3: 通过API切换

```bash
curl -X POST "http://localhost:8000/api/models/agent/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "teaching_team",
    "agent_name": "teacher_agent", 
    "model_code": "gpt4_turbo"
  }'
```

## 📊 API接口

### 基础查询

```bash
# 获取所有可用模型
GET /api/models/available

# 获取模型状态
GET /api/models/status

# 获取特定Agent的模型
GET /api/models/agent/{team_name}/{agent_name}

# 获取所有团队和Agent
GET /api/models/teams
```

### 管理操作

```bash
# 切换Agent模型
POST /api/models/agent/switch
{
  "team_name": "teaching_team",
  "agent_name": "teacher_agent",
  "model_code": "gpt4_turbo"
}

# 批量切换模型
POST /api/models/batch/switch
[
  {
    "team_name": "teaching_team",
    "agent_name": "teacher_agent",
    "model_code": "gpt4_turbo"
  },
  {
    "team_name": "teaching_team",
    "agent_name": "course_planner",
    "model_code": "gemini_pro"
  }
]

# 重新加载配置
POST /api/models/reload

# 清除缓存
DELETE /api/models/cache
```

## 🎛️ 支持的模型

### OpenAI
- `gpt4_turbo` - GPT-4 Turbo
- `gpt4o` - GPT-4o
- `gpt35_turbo` - GPT-3.5 Turbo

### xAI
- `grok_beta` - Grok Beta
- `grok_vision` - Grok Vision

### Gemini
- `gemini_pro` - Gemini Pro
- `gemini_pro_vision` - Gemini Pro Vision
- `gemini_15_pro` - Gemini 1.5 Pro

### Ollama
- `qwen3_32b` - Qwen3 32B
- `qwen3_14b` - Qwen3 14B
- `llama3_8b` - Llama3 8B
- `codellama_13b` - CodeLlama 13B

## 📝 快速配置示例

### 全部使用本地模型
```yaml
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "qwen3_32b"
    course_planner:
      model_code: "qwen3_14b"
    content_designer:
      model_code: "llama3_8b"
```

### 全部使用GPT-4
```yaml
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "gpt4_turbo"
    course_planner:
      model_code: "gpt4_turbo"
    content_designer:
      model_code: "gpt4_turbo"
```

### 混合使用不同提供商
```yaml
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "gpt4_turbo"      # OpenAI
    course_planner:
      model_code: "grok_beta"       # xAI
    content_designer:
      model_code: "gemini_pro"      # Google
    content_verifier:
      model_code: "qwen3_32b"       # Ollama
```

## 🧪 测试

```bash
# 测试配置是否正确
python -c "
import sys
sys.path.append('src')
from utils.model_manager import get_model_manager

manager = get_model_manager()
print(f'可用提供商: {list(manager.config[\"model_providers\"].keys())}')

teacher_info = manager.get_agent_current_model('teaching_team', 'teacher_agent')
print(f'教师Agent当前模型: {teacher_info[\"model_code\"]}')
"
```

## 🔧 添加新模型

1. 在 `model_providers` 部分添加新模型配置
2. 在 `agent_teams` 部分指定Agent使用新模型

```yaml
model_providers:
  # 添加新模型
  anthropic:
    claude_3:
      provider: "anthropic"
      model_id: "claude-3-opus"
      description: "Claude 3 Opus"
      config:
        api_key: "${ANTHROPIC_API_KEY}"

agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "claude_3"  # 使用新模型
```

## 🚨 常见问题

1. **配置文件加载失败**
   - 检查文件路径是否正确
   - 确保YAML语法正确

2. **API密钥错误**
   - 检查环境变量是否设置
   - 确认API密钥有效

3. **Ollama连接失败**
   - 确保Ollama服务已启动：`ollama serve`
   - 检查端口是否正确

4. **模型代号不存在**
   - 检查配置文件中是否定义了该模型代号
   - 确认拼写正确

## 📞 支持

这个简化版的模型管理系统专注于最核心的功能：
- ✅ 每个Agent独立配置模型
- ✅ 简单的模型切换
- ✅ 基础的API管理接口
- ✅ 多提供商支持

如果需要更复杂的功能，可以参考完整版的 `MODEL_MANAGEMENT_GUIDE.md`。

---

**这样够简单了吗？** 😊 