# 环境配置系统使用说明

## 概述

本系统参考 [agno 框架](https://deepwiki.com/agno-agi/agno) 的最佳实践，实现了统一的环境变量管理，支持多种AI模型提供商的API密钥配置。

## 特性

- ✅ **参考 agno 框架设计**: 统一的API密钥管理方式
- ✅ **支持多种提供商**: OpenAI、xAI、Gemini、Anthropic、Ollama
- ✅ **环境文件管理**: 使用 `.env` 文件存储敏感信息
- ✅ **自动验证**: 启动时检查配置完整性
- ✅ **安全性**: 自动过滤占位符，隐藏敏感信息
- ✅ **降级支持**: 部分配置缺失时仍可正常运行

## 快速开始

### 1. 环境配置

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，设置你的API密钥
vim .env
```

### 2. 环境变量设置

```bash
# OpenAI
OPENAI_API_KEY=sk-your_openai_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# xAI (Grok)
XAI_API_KEY=your_xai_key_here
XAI_BASE_URL=https://api.x.ai/v1

# Google Gemini
GOOGLE_API_KEY=your_google_key_here

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key_here

# Ollama (本地，无需API密钥)
OLLAMA_HOST=http://localhost:11434
```

### 3. 验证配置

```bash
# 运行测试脚本
python test_env_config.py

# 运行演示
python examples/env_config_demo.py
```

## 使用方式

### 基本用法

```python
from config.env_config import get_env_config, get_api_key
from utils.model_manager import get_agent_model, get_model_by_id

# 获取环境配置
env_config = get_env_config()

# 获取API密钥
openai_key = get_api_key("openai")

# 方式1: 使用默认配置的模型
teacher_model = get_agent_model("teaching_team", "teacher_agent")

# 方式2: 临时切换到指定模型 (不更改配置文件)
teacher_model_gpt = get_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")

# 方式3: 直接获取指定模型 (不绑定Agent)
qwen_model = get_model_by_id("qwen3_32b")
```

### agno 风格配置

```python
from config.env_config import validate_environment

# 验证环境配置
if validate_environment():
    print("✅ 环境配置完整")
else:
    print("⚠️ 部分配置缺失")
```

### 动态模型切换

```python
from utils.model_manager import get_model_manager, get_agent_model

# 三种模型使用方式对比

# 1. 使用默认配置
default_model = get_agent_model("teaching_team", "course_planner")

# 2. 临时指定模型 (推荐) - 不更改配置，灵活切换
temp_model = get_agent_model("teaching_team", "course_planner", "gpt4_turbo")

# 3. 永久更改默认配置
manager = get_model_manager()
manager.update_agent_model("teaching_team", "course_planner", "qwen3_14b")

# 查看当前配置
config = manager.get_agent_current_model("teaching_team", "course_planner")
print(f"当前模型: {config['model_code']}")
```

### 实际使用示例

```python
# 示例1: 在不同场景下使用不同模型
def handle_request(request_type, content):
    if request_type == "simple_qa":
        # 简单问答使用本地模型
        model = get_agent_model("teaching_team", "teacher_agent", "qwen3_14b")
    elif request_type == "complex_analysis":
        # 复杂分析使用高性能模型
        model = get_agent_model("teaching_team", "teacher_agent", "gpt4_turbo")
    else:
        # 其他情况使用默认配置
        model = get_agent_model("teaching_team", "teacher_agent")
    
    return model.generate(content)

# 示例2: 批量测试不同模型性能
def test_models_performance(prompt):
    models_to_test = ["qwen3_32b", "qwen3_14b", "gpt4_turbo", "grok_beta"]
    results = {}
    
    for model_id in models_to_test:
        try:
            model = get_agent_model("teaching_team", "teacher_agent", model_id)
            response = model.generate(prompt)
            results[model_id] = response
        except Exception as e:
            results[model_id] = f"Error: {e}"
    
    return results
```

## Agent 配置

在 `config/models.yaml` 中进行细粒度的Agent配置：

```yaml
agent_teams:
  teaching_team:
    teacher_agent:
      model_code: "qwen3_32b"  # 使用本地Ollama模型
    
    course_planner:
      model_code: "qwen3_32b"  # 使用本地Ollama模型
    
    content_designer:
      model_code: "gemini_flash"  # 需要GOOGLE_API_KEY
    
    content_verifier:
      model_code: "grok_beta"  # 需要XAI_API_KEY
```

## 支持的提供商

| 提供商 | 环境变量 | 说明 |
|--------|----------|------|
| OpenAI | `OPENAI_API_KEY` | GPT-4, GPT-3.5等 |
| xAI | `XAI_API_KEY` | Grok模型 |
| Gemini | `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` | Google的AI模型 |
| Anthropic | `ANTHROPIC_API_KEY` 或 `CLAUDE_API_KEY` | Claude模型 |
| Ollama | `OLLAMA_HOST` | 本地模型，默认无需API密钥 |

## 安全最佳实践

1. **环境文件安全**
   - 将 `.env` 添加到 `.gitignore`
   - 使用 `.env.example` 作为模板
   - 定期轮换API密钥

2. **敏感信息保护**
   - 系统自动过滤占位符值
   - 日志中不显示完整API密钥
   - 支持多种环境变量名称

3. **配置验证**
   - 启动时自动验证配置
   - 提供明确的错误信息
   - 支持部分配置的降级使用

## 故障排除

### 常见问题

1. **API密钥未生效**
   ```bash
   # 检查环境变量是否正确加载
   python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

2. **模型创建失败**
   ```bash
   # 运行诊断脚本
   python test_env_config.py
   ```

3. **配置文件路径错误**
   ```bash
   # 检查配置文件是否存在
   ls -la config/models.yaml
   ```

### 错误代码

- `ConfigNotFound`: 配置文件不存在
- `APIKeyMissing`: API密钥未设置
- `ModelProviderError`: 模型提供商配置错误

## 与 agno 框架的兼容性

本系统参考了 agno 框架的设计理念：

1. **统一的API密钥管理**: 支持多种提供商的统一配置
2. **环境特定配置**: 支持开发、测试、生产环境
3. **模型无关设计**: 与具体模型实现解耦
4. **最佳实践**: 安全、可维护、易扩展

## 更新日志

- **v1.0.0**: 初始版本，参考 agno 框架设计
- 支持 OpenAI、xAI、Gemini、Anthropic、Ollama
- 环境变量自动加载和验证
- 细粒度Agent配置支持 