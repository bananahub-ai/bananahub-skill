# Nano Banana Prompt Optimization Guide

本文档定义基础优化阶段的规则。增强优化规则请参见 `profiles/` 目录下的各 Profile 文件。

## 错误检测规则（基础优化阶段使用）

优化用户 prompt 时，检查并修正以下常见问题：

### 1. 关键词列表模式
**检测**: 逗号分隔的关键词堆砌，如 "cat, window, sunlight, cozy"
**修正**: 改写为自然语言叙述："A cat sitting by a window in warm sunlight, creating a cozy atmosphere"

### 2. SD/Midjourney 权重语法
**检测**: 括号权重如 `(detailed:1.5)`、`[negative]`、`{emphasis}`
**修正**: 移除所有权重语法。通过描述性语言表达强调。

### 3. 负面表述
**检测**: "no blur"、"without distortion"、"not ugly" 等否定式
**修正**: 正向重述："sharp focus"、"clean lines"、"beautiful"

### 4. 主体被埋没
**检测**: 主体出现在修饰语或场景描述之后
**修正**: 将主体移到提示词开头

### 5. 质量标签堆砌
**检测**: "masterpiece, best quality, ultra detailed, 8k, HDR" 等通用质量标签
**修正**: 删除。Nano Banana 不使用质量标签。描述实际想要的视觉效果。

### 6. 画面内文字过长
**检测**: 要求渲染的文字内容超过 25 字符
**处理**: 警告用户文字渲染短语效果最佳，建议拆分或缩短。

## 智能翻译规则

### 描述性文字 → 翻译为英语
用户对画面内容的描述，翻译为自然英语（非直译，重写为符合 Nano Banana 的表达）。

### 画面内文字 → 保留原文
用户想在图片中显示的文字，保留原始语言，用引号包裹。

**识别画面内文字的信号**：
- 引号包裹的内容：`"生日快乐"`
- "写着/印着/显示/标注/刻着" 后的内容
- 品牌名、标语、标签等明确要在画面中展示的文字

**示例**：
| 输入 | 翻译结果 |
|------|---------|
| 写着"春天来了"的横幅 | a banner with the text "春天来了" |
| T恤上印着"HELLO" | a T-shirt with "HELLO" printed on it |
| 一个红色的苹果 | a red apple |
| 咖啡杯上写着"Good Morning" | a coffee cup with "Good Morning" written on it |

## 结构化规则

1. **主体前置**: 确保图片主体在提示词开头
2. **触发前缀**: 添加 "Create an image of" 或其他合适的动作短语（Generate, Draw, Paint 等，根据内容选择）

## 意图识别关键词表

| Profile | 触发关键词 |
|---------|-----------|
| `photo` | 照片、写实、人像、肖像、风景、街拍、产品图、美食摄影、纪实、抓拍、摄影、真实感、photo、portrait、landscape |
| `illustration` | 插画、漫画、动漫、卡通、手绘、二次元、Q版、赛博朋克风、像素画、扁平化、矢量、水彩画、油画、素描、涂鸦、anime、manga、cartoon、pixel art、comic |
| `diagram` | 图表、流程图、架构图、信息图、示意图、思维导图、组织架构、时间线、对比图、数据可视化、diagram、flowchart、infographic、chart |
| `text-heavy` | Logo、海报、名片、菜单、标牌、横幅、封面、标题、字体设计、排版、招牌、广告、宣传、传单、poster、banner、logo、typography |
| `minimal` | 极简、留白、壁纸、背景图、纯色、简约、负空间、桌面壁纸、手机壁纸、抽象、纹理、minimal、wallpaper、abstract、texture |
| `general` | 无法匹配以上任何分类 |

**识别优先级**: 关键词直接匹配 > 语义推断 > 归入 general

## 宽高比推荐

| 场景 | 推荐比例 |
|------|---------|
| 人像 / 角色 | 3:4 或 9:16 |
| 风景 / 全景 | 16:9 或 3:2 |
| 正方形 / 社交媒体 | 1:1 |
| 产品 / 静物 | 1:1 或 4:3 |
| 电影感 | 16:9 |
| 手机壁纸 | 9:16 |
| 桌面壁纸 | 16:9 |

## 模型参考

### gemini-3-pro-image-preview (Nano Banana Pro)
- **适合**: 高质量、细节丰富、复杂场景、文字渲染
- **宽高比**: 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3
- **推荐**: 默认模型

### gemini-2.0-flash-preview-image-generation (Nano Banana Flash)
- **适合**: 快速生成、简单场景、快速迭代
- **宽高比**: 1:1, 16:9, 9:16, 4:3, 3:4
- **权衡**: 速度快但质量略低于 Pro
