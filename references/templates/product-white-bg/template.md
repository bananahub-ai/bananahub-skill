---
id: product-white-bg
type: prompt
title: 电商白底产品图
title_en: E-commerce Product on White
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: product
tags: [产品图, 电商, 白底, 商品, 淘宝]
models:
  - name: gemini-3.1-flash-image-preview
    tested: true
    quality: good
  - name: gemini-3-pro-image-preview
    tested: false
    quality: expected-best
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
  edit: true
  mask_edit: true
prompt_variants:
  default: base
  gemini: prompt-gemini
  gpt-image: prompt-gpt-image
aspect: "1:1"
difficulty: beginner
samples:
  - file: samples/sample-3.1-flash-01.png
    provider: google-ai-studio
    model: gemini-3.1-flash-image-preview
    prompt_variant: gemini
    prompt: "A photorealistic professional product photograph of a sleek wireless Bluetooth headphone in matte black finish. Front three-quarter hero angle showing the top and front of the product. Pure white background with a subtle soft shadow directly beneath the product for depth. Studio three-point softbox lighting setup with a soft diffused key light and gentle rim light to define edges. Sharp focus on the product texture and material finish, the product fills most of the frame. Commercial catalog photography style, isolated composition."
    aspect: "1:1"
created: 2026-03-24
updated: 2026-03-24
---

## 描述

生成电商平台标准白底产品图。干净的白色背景、专业的产品摄影灯光、清晰的产品细节，适合淘宝主图、亚马逊 listing、商品详情页。

## Prompt Template

```
A photorealistic professional product photograph of {{product|a sleek wireless Bluetooth headphone in matte black finish}}. {{angle|Front three-quarter hero angle showing the top and front of the product}}. {{background|Pure white background with a subtle soft shadow directly beneath the product for depth}}. {{lighting|Studio three-point softbox lighting setup with a soft diffused key light and gentle rim light to define edges}}. {{detail|Sharp focus on the product texture and material finish, the product fills most of the frame}}. Commercial catalog photography style, isolated composition.
```

## Prompt Template: gemini

```
A photorealistic professional catalog product photograph of {{product|a sleek wireless Bluetooth headphone in matte black finish}}. {{angle|Front three-quarter hero angle showing the top and front of the product}}. {{background|Pure white background with a subtle soft shadow directly beneath the product for depth}}. {{lighting|Studio three-point softbox lighting setup with a soft diffused key light and gentle rim light to define edges}}. {{detail|Sharp focus on the product texture and material finish, the product fills most of the frame}}. Preserve accurate material texture, clean edges, and natural shadows. Commercial catalog photography style, isolated composition.
```

## Prompt Template: gpt-image

```
Create a studio catalog product image of {{product|a sleek wireless Bluetooth headphone in matte black finish}} on a clean pure white background. Use {{angle|a front three-quarter hero angle showing the top and front of the product}} with {{lighting|soft three-point studio lighting, a diffused key light, subtle fill, and a gentle rim light}}. Keep the object isolated, centered, sharply focused, and large in frame with {{background|a small realistic contact shadow directly beneath it}}. Avoid lifestyle props, busy reflections, text artifacts, duplicated parts, or cropped edges.
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `product` | a sleek wireless Bluetooth headphone in matte black finish | 产品描述，包含材质和颜色。描述越具体越好 |
| `angle` | Front three-quarter hero angle showing the top and front of the product | 拍摄角度：front / side / top-down / 45-degree hero / eye-level |
| `background` | Pure white background with a subtle soft shadow directly beneath the product for depth | 背景设置，电商标准为纯白加柔和投影 |
| `lighting` | Studio three-point softbox lighting setup with a soft diffused key light and gentle rim light to define edges | 灯光方案，使用摄影专业术语 |
| `detail` | Sharp focus on the product texture and material finish, the product fills most of the frame | 细节表现重点和构图 |

## Usage Examples

**Basic**:
```
/bananahub use product-white-bg
```

**Custom product**:
```
/bananahub use product-white-bg 一瓶绿色玻璃瓶的精酿啤酒，带水珠
```

**Specific angle**:
```
/bananahub use product-white-bg 红色运动鞋，侧面视角，突出鞋底纹理
```

## Tips

- Pro model strongly recommended — better material rendering and text/logo clarity
- 1:1 ratio is the e-commerce standard (淘宝/Amazon main image); Amazon requires product to fill 85% of frame
- Keep descriptions focused on the product itself; avoid adding lifestyle context for catalog shots
- Use studio photography terminology: "softbox," "key light," "rim light," "fill light" for precise control
- "Soft shadow directly beneath" gives depth without distracting from the product
- Describe the product's key material explicitly (matte black plastic, brushed steel, frosted glass) for realism
- For products with text/logos, mention them explicitly so the model renders them
- Add "with water droplets" for beverages or "with steam" for hot products to add appeal
- Avoid "8K" or "ultra-detailed" quality tags — Gemini responds better to descriptive scene language
- GPT Image prompts should explicitly say what to avoid, especially props, duplicated parts, and cropped edges
