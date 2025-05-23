# Quest Agent Verse

Quest Agent Verse 是一个由后端 AI Agents 集群驱动的真实实时互动学习系统。它通过大模型驱动的教学规划、动态内容生成、苏格拉底式互动教学以及学习效果分析，旨在提供高度个性化和引人入胜的学习体验。

## ✨ 特性

-   **AI Agent驱动**: 由多个专门的AI Agent协同工作，覆盖教学全流程。
-   **个性化课程规划**: `CoursePlanner` Agent 根据用户主题和学情生成定制化课程大纲。
-   **动态内容生成**: `ContentDesigner` Agent 为每个课程章节创建详细的多媒体教学内容。
-   **内容审查与迭代**: `ContentVerifier` Agent 负责审核教学内容的质量，并提供反馈进行优化。
-   **苏格拉底式互动教学**: `Teacher` Agent 以对话方式逐步引导学习，启发思考。
-   **学习伴侣**: `LearningCompanion` Agent 辅助教学，鼓励学习者参与。
-   **学习分析与反馈**: `Monitor Team` (包含 `SessionAnalyst` 和 `LearningProfiler`) 监测学习过程，分析学习效果，并提供优化建议。

## 项目结构

项目采用前后端分离架构：

```
quest-agent-verse/
├── backend/             # 后端代码 (Python, FastAPI, Agno)
│   ├── src/
│   │   ├── agents/      # 实现各类AI Agents (Teaching, Learning, Monitor Teams)
│   │   ├── api/         # FastAPI路由和API端点定义
│   │   ├── services/    # 后端核心业务逻辑服务 (如AgentService)
│   │   └── utils/       # 通用工具函数
│   ├── requirements.txt # 后端Python依赖
│   └── ...
├── src/                 # 前端代码 (React, Vite, TypeScript)
│   ├── components/      # UI组件
│   ├── contexts/        # React上下文管理
│   ├── hooks/           # 自定义React Hooks
│   ├── lib/             # 前端工具函数库
│   ├── pages/           # 应用页面级组件
│   └── services/        # 前端API服务对接
├── docs/                # 项目文档 (如prd.md)
├── start_dev.sh         # 开发环境一键启动脚本
└── README.md            # 本文档
```

## 🤖 后端 Agents 架构

后端系统由三个核心 Agent 团队组成，每个团队包含多个具有特定职责的 Agent：

### 1. Teaching Team (教学团队)
负责规划和执行教学任务。

-   **CoursePlanner (课程规划师)**: 接收用户学习主题、目标、时长和背景知识，生成结构化的课程大纲，包括章节划分、核心内容、学习目标、时长安排及课标对齐。
-   **ContentDesigner (内容设计师)**: 基于课程大纲，为每个章节设计详细的多媒体教学材料，包括情景故事、讲解文本、图片提示词、代码示例、练习题和互动环节。
-   **ContentVerifier (内容审核员)**: 审查 `CoursePlanner` 和 `ContentDesigner` 生成的内容，检查其与用户需求/学情的匹配度、准确性、完整性、课标对齐等，并提供评分和修改意见。
-   **Teacher (教师)**: 执行经验证的课程内容，以苏格拉底式对话与学习者互动，引导学习，解答疑问，并评估理解程度。

### 2. Learning Team (学习团队)
辅助学习者进行学习任务。

-   **LearningCompanion (学习伙伴)**: 作为课堂讨论的参与者，配合 `Teacher` 启发人类学习者思考，适时提供见解（不直接给答案），建立同伴关系，鼓励学习者主动输出。
-   **CodeCompanion (代码伙伴)**: *[暂不启用]* 未来版本中，将提供编程学习内容的专业辅助，如代码示例、调试帮助等。

### 3. Monitor Team (监控团队)
负责监测教学效果，形成评价与优化建议。

-   **SessionAnalyst (会话分析师)**: 实时监测和分析单次学习会话中的交互数据（问题准确率、参与度、反应速度），识别学习者困惑点，并向 `Teacher` 提供实时教学调整建议。
-   **LearningProfiler (学习档案分析师)**: 维护学习者的长期学习档案和知识图谱，整合多次会话数据，识别学习模式与趋势，生成综合评估报告，并提出个性化学习路径和课程优化建议。

## 🛠️ 技术栈

-   **前端**:
    -   [Vite](https://vitejs.dev/)
    -   [TypeScript](https://www.typescriptlang.org/)
    -   [React](https://reactjs.org/)
    -   [shadcn-ui](https://ui.shadcn.com/)
    -   [Tailwind CSS](https://tailwindcss.com/)
-   **后端**:
    -   [Python](https://www.python.org/downloads/) (3.8 或更高版本) 和 pip
    -   [FastAPI](https://fastapi.tiangolo.com/) (用于构建API)
    -   [Agno](https://deepwiki.com/agno-agi/agno) (AI Agent 开发框架)
    -   [Ollama](https://ollama.ai/) (用于本地运行大语言模型，如Qwen)

## 🚀 安装与启动

### 前提条件
-   [Node.js 和 npm](https://nodejs.org/) (建议使用 [nvm](https://github.com/nvm-sh/nvm#installing-and-updating) 安装)
-   [Python](https://www.python.org/downloads/) (3.8 或更高版本) 和 pip

### 步骤

1.  **克隆仓库**
    ```bash
    git clone <YOUR_GIT_URL>
    cd quest-agent-verse
    ```

2.  **安装前端依赖**
    ```bash
    # 进入项目根目录 (如果不在)
    npm install
    ```

3.  **安装后端依赖**
    ```bash
    cd backend
    # 建议创建并激活Python虚拟环境
    python -m venv venv
    # Linux/Mac:
    source venv/bin/activate
    # Windows:
    # venv\Scripts\activate
    pip install -r requirements.txt
    cd .. 
    ```

4.  **配置本地大语言模型 (Ollama)**
    -   确保你已经安装并运行了 [Ollama](https://ollama.ai/)。
    -   拉取 Agents 使用的模型 (例如 `qwen2:7b` 或 `qwen3:32b`，具体参照各 Agent 配置文件):
        ```bash
        ollama pull qwen2:7b 
        # ollama pull qwen3:32b
        ```
    -   确认 Ollama 服务正在运行 (通常在 `http://localhost:11434`)。

5.  **启动开发环境**

    项目提供了一个一键启动脚本，可以同时启动前后端服务：
    ```bash
    ./start_dev.sh
    ```
    该脚本通常会处理进入 `backend` 目录启动后端，然后在根目录启动前端。请检查脚本内容以确认其行为。

    或者，你可以分别启动前后端服务：

    *   **启动前端服务** (在项目根目录运行):
        ```bash
        npm run dev
        ```
        前端通常运行在 `http://localhost:3000`。

    *   **启动后端服务** (在 `backend` 目录运行):
        ```bash
        cd backend
        # 如果使用了虚拟环境，请确保已激活
        # source venv/bin/activate 
        python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        ```
        后端 API 通常运行在 `http://localhost:8000`，API文档 (Swagger UI) 可在 `http://localhost:8000/docs` 访问。

## 🤝 开发与贡献

### 使用你喜欢的IDE
1.  克隆仓库到本地。
2.  根据上述安装步骤设置好开发环境。
3.  使用你的IDE打开项目文件夹。
4.  进行代码修改，提交并推送你的更改。

### Agent 开发框架
本项目后端 Agent 使用 [Agno](https://deepwiki.com/agno-agi/agno) 框架开发。请查阅其官方文档以了解 Agent 的编程方法和最佳实践。

### 前后端通信
后端 Agents 与前端的通信，遵循 "AG-UI" 协议（具体细节请参照项目内部文档 `@agui_guidance.txt`）。

## 部署
(关于部署的说明可以根据实际情况添加，例如，如果使用特定平台如Lovable，或者有其他部署策略。)

---

*此 `README.md` 基于项目 `prd.md` 和原有信息整合而成。*
