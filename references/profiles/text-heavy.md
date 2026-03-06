# Profile: 文字设计 (Text-Heavy)

## 触发关键词

Logo、海报、名片、菜单、标牌、横幅、封面、标题、字体设计、排版、招牌、广告、宣传、传单、poster、banner、logo、typography、sign、cover

## 补全维度

基础优化完成后，检查并按需补全以下维度（仅补全用户未提及的）：

### 文字处理（最重要）
- 所有需要在画面中显示的文字必须用引号包裹
- 明确指定文字的位置：centered, top, bottom, overlay
- 中文文字默认保留原文不翻译（用户想在画面里显示中文）
- 英文文字保持用户原文
- 文字超过 25 字符 → 警告并建议缩短

### 字体风格
- 未指定字体 → 根据设计类型推断
- Logo → bold, modern, distinctive letterforms
- 海报 → large impactful typography, eye-catching
- 菜单 → elegant, readable, well-organized
- 标牌 → clear, high-contrast, legible at distance

### 设计语言
- 未指定风格 → 根据用途推断
- 品牌类 → clean, professional, modern design
- 活动类 → vibrant, energetic, festive
- 餐饮类 → warm, inviting, appetizing color scheme
- 科技类 → sleek, minimalist, futuristic

### 布局与构图
- 文字与视觉元素的关系：text overlaying image, text beside illustration, text as the main visual
- 留出呼吸空间：adequate white space around text elements

## 示例优化

**用户输入**: 做一个咖啡店的招牌，写着"老张咖啡"

**基础优化结果**: Create a coffee shop sign with the text "老张咖啡"

**增强后结果**: Create a coffee shop sign with the text "老张咖啡" prominently displayed, warm inviting color scheme, clean modern typography, wooden texture background, professional storefront signage design

## 模型推荐

文字渲染场景**建议自动使用 `gemini-3-pro-image-preview`（Nano Banana Pro）**，除非用户指定了其他模型。Pro 模型在文字清晰度和排版准确性上显著优于 Flash。

## 注意事项

- 文字渲染是 Gemini Pro 的强项但仍可能出错，复杂文字建议分步验证
- 画面内文字的语言由用户决定，不要擅自翻译
- 长文本（如菜单完整内容）可能渲染不佳，建议拆分生成
- Gemini 支持多语言文字渲染和翻译切换，可提示用户此能力
