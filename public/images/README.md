# 学习图片资源

这个文件夹包含用于互动学习页面的图片资源。

## 如何添加新图片

1. 将您的图片文件（支持 .png, .jpg, .jpeg, .gif, .svg, .webp 格式）放入此文件夹
2. 打开 `src/pages/InteractiveLearning.tsx` 文件
3. 在 `availableImages` 数组中添加新图片的路径，格式为：`'/images/您的图片文件名'`

例如：
```javascript
const availableImages = [
  '/images/chatgpt_image.png',
  '/images/learning_diagram.jpg',    // 新添加的图片
  '/images/concept_map.png',         // 另一张新图片
  '/placeholder.svg',
];
```

## 当前可用图片

- `chatgpt_image.png` - AI助手相关图片

## 图片切换功能

当有多张图片时，用户可以：
- 点击左右箭头按钮切换图片
- 查看底部的圆点指示器了解当前图片位置
- 点击顶部的向上/向下箭头折叠/展开图片面板
