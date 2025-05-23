#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}启动 Quest Agent Verse 开发环境...${NC}"

# 检查端口是否被占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}警告：端口 $1 已被占用，可能会导致服务冲突${NC}"
    fi
}

check_port 8080
check_port 8000

# 在新的终端窗口中启动前端
echo -e "${GREEN}启动前端服务...${NC}"
osascript -e 'tell app "Terminal" to do script "cd \"'$PWD'\" && npm run dev"'

# 在新的终端窗口中启动后端
echo -e "${GREEN}启动后端服务...${NC}"
osascript -e 'tell app "Terminal" to do script "cd \"'$PWD'/backend\" && python -m uvicorn src.main:app --reload"'

echo -e "${GREEN}开发环境已启动!${NC}"
echo -e "前端：http://localhost:8080"
echo -e "后端：http://localhost:8000"
echo -e "API文档：http://localhost:8000/docs"
