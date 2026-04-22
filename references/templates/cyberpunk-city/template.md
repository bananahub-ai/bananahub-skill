---
id: cyberpunk-city
type: prompt
title: 赛博朋克城市夜景
title_en: Cyberpunk City Nightscape
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: photo
tags: [赛博朋克, 城市, 夜景, 科幻, neon]
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
aspect: "16:9"
difficulty: beginner
samples:
  - file: samples/sample-3.1-flash-01.png
    provider: google-ai-studio
    model: gemini-3.1-flash-image-preview
    prompt_variant: gemini
    prompt: "A photorealistic wide-angle shot of a cyberpunk city street at night. A rain-soaked narrow alley lined with storefronts, holographic advertisements floating above the shops and flickering neon signage in the distance. The scene is bathed in pink and cyan neon light reflecting off the wet pavement and puddles. Dense fog drifts through the alley with volumetric light rays piercing through from above, creating visible shafts of colored light. Captured with a 35mm wide-angle lens, deep focus keeping both the foreground puddles and distant buildings sharp. Cinematic composition with leading lines drawing the eye into the depth of the street."
    aspect: "16:9"
created: 2026-03-24
updated: 2026-03-24
---

## 描述

一键生成赛博朋克风格的城市夜景。霓虹灯光、雨水反射、未来感建筑，适合用作桌面壁纸、概念设定、社交媒体封面。

## Prompt Template

```
A photorealistic wide-angle shot of a cyberpunk city street at night. {{scene_detail|A rain-soaked narrow alley lined with storefronts, holographic advertisements floating above the shops and flickering neon signage in the distance}}. The scene is bathed in {{color_scheme|pink and cyan}} neon light reflecting off the wet pavement and puddles. {{atmosphere|Dense fog drifts through the alley with volumetric light rays piercing through from above, creating visible shafts of colored light}}. {{camera|Captured with a 35mm wide-angle lens, deep focus keeping both the foreground puddles and distant buildings sharp}}. Cinematic composition with leading lines drawing the eye into the depth of the street.
```

## Prompt Template: gemini

```
A photorealistic wide-angle shot of a cyberpunk city street at night. {{scene_detail|A rain-soaked narrow alley lined with storefronts, holographic advertisements floating above the shops and flickering neon signage in the distance}}. The scene is bathed in {{color_scheme|pink and cyan}} neon light reflecting off the wet pavement and puddles. {{atmosphere|Dense fog drifts through the alley with volumetric light rays piercing through from above, creating visible shafts of colored light}}. {{camera|Captured with a 35mm wide-angle lens, deep focus keeping both the foreground puddles and distant buildings sharp}}. Cinematic composition with leading lines drawing the eye into the depth of the street.
```

## Prompt Template: gpt-image

```
Create a cinematic cyberpunk city scene showing {{scene|a rainy neon alley at night}}. Use {{lighting|strong neon signs reflected on wet pavement}} and {{mood|moody futuristic atmosphere}} with {{details|dense urban depth, umbrellas, steam, and layered architecture}}. Keep the composition readable with one clear focal path. Avoid illegible sign text, random logos, cluttered foreground objects, distorted people, or overexposed neon bloom.
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `scene_detail` | A rain-soaked narrow alley lined with storefronts, holographic advertisements floating above the shops and flickering neon signage in the distance | 街道场景细节描述，用完整句子描述 |
| `color_scheme` | pink and cyan | 霓虹灯主色调，可换为 purple and gold / red and blue / green and orange |
| `atmosphere` | Dense fog drifts through the alley with volumetric light rays piercing through from above, creating visible shafts of colored light | 环境氛围效果，描述光线与空气的交互 |
| `camera` | Captured with a 35mm wide-angle lens, deep focus keeping both the foreground puddles and distant buildings sharp | 镜头语言（仅 photo profile 有效） |

## Usage Examples

**Basic** (use all defaults):
```
/bananahub use cyberpunk-city
```

**Custom scene**:
```
/bananahub use cyberpunk-city 东京新宿街头，紫色和金色霓虹
```
The user description replaces relevant variables while keeping the template structure.

**With flags**:
```
/bananahub use cyberpunk-city 上海外滩未来版 --model gemini-2.5-flash-image --aspect 9:16
```

## Tips

- Describe the scene as a narrative, not a keyword list — Gemini understands natural language better than comma-separated tags
- Adding "rain" or "wet pavement" significantly improves neon reflection quality through reflections
- Pro model renders neon light details and fog better; Flash is faster but less detailed
- 16:9 works best for wide city scenes; 9:16 for vertical building close-ups
- Try "aerial view" or "bird's eye" for a different perspective
- Adding specific city names (Tokyo, Hong Kong, Shanghai) gives culturally distinct architecture
- Include a human figure or character for narrative depth — e.g., "a lone figure in a hooded jacket walking away"
- Use "deep focus" instead of "shallow depth of field" for cityscapes to keep the full scene sharp
