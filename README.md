# Quest Agent Verse

Quest Agent Verse是一个基于AI Agents的智能教育平台，通过大模型驱动的教学规划、内容生成和互动学习，提供个性化学习体验。

## 项目结构

项目采用前后端分离架构：

```
quest-agent-verse/
├── src/                 # 前端代码
│   ├── components/      # React组件
│   ├── contexts/        # 上下文管理
│   ├── hooks/           # 自定义Hooks
│   ├── lib/             # 工具函数库
│   ├── pages/           # 页面组件
│   └── services/        # API服务
├── backend/             # 后端代码
│   ├── src/
│   │   ├── agents/      # 实现各类AI Agents
│   │   ├── api/         # FastAPI路由和端点
│   │   ├── services/    # 业务逻辑服务
│   │   └── utils/       # 工具函数
│   └── requirements.txt # 后端依赖
└── start_dev.sh         # 开发环境启动脚本
```

## Agents架构

系统由三个Agent团队组成：

1. **Teaching Team**：负责规划和执行教学任务
   - CoursePlanner：课程规划设计
   - ContentDesigner：内容设计生成
   - ContentVerifier：内容验证检查
   - Teacher：课程讲解与问答

2. **Learning Team**：辅助学习者进行学习
   - LearningCompanion：学习伙伴，提供个性化引导

3. **Monitor Team**：监测教学内容和学习效果
   - SessionAnalyst：学习会话分析
   - LearningProfiler：学习者画像分析

## 安装与启动

### 安装前端依赖

```bash
npm install
```

### 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 启动开发环境

使用提供的启动脚本可以同时启动前后端服务：

```bash
./start_dev.sh
```

或者分别启动：

#### 前端开发服务器

```bash
npm run dev
```

#### 后端开发服务器

```bash
cd backend
python -m uvicorn src.main:app --reload
```

服务启动后：
- 前端访问：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/00ad2dda-c534-4093-b15f-023a02fba78e) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/00ad2dda-c534-4093-b15f-023a02fba78e) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)
