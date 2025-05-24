#!/bin/bash

# 添加学习图片示例脚本
# 这个脚本会下载一些示例学习图片到 public/images 文件夹

echo "正在添加示例学习图片..."

# 创建 images 目录（如果不存在）
mkdir -p public/images

# 这里您可以添加您自己的图片文件
# 或者从网络下载一些开源的教育相关图片

echo "请手动将您的学习图片文件复制到 public/images/ 文件夹中"
echo "支持的格式: .png, .jpg, .jpeg, .gif, .svg, .webp"
echo ""
echo "然后编辑 src/pages/InteractiveLearning.tsx 文件中的 availableImages 数组："
echo "例如："
echo "  const availableImages = ["
echo "    '/images/chatgpt_image.png',"
echo "    '/images/您的图片1.jpg',"
echo "    '/images/您的图片2.png',"
echo "    '/placeholder.svg',"
echo "  ];"
echo ""
echo "完成后，图片切换功能将自动启用！"
