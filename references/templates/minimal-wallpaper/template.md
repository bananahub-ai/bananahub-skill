---
id: minimal-wallpaper
type: prompt
title: 极简手机壁纸
title_en: Minimal Phone Wallpaper
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: minimal
tags: [极简, 壁纸, 手机, 留白, 简约]
models:
  - name: gemini-3.1-flash-image-preview
    tested: true
    quality: good
  - name: gemini-3-pro-image-preview
    tested: false
    quality: expected-best
  - name: gemini-2.5-flash-image
    tested: false
    quality: unknown
providers:
  - id: google-ai-studio
    family: gemini-image
    models:
      - id: gemini-3-pro-image-preview
        aliases: [nano-banana-pro]
        quality: best
        prompt_variant: gemini
      - id: gemini-3.1-flash-image-preview
        aliases: [nano-banana-2]
        quality: good
        prompt_variant: gemini
  - id: openai
    family: gpt-image
    models:
      - id: gpt-image-2
        quality: untested
        prompt_variant: gpt-image
      - id: gpt-image-1
        quality: untested
        prompt_variant: gpt-image
capabilities:
  generation: true
  edit: false
  mask_edit: false
prompt_variants:
  default: base
  gemini: prompt-gemini
  gpt-image: prompt-gpt-image
aspect: "9:16"
difficulty: beginner
samples:
  - file: samples/sample-3.1-flash-01.png
    provider: google-ai-studio
    model: gemini-3.1-flash-image-preview
    prompt_variant: gemini
    prompt: "A minimalist phone wallpaper featuring a single small paper boat centered in the lower third of the frame with vast empty space above. Soft cream background with a muted blue accent on the subject. Clean vector illustration with subtle grain texture and crisp edges. Expansive negative space occupying most of the image, serene and contemplative mood."
    aspect: "9:16"
created: 2026-03-24
updated: 2026-03-24
---

## 描述

生成极简风格手机壁纸。大面积留白、单一主体、克制的配色，适合 iPhone/Android 锁屏和主屏壁纸。

## Prompt Template

```
A minimalist phone wallpaper featuring {{subject|a single small paper boat}} {{placement|centered in the lower third of the frame with vast empty space above}}. {{palette|Soft cream background with a muted blue accent on the subject}}. {{style|Clean vector illustration with subtle grain texture and crisp edges}}. Expansive negative space occupying most of the image, serene and contemplative mood.
```

## Prompt Template: gemini

```
A minimalist phone wallpaper featuring {{subject|a single small paper boat}} {{placement|centered in the lower third of the frame with vast empty space above}}. {{palette|Soft cream background with a muted blue accent on the subject}}. {{style|Clean vector illustration with subtle grain texture and crisp edges}}. Expansive negative space occupying most of the image, serene and contemplative mood.
```

## Prompt Template: gpt-image

```
Create a minimal phone wallpaper with {{subject|a single small paper boat}} {{placement|centered in the lower third with vast empty space above}}. Use {{palette|a soft cream background with one muted blue accent}} and {{style|clean vector shapes with subtle grain}}. Keep at least 75% negative space and leave safe empty areas for clock, notch, and dock. Avoid extra objects, text, detailed backgrounds, visual clutter, or centered busy compositions.
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `subject` | a single small paper boat | 主体物，保持简单，最好只有一个元素 |
| `placement` | centered in the lower third of the frame with vast empty space above | 主体位置，明确描述留白方向 |
| `palette` | Soft cream background with a muted blue accent on the subject | 配色方案，限制 2-3 色最佳 |
| `style` | Clean vector illustration with subtle grain texture and crisp edges | 渲染风格，指定边缘处理防止模糊 |

## Usage Examples

**Basic**:
```
/bananahub use minimal-wallpaper
```

**Custom subject**:
```
/bananahub use minimal-wallpaper 一棵孤独的树，秋天，橙色和米白配色
```

**Gradient style**:
```
/bananahub use minimal-wallpaper 日落渐变色，从深紫到淡橙，一只飞鸟剪影
```

**Abstract**:
```
/bananahub use minimal-wallpaper 几何线条，金色细线在深蓝背景上
```

## Tips

- Less is more — single subject with maximum negative space works best
- 9:16 ratio is standard for phone wallpapers; 16:9 for desktop
- Limit palette to 2-3 colors for true minimalism
- "Lower third" or "upper third" placement creates elegant asymmetry; avoid dead center
- Explicitly state how much negative space you want (e.g., "80% negative space") for stronger effect
- Both Pro and Flash models handle minimal styles well
- Ideal prompt length: 30-50 words; longer prompts add unwanted complexity and clutter
- Avoid detailed backgrounds — the emptiness IS the design
- For phone wallpapers, avoid placing elements where the clock, notch, or dock would cover them
- Don't rely on the word "minimalist" alone — pair it with concrete descriptions like "single subject," "vast empty space," "limited palette"
