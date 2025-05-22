# Quest Agent Verse - 后端

这是Quest Agent Verse项目的后端部分，负责实现各类AI Agents。

## 项目结构
```backend/
├── src/
│   ├── agents/         # 实现各类AI Agents
│   ├── api/            # FastAPI路由和端点
│   ├── services/       # 业务逻辑服务
│   └── utils/          # 工具函数
├── requirements.txt    # 依赖包
└── README.md           # 说明文档
```

## 安装
```bash
# 创建并激活虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt
```

## 运行
```bash
cd backend
python -m uvicorn src.main:app --reload
```

## Agents架构
后端主要由三个Agent Team组成：
1. Teaching Team：负责规划和执行教学任务
2. Learning Team：辅助学习者进行学习任务
3. Monitor Team：负责监测教学内容的规划与执行效果