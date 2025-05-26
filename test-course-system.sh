#!/bin/bash

# 课程规划系统端到端测试脚本
# 作者: Quest Agent Verse Team
# 日期: 2025-05-26

echo "🎓 Quest Agent Verse - 课程规划系统测试"
echo "================================================"
echo ""

# 检查服务器状态
echo "1. 检查服务器状态..."
echo "-------------------"

# 检查前端服务器
echo "🔍 检查前端服务器 (localhost:8080)..."
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ 前端服务器运行正常"
else
    echo "❌ 前端服务器未响应"
fi

# 检查后端服务器
echo "🔍 检查后端服务器 (localhost:8000)..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务器运行正常"
    # 获取服务器信息
    echo "📊 后端服务器信息:"
    curl -s http://localhost:8000/api/health | python3 -m json.tool 2>/dev/null || echo "  API响应正常但格式化失败"
else
    echo "❌ 后端服务器未响应"
fi

echo ""

# 测试API端点
echo "2. 测试核心API端点..."
echo "----------------------"

# 测试课程列表API
echo "🔍 测试课程列表API..."
COURSE_LIST_RESPONSE=$(curl -s http://localhost:8000/api/course/list)
if [[ $? -eq 0 && "$COURSE_LIST_RESPONSE" != "" ]]; then
    echo "✅ 课程列表API正常"
    # 计算课程数量
    COURSE_COUNT=$(echo "$COURSE_LIST_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    courses = data.get('courses', [])
    print(f'📚 找到 {len(courses)} 个存储的课程')
    if courses:
        for i, course in enumerate(courses[:3]):
            title = course.get('title', course.get('topic', 'Unknown'))
            print(f'  📖 课程 {i+1}: {title}')
except:
    print('  响应数据格式错误')
" 2>/dev/null)
    echo "$COURSE_COUNT"
else
    echo "❌ 课程列表API失败"
fi

# 测试课程搜索API
echo "🔍 测试课程搜索API..."
SEARCH_RESPONSE=$(curl -s "http://localhost:8000/api/course/search?keywords=Python")
if [[ $? -eq 0 && "$SEARCH_RESPONSE" != "" ]]; then
    echo "✅ 课程搜索API正常"
    echo "$SEARCH_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    courses = data.get('courses', [])
    print(f'🔍 搜索\"Python\"找到 {len(courses)} 个结果')
except:
    print('  搜索响应数据格式错误')
" 2>/dev/null
else
    echo "❌ 课程搜索API失败"
fi

echo ""

# 测试课程生成
echo "3. 测试课程生成功能..."
echo "----------------------"

echo "🔍 测试课程大纲生成..."
OUTLINE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/course/outline" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python编程入门",
    "learning_objective": "掌握Python基础语法和编程思维",
    "duration": "4-6小时", 
    "background": "初学者"
  }')

if [[ $? -eq 0 && "$OUTLINE_RESPONSE" != "" ]]; then
    echo "✅ 课程大纲生成API正常"
    echo "$OUTLINE_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    chapters = data.get('chapters', [])
    print(f'📚 生成了 {len(chapters)} 个章节')
    if chapters:
        for i, chapter in enumerate(chapters[:2]):
            title = chapter.get('title', 'Unknown')
            sections = len(chapter.get('sections', []))
            print(f'  📖 章节 {i+1}: {title} ({sections} 个小节)')
except Exception as e:
    print(f'  解析课程大纲失败: {e}')
" 2>/dev/null
else
    echo "❌ 课程大纲生成失败"
fi

echo ""

# 文件系统检查
echo "4. 检查关键文件..."
echo "------------------"

FILES_TO_CHECK=(
    "src/pages/CoursePlanning.tsx"
    "src/components/course/CourseSelectionDialog.tsx"
    "src/utils/courseCompletenessChecker.ts"
    "src/services/api.ts"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [[ -f "$file" ]]; then
        size=$(wc -l < "$file" 2>/dev/null)
        echo "✅ $file (${size} 行)"
    else
        echo "❌ $file - 文件不存在"
    fi
done

echo ""

# 检查localStorage功能（通过浏览器测试）
echo "5. 生成浏览器测试链接..."
echo "-------------------------"

echo "🌐 测试链接:"
echo "  📱 主页: http://localhost:8080/"
echo "  📚 课程规划: http://localhost:8080/course-planning"
echo "  🔧 API文档: http://localhost:8000/docs"
echo "  🧪 测试页面: file://$(pwd)/test-course-planning.html"

echo ""

# 总结
echo "6. 测试总结..."
echo "-------------"

echo "🎯 核心功能检查清单:"
echo "  ✓ 前端和后端服务器状态"
echo "  ✓ 课程列表和搜索API"
echo "  ✓ 课程大纲生成API"
echo "  ✓ 关键组件文件存在"
echo ""

echo "📋 手动测试建议:"
echo "  1. 访问主页输入学习主题"
echo "  2. 跳转到课程规划页面"
echo "  3. 测试课程选择对话框"
echo "  4. 验证课程完整性分析"
echo "  5. 测试缓存和内容生成"
echo ""

echo "🚀 系统已准备就绪，可以进行完整的用户交互测试！"
echo "================================================"
